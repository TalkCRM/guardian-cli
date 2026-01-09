"""
Google Gemini API client for Guardian
Handles communication with Gemini AI model via Antigravity Auth or Standard API Key
"""

import time
import asyncio
import os
from typing import Optional, Dict, Any, List, Union

# Import standard Google GenAI deps
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Import Antigravity deps
try:
    from antigravity_auth import AntigravityService, NoAccountsError
    ANTIGRAVITY_AVAILABLE = True
except ImportError:
    ANTIGRAVITY_AVAILABLE = False

from utils.logger import get_logger


class GeminiClient:
    """Google Gemini API client wrapper supporting Dual Authentication"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger(config)
        
        ai_config = config.get("ai", {})
        self.model_name = ai_config.get("model", "gemini-3-pro")
        
        # Determine authentication method
        self.auth_method = ai_config.get("auth_method", "auto").lower()
        self.api_key = ai_config.get("api_key") or os.environ.get("GOOGLE_API_KEY")
        
        # Rate limiting configuration
        self.rate_limit = ai_config.get("rate_limit", 60)
        self._min_request_interval = 60.0 / self.rate_limit if self.rate_limit > 0 else 0
        self._last_request_time = 0.0
        
        self.backend = None
        self._initialize_backend()

    def _initialize_backend(self):
        """Initialize the appropriate backend based on configuration"""
        
        # 1. Try Antigravity if selected or auto
        if self.auth_method in ["auto", "antigravity"]:
            if self._try_init_antigravity():
                return
            
            if self.auth_method == "antigravity":
                 raise RuntimeError("Antigravity Auth selected but initialization failed (no accounts or library missing).")

        # 2. Try Standard API if selected or auto (fallback)
        if self.auth_method in ["auto", "api_key"]:
            if self._try_init_api():
                return
                
            if self.auth_method == "api_key":
                 raise RuntimeError("API Key Auth selected but initialization failed (no API key or library missing).")

        raise RuntimeError("No valid authentication method available. Please login via 'guardian auth login' OR set GOOGLE_API_KEY.")

    def _try_init_antigravity(self) -> bool:
        """Attempt to initialize Antigravity backend"""
        if not ANTIGRAVITY_AVAILABLE:
            self.logger.debug("Antigravity library not found.")
            return False
            
        try:
            # Check for accounts first to avoid unnecessary service init overhead if empty
            service = AntigravityService(model=self.model_name, quiet_mode=True)
            if not service.get_accounts():
                self.logger.debug("No Antigravity accounts found.")
                return False
                
            self.backend = service
            self.backend_type = "antigravity"
            self.logger.info(f"Initialized Antigravity backend: {self.model_name}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to check Antigravity status: {e}")
            return False

    def _try_init_api(self) -> bool:
        """Attempt to initialize Standard API backend"""
        if not LANGCHAIN_AVAILABLE:
            self.logger.warning("LangChain Google GenAI library not found.")
            return False
            
        if not self.api_key:
            self.logger.debug("No GOOGLE_API_KEY found.")
            return False
            
        try:
            self.backend = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=self.config.get("ai", {}).get("temperature", 0.2),
                convert_system_message_to_human=True 
            )
            self.backend_type = "api"
            self.logger.info(f"Initialized Standard API backend: {self.model_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Standard API backend: {e}")
            return False

    async def _apply_rate_limit(self):
        """Apply rate limiting between API calls"""
        if self._min_request_interval > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                wait_time = self._min_request_interval - elapsed
                await asyncio.sleep(wait_time)
        self._last_request_time = time.time()
    
    def _apply_rate_limit_sync(self):
        """Synchronous rate limiting"""
        if self._min_request_interval > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                wait_time = self._min_request_interval - elapsed
                time.sleep(wait_time)
        self._last_request_time = time.time()
    
    def _format_context_antigravity(self, context: Optional[List[Any]]) -> str:
        """Format context into a string history for Antigravity (temporary shim)"""
        if not context:
            return ""
            
        history_lines = []
        for msg in context:
            role = "user"
            content = ""
            
            # Handle LangChain objects
            if hasattr(msg, "content") and hasattr(msg, "type"):
                role = "user" if msg.type == "human" else "model"
                content = msg.content
            # Handle dicts
            elif isinstance(msg, dict):
                role = msg.get("role", "user")
                parts = msg.get("parts", [{"text": ""}])
                content = parts[0].get("text", "") if parts else ""
            
            if content:
                history_lines.append(f"{role.upper()}: {content}")
        
        return "\n".join(history_lines)

    def _format_context_langchain(self, context: Optional[List[Any]]) -> List[Any]:
        """Format context for LangChain backend"""
        if not context:
            return []
            
        messages = []
        for msg in context:
            # Already a LangChain message object?
            if hasattr(msg, "content") and hasattr(msg, "type"):
                messages.append(msg)
                continue
                
            # Convert dict to LangChain message
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                text = msg.get("parts", [{"text": ""}])[0].get("text", "")
                
                if role == "user":
                    messages.append(HumanMessage(content=text))
                elif role == "model":
                    messages.append(AIMessage(content=text))
        
        return messages

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None
    ) -> str:
        """Generate response using current backend"""
        await self._apply_rate_limit()
        
        try:
            if self.backend_type == "antigravity":
                # Antigravity Logic
                full_prompt = prompt
                history_str = self._format_context_antigravity(context)
                
                if history_str:
                    full_prompt = f"Previous conversation history:\n{history_str}\n\nCurrent interaction:\n{prompt}"
                
                return await self.backend.generate(
                    prompt=full_prompt,
                    system_prompt=system_prompt
                )
                
            elif self.backend_type == "api":
                # Standard API Logic (LangChain)
                messages = []
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                
                # Add history
                messages.extend(self._format_context_langchain(context))
                
                # Add current prompt
                messages.append(HumanMessage(content=prompt))
                
                response = await self.backend.ainvoke(messages)
                return response.content

        except Exception as e:
            self.logger.error(f"Generation failed ({self.backend_type}): {e}")
            raise

    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None
    ) -> str:
        """Synchronous generation"""
        self._apply_rate_limit_sync()
        
        try:
            if self.backend_type == "antigravity":
                 # Antigravity Logic
                full_prompt = prompt
                history_str = self._format_context_antigravity(context)
                
                if history_str:
                    full_prompt = f"Previous conversation history:\n{history_str}\n\nCurrent interaction:\n{prompt}"
                
                return self.backend.generate_sync(
                    prompt=full_prompt,
                    system_prompt=system_prompt
                )

            elif self.backend_type == "api":
                 # Standard API Logic (LangChain)
                messages = []
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                messages.extend(self._format_context_langchain(context))
                messages.append(HumanMessage(content=prompt))
                
                response = self.backend.invoke(messages)
                return response.content
                
        except Exception as e:
            self.logger.error(f"Sync generation failed ({self.backend_type}): {e}")
            raise

    async def generate_with_reasoning(
        self,
        prompt: str,
        system_prompt: str,
        context: Optional[list] = None
    ) -> Dict[str, str]:
        """Generate response with explicit reasoning"""
        
        # Enhanced prompt to extract reasoning
        enhanced_prompt = f"""{prompt}

Please structure your response as:
1. REASONING: Explain your thought process and decision-making
2. RESPONSE: Provide your final answer or recommendation
"""
        
        response = await self.generate(enhanced_prompt, system_prompt, context)
        
        # Parse reasoning and response
        parts = {"reasoning": "", "response": ""}
        
        if "REASONING:" in response and "RESPONSE:" in response:
            try:
                reasoning_idx = response.find("REASONING:")
                response_idx = response.find("RESPONSE:")
                
                if reasoning_idx != -1 and response_idx != -1:
                    reasoning_content = response[reasoning_idx + len("REASONING:"):response_idx].strip()
                    response_content = response[response_idx + len("RESPONSE:"):].strip()
                    
                    parts["reasoning"] = reasoning_content
                    parts["response"] = response_content
                else:
                     parts["response"] = response
                     parts["reasoning"] = "Parsing failed, check format."
            except Exception:
                parts["response"] = response
                parts["reasoning"] = "Error parsing response structure"
        else:
            parts["response"] = response
            parts["reasoning"] = "No explicit reasoning provided"
        
        return parts
