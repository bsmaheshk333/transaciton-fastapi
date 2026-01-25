from rest_framework import serializers
from .models import WorkItemModel


class BulkWorkItemSerializer(serializers.ListSerializer):
    """
        this is required for bulk insert due to DRF is designed to for single object by default
        so bulk insert or update requires a separate behaviour (ListSerializer) for performance
        without bulk serializer, iteration requires and not ideal
    """
    def create(self, validated_data):
        items = [WorkItemModel(**item) for item in validated_data]
        return WorkItemModel.objects.bulk_create(items, ignore_conflicts=True)


class WorkItemSerializer(serializers.ModelSerializer):
    # config class for framework
    class Meta:
        model = WorkItemModel
        fields = "__all__"
        validators = [] #
        list_serializer_class = BulkWorkItemSerializer

    def create(self, validated_data):
        process_id = validated_data['process_id']
        workitem_id = validated_data['workitem_id']
        obj, created = WorkItemModel.objects.update_or_create(
            process_id=process_id,
            workitem_id=workitem_id,
            defaults={
                "comment": validated_data.get("comment"),
                "state": validated_data.get("state"),
                "status": validated_data.get("status"),
                "detail": validated_data.get("detail"),
                "exception_type": validated_data.get("exception_type")
            }
        )
        return obj

