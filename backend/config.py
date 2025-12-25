from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """系统配置"""
    
    # 数据库
    database_url: str = "postgresql://user:password@localhost:5432/dji_sales_mvp"
    
    # Ollama配置（使用本地LLM）
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:latest"  # 或 llama3, mistral等
    
    # 向量数据库
    chroma_persist_dir: str = "./data/vectordb"
    
    # 文件上传
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 50
    
    # 系统配置
    log_level: str = "INFO"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()
