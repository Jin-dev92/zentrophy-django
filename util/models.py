from django.db import models


class TimeStampModel(models.Model):
    is_created = models.DateTimeField(auto_now_add=True)  # 처음에 추가될때 생성된다.
    is_updated = models.DateTimeField(auto_now=True)  # 처음 추가 될때 생성이 되면서 데이터가 바뀔때 마다 같이 바뀌게된다.

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    class Meta:
        abstract = True
