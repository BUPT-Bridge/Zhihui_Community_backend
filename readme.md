# 智汇社区后端小程序
采用Django框架构建的智能社区后端系统

## 功能特性

- 用户认证和管理
- 向量数据库存储和搜索（Milvus）
- 文本嵌入和相似性搜索
- API接口认证和安全控制

## 安装部署

### 1. 环境准备

```bash
# 安装tmux（用于后台运行服务）
sudo dnf install tmux

# 创建Python虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. Tmux使用指南

```bash
# 创建新会话
tmux new -s myservice

# 在tmux中启动服务
python manage.py runserver 0.0.0.0:8000

# 分离会话（保持服务在后台运行）
# 按 Ctrl+B，然后按 D

# 重新连接会话
tmux attach -t myservice

# 查看所有会话
tmux list-sessions

# 结束会话
tmux kill-session -t myservice
```

### 3. 公私钥鉴权配置

#### 生成RSA密钥对

```bash
# 生成2048位的RSA密钥对
ssh-keygen -t rsa -b 2048 -f /tmp/api_keys -N ""

# 查看公钥
cat /tmp/api_keys.pub

# 查看私钥  
cat /tmp/api_keys

# 将公钥复制到项目目录
cp /tmp/api_keys.pub utils/
```

#### 密钥文件说明

- **私钥** (`/tmp/api_keys`): 客户端使用，用于生成签名
- **公钥** (`utils/api_keys.pub`): 服务器使用，用于验证签名

#### API认证方式

请求需要包含以下头信息：

```http
POST /api/database/insert-text/
X-Auth-Data: {timestamp_or_random_string}
X-Auth-Signature: {base64_encoded_signature}
Content-Type: application/json

{
  "text": "要嵌入的文本内容",
  "metadata": "可选元数据"
}
```

#### 客户端签名示例

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64
import time

# 加载私钥
with open('/tmp/api_keys', 'rb') as f:
    private_key = serialization.load_ssh_private_key(f.read(), password=None)

# 生成认证数据
auth_data = str(int(time.time()))

# 生成签名
signature = private_key.sign(
    auth_data.encode('utf-8'),
    padding.PKCS1v15(),
    hashes.SHA256()
)
signature_b64 = base64.b64encode(signature).decode('utf-8')

# 设置请求头
headers = {
    'X-Auth-Data': auth_data,
    'X-Auth-Signature': signature_b64
}
```

### 4. 启动服务

```bash
# 使用tmux后台运行
tmux new -s zhihui_backend
python manage.py runserver 0.0.0.0:8080
# 按 Ctrl+B, D 分离会话

# 或者直接运行
python manage.py runserver 0.0.0.0:8080
```

### 5. API接口

- `POST /api/database/insert-text/` - 带认证的文本插入
- `POST /api/database/insert/` - 直接插入向量数据
- `POST /api/database/search/` - 向量搜索
- `GET /api/database/health/` - 健康检查

### 6. 测试客户端

提供了测试脚本 `test_auth_client.py`：

```bash
python test_auth_client.py
```

## 注意事项

1. 确保Ollama服务在localhost:11434运行
2. 确保Milvus Lite数据库正常运行
3. 妥善保管私钥文件，不要泄露
4. 生产环境建议使用更安全的密钥管理方式
