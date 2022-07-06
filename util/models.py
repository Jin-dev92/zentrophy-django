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


# class ImageModel(models.Model):
#     origin_image = ImageField(upload_to="image/%Y/%m/%d", null=True)
#
#     def image_tag(self):
#         from django.utils.html import escape
#         return u'<img src="%s" />' % escape(self.origin_image)
#
#     image_tag.short_description = 'Image'
#     image_tag.allow_tags = True
#
#
# class FileModel(models.Model):
#     file = models.FileField(upload_to="file/%Y/%m/%d", null=True)

    # def auto_delete_file_on_delete(self):
    #     if self.file:
    #         if os.path.isfile(self.file.path):  # 해당 경로에 파일이 있다면
    #             os.remove(self.file.path)
    #
    # def auto_delete_file_on_change(self):
    #     try:
    #         obj = FileModel.objects.get(id=self.id)
    #     except FileModel.DoesNotExist:
    #         return
    #
    #     if obj.file and self.file and obj.file != self.file:
    #         obj.file.delete()
