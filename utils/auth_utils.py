"""
API鉴权工具
使用RSA公私钥进行请求鉴权
"""
import os
import base64
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


class AuthUtils:
    """API鉴权工具类"""
    
    def __init__(self):
        # 加载公钥
        public_key_path = os.path.join(os.path.dirname(__file__), 'api_keys.pub')
        with open(public_key_path, 'r') as f:
            self.public_key = serialization.load_ssh_public_key(f.read().encode())
    
    def verify_signature(self, data, signature):
        """
        验证签名
        
        Args:
            data: 原始数据字符串
            signature: base64编码的签名
            
        Returns:
            bool: 验证是否成功
        """
        try:
            # 解码签名
            signature_bytes = base64.b64decode(signature)
            
            # 验证签名
            self.public_key.verify(
                signature_bytes,
                data.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False
    
    def generate_auth_headers(self, data, private_key_path):
        """
        生成认证头（用于客户端测试）
        
        Args:
            data: 要签名的数据
            private_key_path: 私钥路径
            
        Returns:
            dict: 包含认证头的字典
        """
        # 加载私钥
        with open(private_key_path, 'rb') as f:
            private_key = serialization.load_ssh_private_key(f.read(), password=None)
        
        # 生成签名
        signature = private_key.sign(
            data.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Base64编码签名
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return {
            'X-Auth-Data': data,
            'X-Auth-Signature': signature_b64
        }


# 全局认证工具实例
auth_utils = AuthUtils()


def get_auth_utils():
    """获取认证工具实例"""
    return auth_utils
