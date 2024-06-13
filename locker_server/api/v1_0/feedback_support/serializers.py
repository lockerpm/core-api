from rest_framework import serializers


class FeedbackSupportReportSerializer(serializers.Serializer):
    task_name = serializers.CharField(allow_blank=True)
    priority = serializers.CharField(max_length=32, default="High")
    tag = serializers.CharField(max_length=32)
    images = serializers.ListSerializer(
        child=serializers.CharField(allow_blank=False), allow_empty=True, required=False
    )
    description = serializers.CharField(allow_blank=True)

