from django.db import models
from django.utils import timezone


class TimeStampModel(models.Model):
    is_created = models.DateTimeField(auto_now_add=True)  # 처음에 추가될때 생성된다.
    is_updated = models.DateTimeField(auto_now=True)  # 처음 추가 될때 생성이 되면서 데이터가 바뀔때 마다 같이 바뀌게된다.

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    use_for_related_fields = True  # 옵션은 기본 매니저로 이 매니저를 정의한 모델이 있을 때 이 모델을 가리키는 모든 관계 참조에서 모델 매니저를 사용할 수 있도록 한다.

    def get_queryset(self, **kwargs):
        return super().get_queryset().filter(deleted_at__isnull=True, **kwargs)


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField('삭제일', null=True, default=None)

    class Meta:
        abstract = True  # 상속 할수 있게

    objects = SoftDeleteManager()  # 커스텀 매니저

    def soft_delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):  # 삭제된 레코드를 복구한다.
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])


class FileExistModel():
    class Meta:
        proxy = True  # 상속 할수 있게

    # @receiver(pre_delete)
    # def delete_receiver(self, sender, instance, **kwargs):
    #
    #     ...