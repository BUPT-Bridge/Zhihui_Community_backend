"""
Ollama客户端工具
用于调用Ollama API获取文本嵌入向量
"""
import requests
import json
from typing import List, Optional


class OllamaClient:
    """Ollama客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    def get_embedding(self, text: str, model: str = "chroma/all-minilm-l6-v2-f32") -> Optional[List[float]]:
        """
        获取文本的嵌入向量
        
        Args:
            text: 要嵌入的文本
            model: 使用的模型名称
            
        Returns:
            List[float]: 嵌入向量，失败返回None
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("embedding")
            else:
                print(f"❌ Ollama API请求失败: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama连接错误: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            return None
        except Exception as e:
            print(f"❌ 获取嵌入向量失败: {e}")
            return None
    
    def check_connection(self) -> bool:
        """检查Ollama连接状态"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> Optional[list]:
        """获取可用模型列表"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get("models", [])
            return None
        except:
            return None


# 全局Ollama客户端实例
ollama_client = OllamaClient()


def get_ollama_client():
    """获取Ollama客户端实例"""
    return ollama_client
