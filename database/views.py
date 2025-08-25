from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import numpy as np
import csv
import os
from utils.milvus_client import get_milvus_client
from utils.auth_utils import get_auth_utils
from utils.ollama_client import get_ollama_client
from utils.auth import require_auth, get_openid_from_request


@require_http_methods(["GET"])
def health_check(request):
    """
    健康检查接口
    检查Milvus连接状态
    """
    try:
        milvus_client = get_milvus_client()
        connected = milvus_client.connect()
        
        if connected:
            return JsonResponse({
                'code': 200,
                'message': '服务正常',
                'data': {
                    'milvus_connected': True,
                    'collection_name': milvus_client.collection_name,
                    'vector_dimension': milvus_client.vector_dim
                }
            })
        else:
            return JsonResponse({
                'code': 503,
                'message': 'Milvus连接失败',
                'data': {
                    'milvus_connected': False
                }
            }, status=503)
            
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'健康检查失败: {str(e)}',
            'data': None
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def insert_text_with_auth(request):
    """
    带认证的文本插入接口
    请求头需要包含:
    X-Auth-Data: 要签名的数据（通常是时间戳或随机字符串）
    X-Auth-Signature: 对X-Auth-Data的签名（base64编码）
    
    POST请求参数:
    {
        "text": "要嵌入的文本内容",      # 必填，要嵌入的文本
        "metadata": "额外元数据"         # 可选，额外元数据信息
    }
    """
    try:
        # 认证验证
        auth_data = request.headers.get('X-Auth-Data')
        auth_signature = request.headers.get('X-Auth-Signature')
        
        if not auth_data or not auth_signature:
            return JsonResponse({
                'code': 401,
                'message': '认证失败: 缺少认证头信息',
                'data': None
            }, status=401)
        
        auth_utils = get_auth_utils()
        if not auth_utils.verify_signature(auth_data, auth_signature):
            return JsonResponse({
                'code': 401,
                'message': '认证失败: 签名验证失败',
                'data': None
            }, status=401)
        
        # 解析请求数据
        data = json.loads(request.body)
        text = data.get('text')
        metadata = data.get('metadata')
        
        # 参数验证
        if not text:
            return JsonResponse({
                'code': 400,
                'message': '参数错误: text为必填项',
                'data': None
            }, status=400)
        
        # 获取文本嵌入向量
        ollama_client = get_ollama_client()
        embedding = ollama_client.get_embedding(text)
        
        if not embedding:
            return JsonResponse({
                'code': 500,
                'message': '获取嵌入向量失败',
                'data': None
            }, status=500)
        
        # 验证向量维度
        milvus_client = get_milvus_client()
        if len(embedding) != milvus_client.vector_dim:
            return JsonResponse({
                'code': 500,
                'message': f'向量维度不匹配: 期望 {milvus_client.vector_dim}, 实际 {len(embedding)}',
                'data': None
            }, status=500)
        
        # 插入向量数据
        vector_id = milvus_client.insert_vector(embedding, text, metadata)
        
        if vector_id:
            return JsonResponse({
                'code': 200,
                'message': '插入成功',
                'data': {
                    'id': vector_id,
                    'text': text,
                    'metadata': metadata,
                    'embedding_dim': len(embedding)
                }
            })
        else:
            return JsonResponse({
                'code': 500,
                'message': '插入失败',
                'data': None
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'code': 400,
            'message': 'JSON格式错误',
            'data': None
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def search_text_with_auth(request, openid=None):
    """
    带token鉴权的文本搜索接口
    需要Authorization头: Bearer <token>
    
    POST请求参数:
    {
        "text": "查询文本",      # 必填，要搜索的文本
        "limit": 10             # 可选，返回结果数量，默认10
    }
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        text = data.get('text')
        limit = data.get('limit', 10)
        
        # 参数验证
        if not text:
            return JsonResponse({
                'code': 400,
                'message': '参数错误: text为必填项',
                'data': None
            }, status=400)
        
        # 获取文本嵌入向量
        ollama_client = get_ollama_client()
        embedding = ollama_client.get_embedding(text)
        
        if not embedding:
            return JsonResponse({
                'code': 500,
                'message': '获取嵌入向量失败',
                'data': None
            }, status=500)
        
        # 验证向量维度
        milvus_client = get_milvus_client()
        if len(embedding) != milvus_client.vector_dim:
            return JsonResponse({
                'code': 500,
                'message': f'向量维度不匹配: 期望 {milvus_client.vector_dim}, 实际 {len(embedding)}',
                'data': None
            }, status=500)
        
        # 搜索相似向量
        results = milvus_client.search_vectors(embedding, limit)
        
        # 提取content内容
        contents = [item['content'] for item in results]
        
        return JsonResponse({
            'code': 200,
            'message': '搜索成功',
            'data': {
                'results': contents,
                'total': len(contents),
                'openid': openid  # 返回验证的用户openid
            }
        })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'code': 400,
            'message': 'JSON格式错误',
            'data': None
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'data': None
        }, status=500)


@require_http_methods(["GET"])
def export_to_csv(request):
    """
    导出向量数据库所有内容到CSV文件
    无需认证，任何人都可以导出
    
    返回:
    {
        "code": 200,
        "message": "导出成功",
        "data": {
            "file_path": "/file/vectors_export.csv",
            "total_records": 100
        }
    }
    """
    try:
        milvus_client = get_milvus_client()
        
        # 连接到Milvus并创建集合（如果不存在）
        if not milvus_client.connect() or not milvus_client.create_collection():
            return JsonResponse({
                'code': 503,
                'message': 'Milvus连接或集合创建失败',
                'data': None
            }, status=503)
        
        # 确保集合已加载
        if not milvus_client.collection:
            return JsonResponse({
                'code': 503,
                'message': 'Milvus集合未初始化',
                'data': None
            }, status=503)
        
        # 加载集合到内存
        milvus_client.collection.load()
        
        # 查询所有数据
        results = milvus_client.collection.query(
            expr="",  # 空表达式表示查询所有
            output_fields=["id", "content", "metadata"],
            limit=10000  # 设置一个较大的限制，确保获取所有数据
        )
        
        # 创建文件目录
        file_dir = "file"
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        
        # 生成CSV文件路径（使用时间戳作为文件名）
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(file_dir, f"vectors_export_{timestamp}.csv")
        
        # 写入CSV文件
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'content', 'metadata']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in results:
                writer.writerow({
                    'id': item['id'],
                    'content': item['content'],
                    'metadata': item.get('metadata', '')
                })
        
        return JsonResponse({
            'code': 200,
            'message': '导出成功',
            'data': {
                'file_path': file_path,
                'total_records': len(results)
            }
        })
            
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'导出失败: {str(e)}',
            'data': None
        }, status=500)
