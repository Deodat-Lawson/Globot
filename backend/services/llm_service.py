# """
# LLM Service Module - Supports Ollama or OpenAI (ChatGPT)
# """
# import logging
# from typing import List, Dict

# import ollama
# from config import get_settings

# logger = logging.getLogger(__name__)
# settings = get_settings()


# class OllamaService:
#     """Ollama LLM Service Wrapper SettingsConfigDict"""
    
#     def __init__(self):
#         self.client = ollama.Client(host=settings.ollama_base_url)
#         self.model = settings.ollama_model
#         logger.info(f"Initializing Ollama service: {self.model} @ {settings.ollama_base_url}")
    
#     def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 512) -> str:
#         """
#         Chat interface
        
#         Args:
#             messages: List of messages [{"role": "user", "content": "..."}]
#             temperature: Temperature parameter (0-1)
#                 - 0.3: Factual answers (customer categorization, technical spec queries)
#                 - 0.5: Balanced (most chat scenarios)
#                 - 0.7: Creative (marketing copy, requirement discovery)
#             max_tokens: Maximum tokens to generate
            
#         Returns:
#             Model response content
#         """
#         try:
#             response = self.client.chat(
#                 model=self.model,
#                 messages=messages,
#                 options={
#                     "temperature": temperature,
#                     "num_predict": max_tokens,
#                     "top_p": 0.9,  # nucleus sampling
#                     "repeat_penalty": 1.1  # reduce repetition
#                 }
#             )
#             return response['message']['content']
#         except Exception as e:
#             logger.error(f"Ollama call failed: {e}")
#             return "Sorry, I encountered some technical issues, please try again later."
    
#     def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
#         """
#         Generation interface (simplified)
        
#         Args:
#             prompt: Prompt
#             temperature: Temperature parameter
#                 - 0.1-0.3: Structured output (JSON, classification)
#                 - 0.5-0.7: Chat generation
#                 - 0.8-1.0: Creative content
#             max_tokens: Maximum tokens
            
#         Returns:
#             Generated content
#         """
#         try:
#             response = self.client.generate(
#                 model=self.model,
#                 prompt=prompt,
#                 options={
#                     "temperature": temperature,
#                     "num_predict": max_tokens,
#                     "top_p": 0.9,
#                     "repeat_penalty": 1.1
#                 }
#             )
#             return response['response']
#         except Exception as e:
#             logger.error(f"Ollama generation failed: {e}")
#             return "Sorry, I encountered some technical issues, please try again later."


# class OpenAIService:
#     """OpenAI ChatGPT Service Wrapper"""

#     def __init__(self):
#         try:
#             from openai import OpenAI
#         except Exception as exc:  # pragma: no cover - runtime guard
#             raise RuntimeError(f"OpenAI SDK not installed: {exc}") from exc

#         if not settings.openai_api_key:
#             raise ValueError("Missing openai_api_key, please configure it in environment variables or .env")

#         self.client = OpenAI(
#             api_key=settings.openai_api_key,
#             base_url=settings.openai_base_url or None,
#         )
#         self.model = settings.openai_model
#         logger.info(f"Initializing OpenAI service: {self.model} @ {settings.openai_base_url or 'https://api.openai.com'}")

#     def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 512) -> str:
#         try:
#             resp = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 temperature=temperature,
#                 max_tokens=max_tokens,
#             )
#             return resp.choices[0].message.content
#         except Exception as e:
#             logger.error(f"OpenAI call failed: {e}")
#             return "Sorry, I encountered some technical issues, please try again later."

#     def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
#         # Reuse chat interface with single user message
#         return self.chat(
#             [{"role": "user", "content": prompt}],
#             temperature=temperature,
#             max_tokens=max_tokens
#         )


# # Global Singleton
# _llm_service = None

# def get_llm_service() -> OllamaService:
#     """Get LLM service instance (singleton)"""
#     global _llm_service
#     if _llm_service is not None:
#         return _llm_service

#     provider = (settings.llm_provider or "ollama").lower()
#     if provider == "openai":
#         try:
#             _llm_service = OpenAIService()
#             return _llm_service
#         except Exception as e:
#             logger.error(f"OpenAI initialization failed, falling back to Ollama: {e}")

#     _llm_service = OllamaService()
#     return _llm_service
