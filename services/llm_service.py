"""
LLM service for generating plant information and garden plans.
Supports both Ollama (local) and OpenAI (production) providers.
"""

import asyncio
import json
from typing import Optional, Dict, Any
from config import settings

class LLMService:
    """
    Service for LLM interactions with provider switching
    """
    
    def __init__(self):
        self.provider = settings.llm_provider
        print(f"🤖 LLM Service initialized with {self.provider.upper()} provider")
    
    async def generate_plant_info(self, prompt: str) -> Optional[str]:
        """
        Generate plant information using the configured LLM provider
        """
        if self.provider == "openai":
            return await self._generate_with_openai(prompt)
        else:  # ollama
            return await self._generate_with_ollama(prompt)
    
    async def _generate_with_ollama(self, prompt: str) -> Optional[str]:
        """
        Generate response using Ollama (local LLM)
        """
        try:
            # Import ollama here to avoid dependency issues if not installed
            import ollama
            
            response = await asyncio.to_thread(
                ollama.generate,
                model=settings.ollama_model,
                prompt=prompt,
                options={
                    "temperature": 0.3,  # Lower temperature for more consistent data
                    "top_p": 0.9,
                }
            )
            
            return response.get('response', '').strip()
            
        except ImportError:
            print("❌ Ollama not installed. Install with: pip install ollama")
            return None
        except Exception as e:
            print(f"❌ Ollama generation error: {e}")
            return None
    
    async def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """
        Generate response using OpenAI API
        """
        try:
            # Import openai here to avoid dependency issues if not installed
            import openai
            
            if not settings.openai_api_key:
                print("❌ OpenAI API key not configured")
                return None
            
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert gardener and botanist. Provide accurate, structured plant growing information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=settings.openai_max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except ImportError:
            print("❌ OpenAI not installed. Install with: pip install openai")
            return None
        except Exception as e:
            print(f"❌ OpenAI generation error: {e}")
            return None
    
    def is_configured(self) -> bool:
        """
        Check if the current LLM provider is properly configured
        """
        return settings.validate_llm_config()

# Global instance
llm_service = LLMService()