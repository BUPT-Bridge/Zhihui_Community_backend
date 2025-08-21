from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from .models import User
from utils import generate_token
from utils.env_config import get_wx_config


class WxLoginView(APIView):
    """
    微信小程序登录接口
    
    POST /api/wx-login/
    
    请求参数:
    {
        "code": "微信登录凭证code"
    }
    
    返回:
    {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": "生成的JWT token",
            "user_info": {
                "openid": "用户openid",
                "nickname": "用户昵称",
                "avatar": "头像URL",
                "is_new_user": true/false
            }
        }
    }
    """
    
    # 微信API接口
    WX_API_URL = "https://api.weixin.qq.com/sns/jscode2session"
    
    def post(self, request):
        """处理POST请求 - 微信登录"""
        try:
            # 获取请求参数
            code = request.data.get('code')
            
            if not code:
                return self._error_response(
                    code=400,
                    message='缺少必要参数code',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # 从微信服务器获取openid
            openid = self._get_openid_from_wx(code)
            
            if not openid:
                return self._error_response(
                    code=400,
                    message='微信登录失败，无法获取用户信息',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # 获取或创建用户
            user, is_new_user = self._get_or_create_user(openid)
            
            # 生成token
            token = generate_token(openid)
            
            # 构造返回数据
            user_info = self._format_user_info(user, is_new_user)
            
            return self._success_response(
                message='登录成功',
                data={
                    'token': token,
                    'user_info': user_info
                }
            )
            
        except Exception as e:
            return self._error_response(
                code=500,
                message=f'服务器内部错误: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_openid_from_wx(self, code):
        """
        通过微信code获取用户openid (私有方法)
        
        Args:
            code: 微信小程序登录凭证
            
        Returns:
            str: 用户的openid，失败时返回None
        """
        # 获取微信配置
        wx_config = get_wx_config()
        
        params = {
            'appid': wx_config['appid'],
            'secret': wx_config['secret'],
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            # 请求微信API
            response = requests.get(self.WX_API_URL, params=params, timeout=10)
            result = response.json()
            
            # 检查是否有错误
            if 'errcode' in result:
                print(f"微信API错误: {result.get('errmsg', '未知错误')}")
                return None
            
            # 返回openid
            return result.get('openid')
            
        except requests.RequestException as e:
            print(f"请求微信API失败: {str(e)}")
            return None
        except Exception as e:
            print(f"解析微信API响应失败: {str(e)}")
            return None
    
    def _get_or_create_user(self, openid):
        """
        获取或创建用户 (私有方法)
        
        Args:
            openid: 用户的微信openid
            
        Returns:
            tuple: (User对象, 是否为新用户)
        """
        try:
            user = User.objects.get(openid=openid)
            return user, False
        except User.DoesNotExist:
            # 用户不存在，创建新用户
            user = User.objects.create(
                openid=openid,
                nickname=f"用户{openid[-6:]}",  # 使用openid后6位作为默认昵称
            )
            return user, True
    
    def _format_user_info(self, user, is_new_user):
        """
        格式化用户信息 (私有方法)
        
        Args:
            user: User对象
            is_new_user: 是否为新用户
            
        Returns:
            dict: 格式化后的用户信息
        """
        return {
            'openid': user.openid,
            'nickname': user.nickname,
            'name': user.name,
            'phone': user.phone,
            'avatar': user.avatar.url if user.avatar else None,
            'is_new_user': is_new_user
        }
    
    def _success_response(self, message='操作成功', data=None):
        """
        统一成功响应格式 (私有方法)
        
        Args:
            message: 响应消息
            data: 响应数据
            
        Returns:
            Response: DRF Response对象
        """
        return Response({
            'code': 200,
            'message': message,
            'data': data
        }, status=status.HTTP_200_OK)
    
    def _error_response(self, code, message, status_code=None):
        """
        统一错误响应格式 (私有方法)
        
        Args:
            code: 错误代码
            message: 错误消息
            status_code: HTTP状态码
            
        Returns:
            Response: DRF Response对象
        """
        if status_code is None:
            status_code = status.HTTP_400_BAD_REQUEST
            
        return Response({
            'code': code,
            'message': message,
            'data': None
        }, status=status_code)


from utils.auth import get_openid_from_token
from .serializers import UserSerializer


class UserProfileView(APIView):
    """
    用户信息相关接口
    
    GET /api/user/profile/ - 获取用户信息
    PUT /api/user/profile/ - 更新用户信息
    """
    
    def get(self, request):
        """获取用户信息 - 需要token验证"""
        try:
            # 获取token
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header:
                return self._error_response(401, '未提供授权信息')
            
            # 提取token
            token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
            
            # 验证token并获取openid
            try:
                openid = get_openid_from_token(token)
            except Exception as e:
                return self._error_response(401, f'无效的token: {str(e)}')
            
            # 获取用户
            try:
                user = User.objects.get(openid=openid)
            except User.DoesNotExist:
                return self._error_response(404, '用户不存在')
            
            # 序列化返回数据
            serializer = UserSerializer(user)
            
            return self._success_response('获取用户信息成功', serializer.data)
        
        except Exception as e:
            return self._error_response(500, f'服务器内部错误: {str(e)}')
    
    def put(self, request):
        """
        更新用户信息
        
        可更新字段:
        - nickname: 昵称
        - name: 姓名
        - phone: 手机号
        - address: 地址
        - avatar: 头像文件
        """
        try:
            # 获取token
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header:
                return self._error_response(401, '未提供授权信息')
            
            # 提取token
            token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
            
            # 验证token并获取openid
            try:
                openid = get_openid_from_token(token)
            except Exception as e:
                return self._error_response(401, f'无效的token: {str(e)}')
            
            # 获取用户
            try:
                user = User.objects.get(openid=openid)
            except User.DoesNotExist:
                return self._error_response(404, '用户不存在')
            
            # 只更新请求中存在的字段
            allowed_fields = ['nickname', 'name', 'phone', 'address', 'avatar']
            update_data = {}
            
            for field in allowed_fields:
                if field in request.data:
                    update_data[field] = request.data[field]
            
            # 验证昵称长度
            if 'nickname' in update_data and len(update_data['nickname']) > 50:
                return self._error_response(400, '昵称长度不能超过50个字符')
            
            # 更新用户数据
            for field, value in update_data.items():
                setattr(user, field, value)
            
            # 保存
            user.save()
            
            # 序列化返回更新后的用户信息
            serializer = UserSerializer(user)
            
            return self._success_response('更新用户信息成功', serializer.data)
        
        except Exception as e:
            return self._error_response(500, f'服务器内部错误: {str(e)}')
    
    def _success_response(self, message='操作成功', data=None):
        """统一成功响应格式"""
        return Response({
            'code': 200,
            'message': message,
            'data': data
        }, status=status.HTTP_200_OK)
    
    def _error_response(self, code, message, status_code=None):
        """统一错误响应格式"""
        if status_code is None:
            status_code = code
            
        return Response({
            'code': code,
            'message': message,
            'data': None
        }, status=status_code)


# 保留原来的函数式视图作为备用
def wx_login_function_view(request):
    """函数式视图版本的微信登录（备用）"""
    # 原来的函数式视图代码...
    pass
