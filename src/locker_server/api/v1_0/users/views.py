from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError, AuthenticationFailed
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.user_pwd_permission import UserPwdPermission
from locker_server.core.exceptions.user_exception import UserDoesNotExistException
from .serializers import UserMeSerializer, UserUpdateMeSerializer, UserRegisterSerializer


class UserPwdViewSet(APIBaseViewSet):
    permission_classes = (UserPwdPermission,)
    http_method_names = ["options", "head", "get", "post", "put", "delete"]
    lookup_value_regex = r'[0-9a-z-]+'

    def get_throttles(self):
        return super().get_throttles()

    def get_serializer_class(self):
        if self.action == "me":
            if self.request.method == "GET":
                self.serializer_class = UserMeSerializer
            else:
                self.serializer_class = UserUpdateMeSerializer
        elif self.action == "register":
            self.serializer_class = UserRegisterSerializer
        return super().get_serializer_class()

    @action(methods=["post"], detail=False)
    def register(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        key = validated_data.get("key")
        keys = validated_data.get("keys", {})
        master_password_hash = validated_data.get("master_password_hash")
        self.user_service.register_user(
            user_id=user.user_id,
            master_password_hash=master_password_hash,
            key=key,
            keys=keys,
            **{
                "kdf": validated_data.get("kdf", 0),
                "kdf_iterations": validated_data.get("kdf_iterations", 100000),
                "master_password_hint": validated_data.get("master_password_hint", ""),
                "score": validated_data.get("score", 0),
                "trial_plan": validated_data.get("trial_plan"),
                "is_trial_promotion": validated_data.get("is_trial_promotion"),
                "enterprise_name": validated_data.get("enterprise_name")
            }
        )
        return Response(status=200, data={"success": True})

    @action(methods=["get"], detail=False)
    def invitation_confirmation(self, request, *args, **kwargs):
        email = self.request.query_params.get("email", None)
        user_id = self.request.query_params.get("user_id", None)
        if (email is None) or (user_id is None):
            raise NotFound
        self.user_service.invitation_confirmation(user_id=user_id, email=email)
        return Response(status=200, data={"success": True})

    @action(methods=["get", "put"], detail=False)
    def me(self, request, *args, **kwargs):
        user = self.request.user

        if request.method == "GET":
            serializer = self.get_serializer(user, many=False)
            me_data = serializer.data
            pm_current_plan = self.user_service.get_current_plan(user=user)
            user_type = self.user_service.get_user_type(user=user)
            block_by_source = self.user_service.is_blocked_by_source(
                user=user, utm_source=self.request.query_params.get("utm_source")
            )
            me_data.update({
                "block_by_source": block_by_source,
                "pwd_user_type": user_type,
                "pwd_plan": pm_current_plan.pm_plan.alias,
            })
            return Response(status=status.HTTP_200_OK, data=me_data)

        elif request.method == "PUT":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data
            try:
                self.user_service.update_user(user_id=user.user_id, user_update_data=validated_data)
            except UserDoesNotExistException:
                raise AuthenticationFailed
            return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["get"], detail=False)
    def login_method_me(self, request, *args, **kwargs):
        user = self.request.user
        login_method = user.login_method
        require_passwordless = self.user_service.is_require_passwordless(user_id=user.user_id)
        return Response(status=200, data={
            "set_up_passwordless": True if user.fd_credential_id else False,
            "login_method": login_method,
            "require_passwordless": require_passwordless
        })

    @action(methods=["get"], detail=False)
    def passwordless_require(self, request, *args, **kwargs):
        user = self.request.user
        require_passwordless = self.user_service.is_require_passwordless(
            user_id=user.user_id, require_enterprise_member_status=None
        )
        return Response(status=200, data={"require_passwordless": require_passwordless})

    @action(methods=["get"], detail=False)
    def block_by_2fa_policy(self, request, *args, **kwargs):
        user = self.request.user
        is_factor2_param = self.request.query_params.get("is_factor2")
        if is_factor2_param and (is_factor2_param == "1" or is_factor2_param in [True, "true", "True"]):
            is_factor2 = True
        else:
            is_factor2 = False

        if is_factor2 is False:
            user_enterprises = Enterprise.objects.filter(
                enterprise_members__user=user, enterprise_members__status=E_MEMBER_STATUS_CONFIRMED
            )
            for enterprise in user_enterprises:
                policy = enterprise.policies.filter(policy_type=POLICY_TYPE_2FA, enabled=True).first()
                if not policy:
                    continue
                try:
                    member_role = enterprise.enterprise_members.get(user=user).role_id
                except ObjectDoesNotExist:
                    continue
                only_admin = policy.policy_2fa.only_admin
                if only_admin is False or \
                        (only_admin and member_role in [E_MEMBER_ROLE_ADMIN, E_MEMBER_ROLE_PRIMARY_ADMIN]):
                    return Response(status=200, data={"block": True})
        return Response(status=200, data={"block": False})

    @action(methods=["get"], detail=False)
    def violation_me(self, request, *args, **kwargs):
        user = self.request.user
        start_ts, end_ts = start_end_month_current()
        failed_login = Event.objects.filter(
            type=EVENT_USER_BLOCK_LOGIN, user_id=user.user_id,
            creation_date__gte=start_ts, creation_date__lte=end_ts
        ).count()
        return Response(status=200, data={"failed_login": failed_login})


    @action(methods=["get"], detail=False)
    def revision_date(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        return Response(status=status.HTTP_200_OK, data={"revision_date": user.revision_date})



