import jwt
import time
from datetime import datetime, timedelta
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from .env_config import get_jwt_config


class TokenAuth:
    """
    简洁优美的Token鉴权系统
    支持openid编码/解码，可配置过期时间
    """
    
    @classmethod
    def _get_config(cls):
        """获取JWT配置"""
        return get_jwt_config()
    
    @classmethod
    def generate_token(cls, openid: str) -> str:
        """
        生成包含openid的token
        
        Args:
            openid: 用户的openid
            
        Returns:
            str: 生成的token字符串
        """
        try:
            # 获取配置
            config = cls._get_config()
            
            # 计算过期时间
            expire_time = datetime.utcnow() + timedelta(hours=config['expire_hours'])
            
            # 构造payload
            payload = {
                'openid': openid,
                'exp': expire_time,
                'iat': datetime.utcnow(),  # 签发时间
                'iss': 'zhihui_community'  # 签发者
            }
            
            # 生成token
            token = jwt.encode(payload, config['secret_key'], algorithm='HS256')
            return token
            
        except Exception as e:
            raise Exception(f"Token生成失败: {str(e)}")
    
    @classmethod
    def verify_token(cls, token: str) -> dict:
        """
        验证token并返回解码后的信息
        
        Args:
            token: 要验证的token字符串
            
        Returns:
            dict: 包含openid等信息的字典
            
        Raises:
            Exception: token无效或过期时抛出异常
        """
        try:
            # 获取配置
            config = cls._get_config()
            
            # 解码token
            payload = jwt.decode(token, config['secret_key'], algorithms=['HS256'])
            return payload
            
        except jwt.ExpiredSignatureError:
            raise Exception("Token已过期")
        except jwt.InvalidTokenError:
            raise Exception("Token无效")
        except Exception as e:
            raise Exception(f"Token验证失败: {str(e)}")
    
    @classmethod
    def get_openid_from_token(cls, token: str) -> str:
        """
        从token中获取openid
        
        Args:
            token: token字符串
            
        Returns:
            str: 解码出的openid
        """
        payload = cls.verify_token(token)
        return payload.get('openid')
    
    @classmethod
    def extract_token_from_request(cls, request) -> str:
        """
        从请求头中提取token
        
        Args:
            request: Django请求对象
            
        Returns:
            str: 提取的token字符串
            
        Raises:
            Exception: 未找到token时抛出异常
        """
        # 从Authorization头中获取token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            raise Exception("请求头中未找到Authorization")
        
        # 支持 "Bearer token" 和 "token" 两种格式
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header
            
        if not token:
            raise Exception("Token为空")
            
        return token


def require_auth(func):
    """
    装饰器：要求请求必须携带有效的token
    使用方法：在视图函数上加上 @require_auth 装饰器
    
    装饰后的函数会自动获得一个额外的参数 openid
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            # 提取token
            token = TokenAuth.extract_token_from_request(request)
            
            # 验证token并获取openid
            openid = TokenAuth.get_openid_from_token(token)
            
            # 将openid作为参数传递给原函数
            return func(request, openid=openid, *args, **kwargs)
            
        except Exception as e:
            return JsonResponse({
                'code': 401,
                'message': f'鉴权失败: {str(e)}',
                'data': None
            }, status=401)
    
    return wrapper


def optional_auth(func):
    """
    装饰器：可选的身份验证
    如果有token则验证，没有token也不会报错
    
    装饰后的函数会自动获得一个额外的参数 openid，如果未认证则为None
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            # 尝试提取token
            token = TokenAuth.extract_token_from_request(request)
            openid = TokenAuth.get_openid_from_token(token)
        except:
            # 如果获取失败，openid设为None
            openid = None
        
        # 将openid作为参数传递给原函数
        return func(request, openid=openid, *args, **kwargs)
    
    return wrapper


# 便捷函数，方便直接调用
def generate_token(openid: str) -> str:
    """生成token的便捷函数"""
    return TokenAuth.generate_token(openid)


def verify_token(token: str) -> dict:
    """验证token的便捷函数"""
    return TokenAuth.verify_token(token)


def get_openid_from_token(token: str) -> str:
    """从token获取openid的便捷函数"""
    return TokenAuth.get_openid_from_token(token)


def get_openid_from_request(request) -> str:
    """从请求中获取openid的便捷函数"""
    token = TokenAuth.extract_token_from_request(request)
    return TokenAuth.get_openid_from_token(token)