from django.db import models


# Create your models here.
class WorkItemModel(models.Model):
    workitem_id = models.CharField(max_length=100)
    process_id = models.CharField(max_length=100)
    comment = models.CharField(max_length=255)
    state = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    detail = models.JSONField() # bot specific payload
    exception_type = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['process_id', "workitem_id"],
                name="unique_workitem_per_process"
            )
        ]
    def __str__(self):

        return self.workitem_id

