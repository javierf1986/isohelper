"""
AI Enhancement Service
Option B: AI Integration with flexible LLM support (Mistral, OpenAI, etc.)

This service provides context-aware content enhancement for ISO standards documents.
Supports multiple AI providers with a unified interface.
"""
from typing import Dict, List, Optional, Literal
from pathlib import Path
import logging
from abc import ABC, abstractmethod

from config.settings import settings


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate content using the AI provider"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name"""
        pass


class MistralProvider(AIProvider):
    """Mistral AI provider implementation"""
    
    def __init__(self, api_key: str):
        try:
            from mistralai.client import MistralClient
            self.client = MistralClient(api_key=api_key)
            self.model = "mistral-medium"  # Good balance of performance and cost
            logging.info("✅ Mistral AI provider initialized")
        except ImportError:
            logging.error("❌ mistralai package not installed. Run: pip install mistralai")
            raise
        except Exception as e:
            logging.error(f"❌ Failed to initialize Mistral: {e}")
            raise
    
    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate content using Mistral AI"""
        try:
            from mistralai.models.chat_completion import ChatMessage
            
            messages = [
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Mistral generation failed: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "Mistral AI"


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation (fallback option)"""
    
    def __init__(self, api_key: str):
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
            self.model = "gpt-4o-mini"  # Cost-effective option
            logging.info("✅ OpenAI provider initialized")
        except ImportError:
            logging.error("❌ openai package not installed")
            raise
        except Exception as e:
            logging.error(f"❌ Failed to initialize OpenAI: {e}")
            raise
    
    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate content using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an ISO standards quality management expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"OpenAI generation failed: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "OpenAI"


class LocalLLMProvider(AIProvider):
    """Local LLM provider (Ollama, LM Studio, etc.)"""
    
    def __init__(self, base_url: str, model_name: str = "mistral"):
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                base_url=base_url,
                api_key="not-needed"  # Local LLMs don't need API keys
            )
            self.model = model_name
            logging.info(f"✅ Local LLM provider initialized: {base_url}")
        except Exception as e:
            logging.error(f"❌ Failed to initialize Local LLM: {e}")
            raise
    
    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate content using local LLM"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Local LLM generation failed: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return f"Local LLM ({self.model})"


