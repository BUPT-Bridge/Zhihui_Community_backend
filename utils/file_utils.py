import os
import uuid
import datetime


def generate_random_avatar_filename(instance, filename):
    """
    生成随机的头像文件名
    
    Args:
        instance: 模型实例
        filename: 原始文件名
        
    Returns:
        str: 新的文件路径
    """
    # 获取文件扩展名
    ext = filename.split('.')[-1] if '.' in filename else 'webp'
    
    # 生成随机文件名: uuid + 时间戳
    timestamp = int(datetime.datetime.now().timestamp())
    random_name = f"{uuid.uuid4().hex}_{timestamp}.{ext}"
    
    # 返回新的文件路径
    return os.path.join('avatars', random_name)
