from django.core.cache import cache
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.decorators import action

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.exclude_domain_pwd_permission import ExcludeDomainPwdPermission
from locker_server.api.permissions.locker_permissions.sync_pwd_permission import SyncPwdPermission
from locker_server.core.exceptions.cipher_exception import FolderDoesNotExistException, CipherDoesNotExistException
from locker_server.core.exceptions.collection_exception import CollectionDoesNotExistException
from locker_server.core.exceptions.exclude_domain_exception import ExcludeDomainNotExistException
from locker_server.shared.caching.sync_cache import SYNC_CACHE_TIMEOUT
from locker_server.shared.constants.account import LOGIN_METHOD_PASSWORDLESS
from locker_server.shared.constants.ciphers import CIPHER_TYPE_MASTER_PASSWORD
from locker_server.shared.constants.members import MEMBER_ROLE_MEMBER
from locker_server.shared.external_services.pm_sync import SYNC_EVENT_FOLDER_UPDATE, PwdSync, SYNC_EVENT_FOLDER_DELETE
from locker_server.shared.utils.app import camel_snake_data
from .serializers import SyncFolderSerializer, SyncCollectionSerializer, SyncEnterprisePolicySerializer


class SyncPwdViewSet(APIBaseViewSet):
    permission_classes = (SyncPwdPermission, )
    http_method_names = ["head", "options", "get"]

    def get_cipher_obj(self):
        try:
            cipher = self.cipher_service.get_by_id(cipher_id=self.kwargs.get("pk"))
            if cipher.team:
                self.check_object_permissions(request=self.request, obj=cipher)
            else:
                if cipher.user and cipher.user.user_id != self.request.user.user_id:
                    raise NotFound
            return cipher
        except CipherDoesNotExistException:
            raise NotFound

    def get_folder_obj(self):
        try:
            folder = self.folder_service.get_by_id(folder_id=self.kwargs.get("pk"))
            if folder.user.user_id != self.request.user.user_id:
                raise NotFound
            return folder
        except FolderDoesNotExistException:
            raise NotFound

    def get_collection_obj(self):
        user = self.request.user
        try:
            user_collections = self.collection_service.list_user_collections(user_id=user.user_id, exclude_team_ids=[])
            for collection in user_collections:
                if collection.collection_id == self.kwargs.get("pk"):
                    return collection
            raise NotFound
        except CollectionDoesNotExistException:
            raise NotFound

    @action(methods=["get"], detail=False)
    def sync(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)

        paging_param = self.request.query_params.get("paging", "0")
        page_size_param = self.check_int_param(self.request.query_params.get("size", 50))
        page_param = self.check_int_param(self.request.query_params.get("page", 1))

        # Get sync data from cache
        cache_key = self.user_service.get_sync_cache_key(user_id=user.user_id, page=page_param, size=page_size_param)
        response_cache_data = cache.get(cache_key)
        if response_cache_data:
            return Response(status=200, data=response_cache_data)

        policies = self.enterprise_service.list_policies_by_user(user_id=user)

        # Check team policies
        block_team_ids = []
        # for policy in policies:
        #     check_policy = self.team_repository.check_team_policy(request=request, team=policy.team)
        #     if check_policy is False:
        #         block_team_ids.append(policy.team_id)

        # Check the login method to exclude
        exclude_types = []
        if user.login_method == LOGIN_METHOD_PASSWORDLESS:
            exclude_types = [CIPHER_TYPE_MASTER_PASSWORD]

        ciphers = self.cipher_repository.get_multiple_by_user(
            user=user, exclude_team_ids=block_team_ids, exclude_types=exclude_types
        ).order_by('-revision_date').prefetch_related('collections_ciphers')
        total_cipher = ciphers.count()
        not_deleted_ciphers = ciphers.filter(deleted_date__isnull=True)
        not_deleted_ciphers_statistic = not_deleted_ciphers.values('type').annotate(
            count=Count('type')
        ).order_by('-count')
        not_deleted_ciphers_count = {item["type"]: item["count"] for item in list(not_deleted_ciphers_statistic)}
        # ciphers_page = self.paginate_queryset(ciphers)
        if paging_param == "0":
            ciphers_page = ciphers
        else:
            try:
                paginator = Paginator(list(ciphers), page_size_param or 50)
                ciphers_page = paginator.page(page_param).object_list
            except EmptyPage:
                ciphers_page = []

        ciphers_serializer = SyncCipherSerializer(ciphers_page, many=True, context={"user": user})

        folders = self.folder_repository.get_multiple_by_user(user=user)
        collections = self.collection_repository.get_multiple_user_collections(
            user=user, exclude_team_ids=block_team_ids
        ).select_related('team')

        sync_data = {
            "object": "sync",
            "count": {
                "ciphers": total_cipher,
                "not_deleted_ciphers": {
                    "total": not_deleted_ciphers.count(),
                    "ciphers": not_deleted_ciphers_count
                },
            },
            "profile": SyncProfileSerializer(user, many=False).data,
            "ciphers": ciphers_serializer.data,
            "collections": SyncCollectionSerializer(collections, many=True, context={"user": user}).data,
            "folders": SyncFolderSerializer(folders, many=True).data,
            "domains": None,
            "policies": SyncEnterprisePolicySerializer(policies, many=True).data,
            "sends": []
        }
        sync_data = camel_snake_data(sync_data, snake_to_camel=True)
        cache.set(cache_key, sync_data, SYNC_CACHE_TIMEOUT)
        return Response(status=200, data=sync_data)

    @action(methods=["get"], detail=False)
    def sync_count(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        # Check team policies
        block_team_ids = []
        # Check the login method to exclude
        exclude_types = []
        if user.login_method == LOGIN_METHOD_PASSWORDLESS:
            exclude_types = [CIPHER_TYPE_MASTER_PASSWORD]

        ciphers = self.cipher_repository.get_multiple_by_user(
            user=user, exclude_team_ids=block_team_ids, exclude_types=exclude_types
        ).order_by('-revision_date')
        total_cipher = ciphers.count()
        not_deleted_ciphers = ciphers.filter(deleted_date__isnull=True)
        not_deleted_ciphers_statistic = not_deleted_ciphers.values('type').annotate(
            count=Count('type')
        ).order_by('-count')
        not_deleted_ciphers_count = {item["type"]: item["count"] for item in list(not_deleted_ciphers_statistic)}
        total_folders = self.folder_repository.get_multiple_by_user(user=user).count()
        total_collections = self.collection_repository.get_multiple_user_collections(
            user=user, exclude_team_ids=block_team_ids
        ).count()

        sync_count_data = {
            "object": "sync_count",
            "count": {
                "ciphers": total_cipher,
                "not_deleted_ciphers": {
                    "total": not_deleted_ciphers.count(),
                    "ciphers": not_deleted_ciphers_count
                },
                "folders": total_folders,
                "collections": total_collections
            }
        }
        sync_count_data = camel_snake_data(sync_count_data, snake_to_camel=True)
        return Response(status=200, data=sync_count_data)

    @action(methods=["get"], detail=False)
    def sync_cipher_detail(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        cipher = self.get_cipher_obj()
        cipher_obj = self.cipher_repository.get_multiple_by_user(
            user=user, filter_ids=[cipher.id]
        ).prefetch_related('collections_ciphers').first()
        serializer = SyncCipherSerializer(cipher_obj, context={"user": user}, many=False)
        result = camel_snake_data(serializer.data, snake_to_camel=True)
        return Response(status=200, data=result)

    @action(methods=["get"], detail=False)
    def sync_folder_detail(self, request, *args, **kwargs):
        self.check_pwd_session_auth(request=request)
        folder = self.get_folder_obj()
        serializer = SyncFolderSerializer(folder, many=False)
        result = camel_snake_data(serializer.data, snake_to_camel=True)
        return Response(status=200, data=result)

    @action(methods=["get"], detail=False)
    def sync_collection_detail(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        collection = self.get_collection_obj()
        serializer = SyncCollectionSerializer(collection, many=False, context={"user": user})
        serializer_data = serializer.data
        role_id = self.team_member_service.get_role_notify(
            user_id=user.user_id, team_id=collection.team.team_id
        ).get("role")
        serializer_data["read_only"] = True if role_id == MEMBER_ROLE_MEMBER else False
        result = camel_snake_data(serializer_data, snake_to_camel=True)
        return Response(status=200, data=result)

    @action(methods=["get"], detail=False)
    def sync_profile_detail(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        serializer = SyncProfileSerializer(user, many=False)
        result = camel_snake_data(serializer.data, snake_to_camel=True)
        return Response(status=200, data=result)

    @action(methods=["get"], detail=False)
    def sync_org_detail(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        try:
            team_member = user.team_members.get(team_id=kwargs.get("pk"), team__key__isnull=False)
        except ObjectDoesNotExist:
            raise NotFound

        serializer = SyncOrgDetailSerializer(team_member, many=False)
        result = camel_snake_data(serializer.data, snake_to_camel=True)
        return Response(status=200, data=result)