class AIEnhancer:
    """
    Main AI Enhancement Service
    Provides context-aware content generation for ISO 9001 documents
    """
    
    def __init__(
        self,
        provider: Literal["mistral", "openai", "local"] = "mistral",
        api_key: Optional[str] = None,
        local_url: Optional[str] = None
    ):
        """
        Initialize AI Enhancer with specified provider
        
        Args:
            provider: AI provider to use ("mistral", "openai", "local")
            api_key: API key for cloud providers (Mistral, OpenAI)
            local_url: Base URL for local LLM (e.g., "http://localhost:11434/v1")
        """
        self.provider_name = provider
        
        # Initialize the appropriate provider
        if provider == "mistral":
            if not api_key:
                api_key = settings.MISTRAL_API_KEY
            self.provider = MistralProvider(api_key)
        
        elif provider == "openai":
            if not api_key:
                api_key = settings.OPENAI_API_KEY
            self.provider = OpenAIProvider(api_key)
        
        elif provider == "local":
            local_url = local_url or getattr(settings, "LOCAL_LLM_URL", "http://localhost:11434/v1")
            model_name = getattr(settings, "LOCAL_LLM_MODEL", "mistral")
            self.provider = LocalLLMProvider(local_url, model_name)  # type: ignore
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        logging.info(f"🤖 AI Enhancer initialized with {self.provider.get_provider_name()}")
    
    async def enhance_clause_content(
        self,
        clause: str,
        base_content: str,
        company_data: Dict,
        enhancement_level: Literal["light", "moderate", "comprehensive"] = "moderate"
    ) -> str:
        """
        Enhance ISO clause content with AI-generated context
        
        Args:
            clause: ISO clause number (e.g., "4.1")
            base_content: Template-generated base content
            company_data: Company information for context
            enhancement_level: How much enhancement to apply
            
        Returns:
            Enhanced content with AI-generated improvements
        """
        try:
            prompt = self._build_enhancement_prompt(
                clause, base_content, company_data, enhancement_level
            )
            
            # Adjust max tokens based on enhancement level
            token_limits = {
                "light": 500,
                "moderate": 1000,
                "comprehensive": 2000
            }
            
            enhanced_section = await self.provider.generate_content(
                prompt=prompt,
                max_tokens=token_limits[enhancement_level],
                temperature=0.7
            )
            
            # Integrate enhanced content with base content
            return self._integrate_enhancement(base_content, enhanced_section)
            
        except Exception as e:
            logging.error(f"Content enhancement failed for clause {clause}: {e}")
            # Return original content if enhancement fails
            return base_content
    
    async def generate_industry_specific_examples(
        self,
        clause: str,
        industry: str,
        company_size: str
    ) -> str:
        """
        Generate industry-specific examples for ISO clause
        
        Args:
            clause: ISO clause number
            industry: Industry sector
            company_size: Company size (small/medium/large)
            
        Returns:
            Industry-specific examples and recommendations
        """
        prompt = f"""Generate 3 practical, industry-specific examples for ISO Clause {clause}.

Industry: {industry}
Company Size: {company_size}

For each example, provide:
1. A realistic scenario
2. How it applies to ISO requirements
3. Practical implementation steps

Format as markdown with clear headings."""

        try:
            return await self.provider.generate_content(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.8
            )
        except Exception as e:
            logging.error(f"Example generation failed: {e}")
            return "*(AI-generated examples unavailable)*"
    
    async def suggest_process_improvements(
        self,
        company_data: Dict,
        current_processes: List[str]
    ) -> str:
        """
        Suggest QMS process improvements based on company profile
        
        Args:
            company_data: Company information
            current_processes: List of current processes
            
        Returns:
            Improvement suggestions
        """
        prompt = f"""As an ISO quality management expert, analyze the following company profile and suggest process improvements:

Company: {company_data.get('company_name')}
Industry: {company_data.get('industry')}
Size: {company_data.get('company_size')}
Current Processes: {', '.join(current_processes)}

Provide:
1. 3-5 specific process improvement recommendations
2. Alignment with ISO standard requirements
3. Expected benefits and implementation timeline

Format as markdown with clear sections."""

        try:
            return await self.provider.generate_content(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.7
            )
        except Exception as e:
            logging.error(f"Process improvement suggestions failed: {e}")
            return "*(AI-generated suggestions unavailable)*"
    
    def _build_enhancement_prompt(
        self,
        clause: str,
        base_content: str,
        company_data: Dict,
        enhancement_level: str
    ) -> str:
        """Build prompt for content enhancement"""
        
        company_name = company_data.get("company_name", "the organization")
        industry = company_data.get("industry", "general")
        company_size = company_data.get("company_size", "medium")
        custom_context = company_data.get("custom_context", "")
        
        if enhancement_level == "light":
            instruction = "Add 2-3 brief, specific details"
        elif enhancement_level == "moderate":
            instruction = "Expand with specific examples and context"
        else:  # comprehensive
            instruction = "Provide comprehensive details, examples, and best practices"
        
        prompt = f"""You are an ISO quality management expert. Enhance the following ISO {clause} documentation for {company_name}.

Industry: {industry}
Company Size: {company_size}
{f"Additional Context: {custom_context}" if custom_context else ""}

Base Documentation:
{base_content[:1000]}  # Limit context to avoid token issues

Task: {instruction} that are:
1. Specific to the {industry} industry
2. Appropriate for a {company_size} organization
3. Aligned with ISO standard requirements
4. Practical and implementable

Provide ONLY the enhanced section content in markdown format. Do not include explanations or meta-commentary."""

        return prompt
    
    def _integrate_enhancement(self, base_content: str, enhanced_section: str) -> str:
        """
        Integrate AI-enhanced content with base template content
        
        Strategy: Insert enhanced content after first section of base content
        """
        lines = base_content.split('\n')
        
        # Find first major section break (after first ## heading)
        insert_position = 0
        header_count = 0
        
        for i, line in enumerate(lines):
            if line.startswith('## '):
                header_count += 1
                if header_count == 2:  # After first section
                    insert_position = i
                    break
        
        if insert_position > 0:
            # Insert AI enhancement after first section
            enhanced_lines = lines[:insert_position]
            enhanced_lines.append("\n### AI-Enhanced Context\n")
            enhanced_lines.append(enhanced_section)
            enhanced_lines.append("\n")
            enhanced_lines.extend(lines[insert_position:])
            return '\n'.join(enhanced_lines)
        else:
            # Append at end if structure is unclear
            return f"{base_content}\n\n### AI-Enhanced Content\n\n{enhanced_section}"
    
    def get_provider_info(self) -> Dict:
        """Get information about current AI provider"""
        return {
            "provider": self.provider_name,
            "provider_name": self.provider.get_provider_name(),
            "status": "active"
        }
