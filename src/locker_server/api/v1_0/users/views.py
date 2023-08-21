from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError, AuthenticationFailed
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.user_pwd_permission import UserPwdPermission
from locker_server.core.exceptions.device_exception import DeviceDoesNotExistException
from locker_server.core.exceptions.user_exception import UserDoesNotExistException, \
    UserAuthBlockingEnterprisePolicyException, UserAuthFailedException, UserAuthBlockedEnterprisePolicyException, \
    UserIsLockedByEnterpriseException, UserEnterprisePlanExpiredException, UserBelongEnterpriseException, \
    User2FARequireException
from locker_server.shared.error_responses.error import refer_error, gen_error
from .serializers import UserMeSerializer, UserUpdateMeSerializer, UserRegisterSerializer, UserSessionSerializer, \
    DeviceFcmSerializer, UserChangePasswordSerializer


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
        elif self.action == "session":
            self.serializer_class = UserSessionSerializer
        elif self.action == "fcm_id":
            self.serializer_class = DeviceFcmSerializer
        elif self.action == "password":
            self.serializer_class = UserChangePasswordSerializer
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
        return Response(status=status.HTTP_200_OK, data={"success": True})

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
        return Response(status=status.HTTP_200_OK, data={
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
        return Response(status=status.HTTP_200_OK, data={"require_passwordless": require_passwordless})

    @action(methods=["get"], detail=False)
    def block_by_2fa_policy(self, request, *args, **kwargs):
        user = self.request.user
        is_factor2_param = self.request.query_params.get("is_factor2")
        if is_factor2_param and (is_factor2_param == "1" or is_factor2_param in [True, "true", "True"]):
            is_factor2 = True
        else:
            is_factor2 = False
        is_block = self.user_service.is_block_by_2fa_policy(user_id=user.user_id, is_factor2=is_factor2)
        return Response(status=status.HTTP_200_OK, data={"block": is_block})

    @action(methods=["get"], detail=False)
    def violation_me(self, request, *args, **kwargs):
        user = self.request.user
        failed_login = self.user_service.count_failed_login_event(user_id=user.user_id)
        return Response(status=status.HTTP_200_OK, data={"failed_login": failed_login})

    @action(methods=["get"], detail=False)
    def revision_date(self, request, *args, **kwargs):
        user = self.request.user
        self.check_pwd_session_auth(request=request)
        return Response(status=status.HTTP_200_OK, data={"revision_date": user.revision_date})

    @action(methods=["post"], detail=False)
    def session(self, request, *args, **kwargs):
        ip = self.get_ip()
        ua_string = self.get_client_agent()
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        client_id = validated_data.get("client_id")
        device_identifier = validated_data.get("device_identifier")
        device_name = validated_data.get("device_name")
        device_type = validated_data.get("device_type")
        password = validated_data.get("password")
        is_factor2 = request.data.get("is_factor2", False)

        try:
            result = self.user_service.user_session(
                user=user, password=password, client_id=client_id, device_identifier=device_identifier,
                device_name=device_name, device_type=device_type,
                is_factor2=is_factor2,
                token_auth_value=self.request.auth,
                secret=settings.SECRET_KEY,
                ip=ip,
                ua=ua_string
            )
            return Response(status=status.HTTP_200_OK, data=result)
        except UserAuthBlockingEnterprisePolicyException as e:
            error_detail = refer_error(gen_error("1008"))
            error_detail["wait"] = e.wait
            return Response(status=400, data=error_detail)
        except UserAuthBlockedEnterprisePolicyException as e:
            raise ValidationError(detail={
                "password": ["Password is not correct"],
                "failed_login_owner_email": e.failed_login_owner_email,
                "owner": e.owner,
                "lock_time": e.lock_time,
                "unlock_time": e.unlock_time,
                "ip": e.ip
            })
        except UserAuthFailedException:
            raise ValidationError(detail={"password": ["Password is not correct"]})
        except UserIsLockedByEnterpriseException:
            raise ValidationError({"non_field_errors": [gen_error("1009")]})
        except UserEnterprisePlanExpiredException:
            raise ValidationError({"non_field_errors": [gen_error("1010")]})
        except UserBelongEnterpriseException:
            raise ValidationError({"non_field_errors": [gen_error("1011")]})
        except User2FARequireException:
            raise ValidationError({"non_field_errors": [gen_error("1012")]})

    @action(methods=["post"], detail=False)
    def fcm_id(self, request, *args, **kwargs):
        # self.check_pwd_session_auth(request=request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        fcm_id = validated_data.get("fcm_id")
        device_identifier = validated_data.get("device_identifier")
        try:
            self.user_service.update_device_fcm_id(
                user=self.request.user, device_identifier=device_identifier, fcm_id=fcm_id
            )
        except DeviceDoesNotExistException:
            raise ValidationError(detail={"device_identifier": ["The device identifier does not exist"]})
        return Response(status=status.HTTP_200_OK, data={"success": True})

    @action(methods=["post"], detail=False)
    def password(self, request, *args, **kwargs):
        user = self.request.user
        ip = self.get_ip()
        # self.check_pwd_session_auth(request=request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        new_master_password_hash = validated_data.get("new_master_password_hash")
        new_master_password_hint = validated_data.get("new_master_password_hint", user.master_password_hint)
        key = validated_data.get("key")
        score = validated_data.get("score", user.master_password_score)
        login_method = validated_data.get("login_method", user.login_method)

        # Update the master password cipher
        master_password_cipher = request.data.get("master_password_cipher")


        master_pwd_item_obj = user.created_ciphers.filter(type=CIPHER_TYPE_MASTER_PASSWORD).first()

        if master_password_cipher:
            if not master_pwd_item_obj:
                # Create master password item
                self.serializer_class = VaultItemSerializer
                serializer = VaultItemSerializer(
                    data=master_password_cipher, **{"context": self.get_serializer_context()}
                )
                serializer.is_valid(raise_exception=True)
                team = serializer.validated_data.get("team")
                cipher_detail = serializer.save(**{"check_plan": False})
                cipher_detail.pop("team", None)
                cipher_detail = json.loads(json.dumps(cipher_detail))
                new_cipher = self.cipher_repository.save_new_cipher(cipher_data=cipher_detail)
                # Send sync message
                PwdSync(event=SYNC_EVENT_CIPHER_UPDATE, user_ids=[request.user.user_id], team=team, add_all=True).send(
                    data={"id": str(new_cipher.id)}
                )
            else:
                # Check permission
                self.serializer_class = UpdateVaultItemSerializer
                serializer = UpdateVaultItemSerializer(
                    data=master_password_cipher, **{"context": self.get_serializer_context()}
                )
                # serializer = self.get_serializer(data=master_password_cipher)
                serializer.is_valid(raise_exception=True)
                team = serializer.validated_data.get("team")
                cipher_detail = serializer.save(**{"cipher": master_pwd_item_obj})
                cipher_detail.pop("team", None)
                cipher_detail = json.loads(json.dumps(cipher_detail))
                master_password_cipher_obj = self.cipher_repository.save_update_cipher(
                    cipher=master_pwd_item_obj, cipher_data=cipher_detail
                )
                PwdSync(event=SYNC_EVENT_CIPHER_UPDATE, user_ids=[request.user.user_id], team=team, add_all=True).send(
                    data={"id": master_password_cipher_obj.id}
                )

        self.user_repository.change_master_password_hash(
            user=user, new_master_password_hash=new_master_password_hash, key=key, score=score,
            login_method=login_method, new_master_password_hint=new_master_password_hint
        )
        # Revoke all sessions
        exclude_sso_token_ids = None
        client = None
        if request.data.get("login_method"):
            decoded_token = self.decode_token(request.auth)
            sso_token_id = decoded_token.get("sso_token_id") if decoded_token else None
            exclude_sso_token_ids = [sso_token_id] if sso_token_id else None

            exclude_device_access_token = DeviceAccessToken.objects.filter(
                device__user=user, sso_token_id__in=exclude_sso_token_ids
            ).order_by('-id').first()
            client = exclude_device_access_token.device.client_id if exclude_device_access_token else None

        self.user_repository.revoke_all_sessions(user=user, exclude_sso_token_ids=exclude_sso_token_ids)
        mail_user_ids = NotificationSetting.get_user_mail(
            category_id=NOTIFY_CHANGE_MASTER_PASSWORD, user_ids=[user.user_id]
        )
        return Response(status=200, data={
            "notification": True if user.user_id in mail_user_ids else False,
            "client": client
        })