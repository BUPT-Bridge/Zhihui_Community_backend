"""
环境变量配置模块
负责加载和验证环境变量
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


class EnvConfig:
    """环境变量配置类"""
    
    def __init__(self):
        # 加载环境变量
        self._load_env()
        # 验证必需的环境变量
        self._validate_required_vars()
    
    def _load_env(self):
        """加载 .env 文件"""
        # 获取项目根目录
        base_dir = Path(__file__).resolve().parent.parent
        env_path = base_dir / '.env'
        
        # 加载 .env 文件
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ 成功加载环境变量文件: {env_path}")
        else:
            print(f"⚠️  警告: 未找到 .env 文件: {env_path}")
            print("请参考 .env.example 创建 .env 文件")
    
    def _validate_required_vars(self):
        """验证必需的环境变量"""
        required_vars = {
            'WX_APPID': '微信小程序AppID',
            'WX_SECRET': '微信小程序Secret',
            'JWT_SECRET_KEY': 'JWT密钥',
            'DJANGO_SECRET_KEY': 'Django密钥'
        }
        
        missing_vars = []
        for var_name, description in required_vars.items():
            value = os.getenv(var_name)
            if not value or value.startswith('your_'):
                missing_vars.append(f"{var_name} ({description})")
        
        if missing_vars:
            print("❌ 缺少以下必需的环境变量配置:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n请在 .env 文件中配置这些变量")
            print("参考 .env.example 文件的格式")
            sys.exit(1)
        else:
            print("✅ 所有必需的环境变量已正确配置")
    
    @property
    def wx_appid(self):
        """微信小程序AppID"""
        return os.getenv('WX_APPID', '')
    
    @property
    def wx_secret(self):
        """微信小程序Secret"""
        return os.getenv('WX_SECRET', '')
    
    @property
    def jwt_secret_key(self):
        """JWT密钥"""
        return os.getenv('JWT_SECRET_KEY', 'default_secret_key')
    
    @property
    def jwt_expire_hours(self):
        """JWT过期时间（小时）"""
        try:
            return int(os.getenv('JWT_EXPIRE_HOURS', '168'))
        except ValueError:
            return 168  # 默认7天
    
    @property
    def django_secret_key(self):
        """Django SECRET_KEY"""
        return os.getenv('DJANGO_SECRET_KEY', 'default_django_secret_key')
    
    @property
    def debug(self):
        """调试模式"""
        return os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on')
    
    @property
    def allowed_hosts(self):
        """允许的主机列表"""
        hosts_str = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
        return [host.strip() for host in hosts_str.split(',') if host.strip()]
    
    def get_env_info(self):
        """获取环境变量信息（用于调试）"""
        return {
            'wx_appid': self.wx_appid[:10] + '...' if len(self.wx_appid) > 10 else self.wx_appid,
            'wx_secret': '***' if self.wx_secret else '',
            'jwt_secret_key': '***' if self.jwt_secret_key else '',
            'jwt_expire_hours': self.jwt_expire_hours,
            'debug': self.debug,
            'allowed_hosts': self.allowed_hosts
        }


# 创建全局配置实例
def get_env_config():
    """获取环境变量配置实例"""
    if not hasattr(get_env_config, '_instance'):
        get_env_config._instance = EnvConfig()
    return get_env_config._instance


# 便捷的配置访问函数
def get_wx_config():
    """获取微信配置"""
    config = get_env_config()
    return {
        'appid': config.wx_appid,
        'secret': config.wx_secret
    }


def get_jwt_config():
    """获取JWT配置"""
    config = get_env_config()
    return {
        'secret_key': config.jwt_secret_key,
        'expire_hours': config.jwt_expire_hours
    }
