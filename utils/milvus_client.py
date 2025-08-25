"""
Milvus向量数据库客户端工具
使用Milvus Lite嵌入式版本
"""
import os
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from django.conf import settings
from utils.env_config import get_env_config


class MilvusClient:
    """Milvus客户端类 - 使用Milvus Lite"""
    
    def __init__(self):
        self.env_config = get_env_config()
        self.collection_name = os.getenv('MILVUS_COLLECTION_NAME', 'zhihui_vectors')
        self.vector_dim = int(os.getenv('VECTOR_DIMENSION', '384'))
        self.collection = None
        self.connected = False
        
    def connect(self):
        """连接到Milvus Lite嵌入式数据库"""
        try:
            # 首先检查是否已经连接
            try:
                connections.get_connection("default")
                print("✅ 已经连接到Milvus Lite")
                self.connected = True
                return True
            except:
                pass
            
            # 使用Milvus Lite嵌入式模式 - 使用文件URI
            connections.connect(
                alias="default", 
                uri="./milvus_data/milvus.db"
            )
            print("✅ 成功连接到Milvus Lite嵌入式数据库")
            self.connected = True
            return True
        except Exception as e:
            print(f"❌ 连接Milvus Lite失败: {e}")
            # 尝试不同的连接方式
            try:
                # 尝试使用默认嵌入式连接
                connections.connect("default")
                print("✅ 使用默认嵌入式连接成功")
                self.connected = True
                return True
            except Exception as e2:
                print(f"❌ 默认连接也失败: {e2}")
                return False
    
    def create_collection(self):
        """创建向量集合"""
        if utility.has_collection(self.collection_name):
            print(f"✅ 集合 {self.collection_name} 已存在")
            self.collection = Collection(self.collection_name)
            return True
            
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.vector_dim),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=500)
        ]
        
        # 创建集合schema
        schema = CollectionSchema(fields, "智慧社区向量数据集合")
        
        try:
            self.collection = Collection(self.collection_name, schema)
            print(f"✅ 成功创建集合: {self.collection_name}")
            
            # 创建索引
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            self.collection.create_index("vector", index_params)
            print("✅ 成功创建向量索引")
            return True
            
        except Exception as e:
            print(f"❌ 创建集合失败: {e}")
            return False
    
    def insert_vector(self, vector, content, metadata=None):
        """插入向量数据"""
        if not self.collection:
            if not self.connect() or not self.create_collection():
                return None
        
        try:
            # 准备数据
            data = [
                [vector],  # 向量数据
                [content],  # 内容
                [metadata or ""]  # 元数据
            ]
            
            # 插入数据
            result = self.collection.insert(data)
            print(f"✅ 成功插入向量数据，ID: {result.primary_keys[0]}")
            return result.primary_keys[0]
            
        except Exception as e:
            print(f"❌ 插入向量数据失败: {e}")
            return None
    
    def search_vectors(self, query_vector, limit=10):
        """搜索相似向量"""
        if not self.collection:
            if not self.connect() or not self.create_collection():
                return []
        
        try:
            # 加载集合到内存
            self.collection.load()
            
            # 搜索参数
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            
            # 执行搜索
            results = self.collection.search(
                data=[query_vector],
                anns_field="vector",
                param=search_params,
                limit=limit,
                output_fields=["content", "metadata"]
            )
            
            # 格式化结果
            search_results = []
            for hits in results:
                for hit in hits:
                    search_results.append({
                        "id": hit.id,
                        "distance": hit.distance,
                        "content": hit.entity.get("content", ""),
                        "metadata": hit.entity.get("metadata", "")
                    })
            
            return search_results
            
        except Exception as e:
            print(f"❌ 搜索向量失败: {e}")
            return []
    
    def disconnect(self):
        """断开连接"""
        try:
            connections.disconnect("default")
            print("✅ 已断开Milvus连接")
        except:
            pass


# 全局Milvus客户端实例
milvus_client = MilvusClient()


def get_milvus_client():
    """获取Milvus客户端实例"""
    return milvus_client
