from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from locker_server.api.api_base_view import APIBaseViewSet
from locker_server.api.permissions.locker_permissions.feedback_support_pwd_permission import \
    FeedbackSupportPwdPermission
from locker_server.shared.external_services.notion.notion import notion_customer_success
from .serializers import FeedbackSupportReportSerializer


class FeedbackSupportPwdViewSet(APIBaseViewSet):
    permission_classes = (FeedbackSupportPwdPermission, )
    http_method_names = ["head", "options", "post"]

    def get_serializer_class(self):
        if self.action == "report":
            self.serializer_class = FeedbackSupportReportSerializer
        return super().get_serializer_class()

    @action(methods=["post"], detail=False)
    def report(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        validated_data = serializer.validated_data
        icon = {"type": "external", "external": {"url": "https://www.notion.so/icons/clipping_lightgray.svg"}}
        task_name = validated_data.get("task_name", "")
        task_status = "Not started"
        priority = validated_data.get("priority", "High")
        description = validated_data.get("description", "")
        tag = validated_data.get("tag")
        images = validated_data.get("images", [])
        files = [
            {"name": "File name", "type": "external", "external": {"url": image}} for image in images
        ]
        properties = {
            "Task name": {"title": [{"type": "text", "text": {"content": task_name}}]},
            "Project Summary": {"type": "rich_text", "rich_text": [{"type": "text", "text": {"content": description}}]},
            "Status": {"status": {"id": "not-started", "name": task_status}},
            "Reporter": {"type": "people", "people": []},
            "Due Date": {"type": "date", "date": {"start": "2024-05-27", "end": None, "time_zone": None}},
            "Priority": {"type": "select", "select": {"name": priority}},
            "Tags": {"type": "multi_select", "multi_select": [{"name": tag}]},
            "Image": {"type": "files", "files": files},
        }
        notion_customer_success.create_page(
            parent={"database_id": settings.NOTION_CUSTOMER_SUCCESS_DATABASE},
            properties=properties,
            icon=icon
        )
        return Response(status=status.HTTP_200_OK, data={"success": True})
