from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'nickname', 'name', 'phone', 'address', 'avatar', 'avatar_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_avatar_url(self, obj):
        """获取头像完整URL"""
        if obj.avatar:
            return obj.avatar.url
        return None
