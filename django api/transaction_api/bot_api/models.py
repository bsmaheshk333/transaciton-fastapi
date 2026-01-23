from django.db import models


# Create your models here.
class WorkItemModel(models.Model):
    workitem_id = models.CharField(max_length=100, verbose_name="workitem id")
    comment = models.CharField(max_length=255)
    state = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    detail = models.JSONField() # bot specific payload
    exception_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.workitem_id

