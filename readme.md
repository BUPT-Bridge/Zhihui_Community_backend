# 智汇社区后端

智汇社区后端是基于Django框架开发的微信小程序服务端，提供用户认证、资料管理等功能。

## 环境要求

- Python 3.9+
- Django 5.2+
- 其他依赖见 requirements.txt

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 文件为 `.env`，并填写相关配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的配置，尤其是微信小程序的 AppID 和 Secret。

### 3. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建超级用户（可选）

```bash
python manage.py createsuperuser
```

### 5. 启动开发服务器

```bash
python manage.py runserver 0.0.0.0:8000
```

现在，服务器应该在 http://localhost:8000/ 上运行。

## API 文档

主要API接口：

- 微信登录：`POST /user/wx-login/`
- 验证登录状态：`GET /user/wx-login/`
- 获取用户信息：`GET /user/profile/`
- 更新用户信息：`PUT /user/profile/`

