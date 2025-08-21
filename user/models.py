from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class User(models.Model):
    """用户模型"""
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name="昵称")
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="姓名")
    phone = models.CharField(max_length=11, unique=True, blank=True, null=True, verbose_name="手机号")
    address = models.TextField(blank=True, null=True, verbose_name="住址")
    openid = models.CharField(max_length=64, unique=True, blank=True, null=True, verbose_name="微信小程序OpenID")
    avatar = ProcessedImageField(
        upload_to='avatars/',
        processors=[ResizeToFill(120, 120)],
        format='WEBP',
        options={'quality': 85},
        blank=True,
        null=True,
        verbose_name="头像"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
        db_table = "user"

    def __str__(self):
        return f"{self.nickname} ({self.name})"
