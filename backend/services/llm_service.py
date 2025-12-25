"""
LLM服务模块 - 使用Ollama本地大模型
"""
import ollama
from config import get_settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class OllamaService:
    """Ollama LLM服务封装"""
    
    def __init__(self):
        self.client = ollama.Client(host=settings.ollama_base_url)
        self.model = settings.ollama_model
        logger.info(f"初始化Ollama服务: {self.model} @ {settings.ollama_base_url}")
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 512) -> str:
        """
        对话接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数 (0-1)
                - 0.3: 事实性回答（客户分类、技术参数查询）
                - 0.5: 平衡（大部分对话场景）
                - 0.7: 创造性（营销文案、需求挖掘）
            max_tokens: 最大生成token数
            
        Returns:
            模型回复内容
        """
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,  # 核采样
                    "repeat_penalty": 1.1  # 减少重复
                }
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama调用失败: {e}")
            return "抱歉，我遇到了一些技术问题，请稍后再试。"
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
        """
        生成接口（简化版）
        
        Args:
            prompt: 提示词
            temperature: 温度参数
                - 0.1-0.3: 结构化输出（JSON、分类）
                - 0.5-0.7: 对话生成
                - 0.8-1.0: 创意内容
            max_tokens: 最大token数
            
        Returns:
            生成内容
        """
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            )
            return response['response']
        except Exception as e:
            logger.error(f"Ollama生成失败: {e}")
            return "抱歉，我遇到了一些技术问题，请稍后再试。"

# 全局单例
_llm_service = None

def get_llm_service() -> OllamaService:
    """获取LLM服务实例（单例）"""
    global _llm_service
    if _llm_service is None:
        _llm_service = OllamaService()
    return _llm_service
