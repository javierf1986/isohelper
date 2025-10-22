"""
AI-Powered ISO Parser using Local LLM (TinyLlama)

This module enhances the ISO importer with semantic understanding:
- Better metadata extraction (ISO number, year, title)
- Semantic clause boundary detection
- Context-aware requirement classification
- Smart template generation
- Quality validation

Uses TinyLlama 1.1B running locally via Ollama (no API keys needed)
"""

import re
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from backend.services.iso_importer import (
    ExtractedClause,
    ISOMetadata,
    ClauseType
)
from backend.services.ai_enhancer import AIEnhancer, LocalLLMProvider
from config.settings import settings

logger = logging.getLogger(__name__)


class SimpleLLMClient:
    """Simple synchronous LLM client for parsing tasks"""
    
    def __init__(self):
        self.provider = LocalLLMProvider(
            base_url=settings.LOCAL_LLM_URL,
            model_name=settings.LOCAL_LLM_MODEL
        )
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.1) -> str:
        """Synchronous generation wrapper"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.provider.generate_content(prompt, max_tokens, temperature)
                    )
                    return future.result(timeout=30)
            else:
                # Use existing loop
                return loop.run_until_complete(
                    self.provider.generate_content(prompt, max_tokens, temperature)
                )
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise


class AIMetadataExtractor:
    """
    Use AI to extract ISO metadata with semantic understanding
    More accurate than regex patterns for complex documents
    """
    
    def __init__(self):
        self.llm = SimpleLLMClient()
    
    def extract_metadata(self, text_sample: str) -> Optional[Dict[str, str]]:
        """
        Extract ISO metadata using AI
        
        Args:
            text_sample: First ~2000 characters of document
            
        Returns:
            Dictionary with standard_number, year, title, category
        """
        prompt = f"""Analyze this ISO standard document excerpt and extract:
1. ISO standard number (e.g., "ISO 9001", "ISO 14001", "ISO/IEC 27001")
2. Publication year (e.g., "2015", "2013")
3. Full title (e.g., "Quality management systems — Requirements")
4. Category type (one of: QMS, EMS, ISMS, OHSMS, FSMS, EnMS, OTHER)

Document excerpt:
{text_sample[:2000]}

Respond in this exact format:
NUMBER: [ISO number]
YEAR: [4-digit year]
TITLE: [full title]
CATEGORY: [category code]
"""
        
        try:
            # Get AI response
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.1  # Low temperature for factual extraction
            )
            
            # Parse response
            metadata = self._parse_metadata_response(response)
            
            if metadata and self._validate_metadata(metadata):
                logger.info(f"AI extracted metadata: {metadata['standard_number']}:{metadata['year']}")
                return metadata
            else:
                logger.warning("AI metadata extraction failed validation")
                return None
                
        except Exception as e:
            logger.error(f"AI metadata extraction error: {e}")
            return None
    
    def _parse_metadata_response(self, response: str) -> Optional[Dict[str, str]]:
        """Parse AI response into structured metadata"""
        try:
            lines = response.strip().split('\n')
            metadata = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().upper()
                    value = value.strip()
                    
                    if key == 'NUMBER':
                        metadata['standard_number'] = value
                    elif key == 'YEAR':
                        metadata['year'] = value
                    elif key == 'TITLE':
                        metadata['title'] = value
                    elif key == 'CATEGORY':
                        metadata['category'] = value
            
            return metadata if len(metadata) == 4 else None
            
        except Exception as e:
            logger.error(f"Error parsing metadata response: {e}")
            return None
    
    def _validate_metadata(self, metadata: Dict[str, str]) -> bool:
        """Validate extracted metadata"""
        # Check ISO number format
        if not re.match(r'ISO(?:/IEC)?\s*\d+', metadata.get('standard_number', '')):
            return False
        
        # Check year format
        if not re.match(r'^\d{4}$', metadata.get('year', '')):
            return False
        
        # Check category
        valid_categories = ['QMS', 'EMS', 'ISMS', 'OHSMS', 'FSMS', 'EnMS', 'OTHER']
        if metadata.get('category') not in valid_categories:
            return False
        
        return True


class AIClauseDetector:
    """
    Use AI to detect clause boundaries with semantic understanding
    Better than regex for complex layouts and formatting
    """
    
    def __init__(self):
        self.llm = SimpleLLMClient()
    
    def detect_clause_boundaries(
        self, 
        text: str,
        context_window: int = 500
    ) -> List[Tuple[int, str, str]]:
        """
        Detect clause boundaries using AI
        
        Args:
            text: Full document text
            context_window: Characters to analyze at once
            
        Returns:
            List of (position, clause_number, clause_title)
        """
        # Split text into chunks
        chunks = self._create_overlapping_chunks(text, context_window)
        
        boundaries = []
        
        for i, chunk in enumerate(chunks):
            chunk_boundaries = self._detect_in_chunk(chunk, i * context_window)
            boundaries.extend(chunk_boundaries)
        
        # Remove duplicates and sort
        unique_boundaries = self._deduplicate_boundaries(boundaries)
        
        return unique_boundaries
    
    def _create_overlapping_chunks(self, text: str, size: int) -> List[str]:
        """Create overlapping text chunks for analysis"""
        chunks = []
        overlap = size // 4  # 25% overlap
        
        for i in range(0, len(text), size - overlap):
            chunks.append(text[i:i + size])
        
        return chunks
    
    def _detect_in_chunk(
        self, 
        chunk: str, 
        offset: int
    ) -> List[Tuple[int, str, str]]:
        """Detect clause boundaries in a text chunk"""
        prompt = f"""Analyze this ISO standard text and identify all clause headers.
A clause header has:
- A number (e.g., "4.1", "7.5.3", "10.2.1")
- A title immediately after the number

List all clause headers in this format:
[number] [title]

Text:
{chunk}

Respond with only the clause headers, one per line."""

        try:
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=300,
                temperature=0.1
            )
            
            # Parse response
            boundaries = []
            for line in response.strip().split('\n'):
                if line.strip():
                    match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', line.strip())
                    if match:
                        number = match.group(1)
                        title = match.group(2).strip()
                        # Find position in chunk
                        pos = chunk.find(f"{number} {title}")
                        if pos >= 0:
                            boundaries.append((offset + pos, number, title))
            
            return boundaries
            
        except Exception as e:
            logger.error(f"Error detecting clauses in chunk: {e}")
            return []
    
    def _deduplicate_boundaries(
        self, 
        boundaries: List[Tuple[int, str, str]]
    ) -> List[Tuple[int, str, str]]:
        """Remove duplicate boundaries"""
        seen = set()
        unique = []
        
        for pos, number, title in sorted(boundaries, key=lambda x: x[0]):
            key = (number, title)
            if key not in seen:
                seen.add(key)
                unique.append((pos, number, title))
        
        return unique


class AIRequirementClassifier:
    """
    Use AI to classify clauses as requirements vs guidance
    Context-aware, better than keyword matching
    """
    
    def __init__(self):
        self.llm = SimpleLLMClient()
    
    def classify_clause(self, clause: ExtractedClause) -> ClauseType:
        """
        Classify clause type using AI
        
        Args:
            clause: ExtractedClause object
            
        Returns:
            ClauseType (REQUIREMENT, GUIDANCE, NOTE, EXAMPLE)
        """
        # Quick checks for obvious cases
        if clause.content.upper().startswith('NOTE'):
            return ClauseType.NOTE
        if clause.content.upper().startswith('EXAMPLE'):
            return ClauseType.EXAMPLE
        
        # Use AI for nuanced classification
        prompt = f"""Analyze this ISO standard clause and classify it.

Clause {clause.clause_number}: {clause.title}

Content:
{clause.content[:500]}

Classification rules:
- REQUIREMENT: Contains mandatory obligations (uses "shall", "must")
- GUIDANCE: Contains recommendations or optional practices (uses "should", "may", "can")
- NOTE: Additional information or clarification
- EXAMPLE: Illustrative content

Respond with only one word: REQUIREMENT, GUIDANCE, NOTE, or EXAMPLE"""

        try:
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=10,
                temperature=0.1
            )
            
            # Parse response
            classification = response.strip().upper()
            
            if 'REQUIREMENT' in classification:
                return ClauseType.REQUIREMENT
            elif 'GUIDANCE' in classification:
                return ClauseType.GUIDANCE
            elif 'NOTE' in classification:
                return ClauseType.NOTE
            elif 'EXAMPLE' in classification:
                return ClauseType.EXAMPLE
            else:
                # Default to guidance if unclear
                return ClauseType.GUIDANCE
                
        except Exception as e:
            logger.error(f"Error classifying clause {clause.clause_number}: {e}")
            # Fallback to keyword-based classification
            return self._fallback_classification(clause)
    
    def _fallback_classification(self, clause: ExtractedClause) -> ClauseType:
        """Fallback to simple keyword matching"""
        content_lower = clause.content.lower()
        
        if 'shall' in content_lower:
            return ClauseType.REQUIREMENT
        elif any(word in content_lower for word in ['should', 'may', 'can', 'could']):
            return ClauseType.GUIDANCE
        else:
            return ClauseType.GUIDANCE


class AITemplateGenerator:
    """
    Use AI to generate professional Jinja2 templates from clauses
    Much better than basic string replacement
    """
    
    def __init__(self):
        self.llm = SimpleLLMClient()
    
    def generate_template(
        self, 
        clause: ExtractedClause,
        industry: Optional[str] = None
    ) -> str:
        """
        Generate a Jinja2 template using AI
        
        Args:
            clause: ExtractedClause object
            industry: Optional industry for customization
            
        Returns:
            Jinja2 template string
        """
        industry_context = f" for {industry} industry" if industry else ""
        
        prompt = f"""Create a professional Jinja2 template for this ISO requirement{industry_context}.

Clause {clause.clause_number}: {clause.title}

Original requirement:
{clause.content}

Instructions:
1. Replace generic terms with Jinja2 variables:
   - "the organization" → {{{{ company_name }}}}
   - Specific values → {{{{ variable_name }}}}
2. Add conditional sections with {{% if industry %}} blocks
3. Include industry-specific guidance
4. Add placeholders for company-specific details
5. Keep professional ISO documentation tone
6. Include comments for customization hints

Generate the complete template in Markdown format."""

        try:
            template = self.llm.generate(
                prompt=prompt,
                max_tokens=800,
                temperature=0.5  # Moderate creativity
            )
            
            # Clean up and validate template
            template = self._clean_template(template)
            
            if self._validate_template(template):
                return template
            else:
                logger.warning(f"Generated template for {clause.clause_number} failed validation")
                return self._create_basic_template(clause)
                
        except Exception as e:
            logger.error(f"Error generating template for {clause.clause_number}: {e}")
            return self._create_basic_template(clause)
    
    def _clean_template(self, template: str) -> str:
        """Clean up AI-generated template"""
        # Remove code block markers if present
        template = re.sub(r'^```(?:markdown|jinja2)?\n', '', template)
        template = re.sub(r'\n```$', '', template)
        
        # Ensure proper Jinja2 syntax
        template = template.replace('{{ ', '{{ ')
        template = template.replace(' }}', ' }}')
        
        return template.strip()
    
    def _validate_template(self, template: str) -> bool:
        """Validate Jinja2 template syntax"""
        # Check for balanced Jinja2 tags
        open_vars = template.count('{{')
        close_vars = template.count('}}')
        
        open_blocks = template.count('{%')
        close_blocks = template.count('%}')
        
        return open_vars == close_vars and open_blocks == close_blocks
    
    def _create_basic_template(self, clause: ExtractedClause) -> str:
        """Create a basic fallback template"""
        content = clause.content
        content = content.replace("the organization", "{{ company_name }}")
        content = content.replace("The organization", "{{ company_name }}")
        
        return f"""# {clause.clause_number} {clause.title}

{content}

{{% if industry %}}
## Industry-Specific Considerations for {{{{ industry }}}}

*This section should be customized based on {{{{ industry }}}} requirements.*
{{% endif %}}

---
*Template generated from ISO standard. Review and customize as needed.*
"""


class AIISOParser:
    """
    Main AI-powered ISO parser that coordinates all AI components
    """
    
    def __init__(self):
        self.metadata_extractor = AIMetadataExtractor()
        self.clause_detector = AIClauseDetector()
        self.requirement_classifier = AIRequirementClassifier()
        self.template_generator = AITemplateGenerator()
        
        logger.info("AI ISO Parser initialized with TinyLlama")
    
    def enhance_metadata_extraction(
        self, 
        text: str, 
        fallback_metadata: Optional[ISOMetadata]
    ) -> ISOMetadata:
        """
        Extract or enhance metadata using AI
        
        Args:
            text: Document text
            fallback_metadata: Metadata from regex extraction (fallback)
            
        Returns:
            ISOMetadata object (AI-extracted or fallback)
        """
        logger.info("Attempting AI metadata extraction...")
        
        ai_metadata = self.metadata_extractor.extract_metadata(text)
        
        if ai_metadata:
            # Convert to ISOMetadata object
            from datetime import datetime
            return ISOMetadata(
                standard_number=ai_metadata['standard_number'],
                year=ai_metadata['year'],
                title=ai_metadata['title'],
                category=ai_metadata['category'],
                total_pages=text.count('--- Page'),
                extraction_date=datetime.now().isoformat()
            )
        elif fallback_metadata:
            logger.info("AI extraction failed, using regex fallback")
            return fallback_metadata
        else:
            raise ValueError("Both AI and regex metadata extraction failed")
    
    def enhance_clause_detection(
        self,
        text: str,
        fallback_clauses: List[ExtractedClause]
    ) -> List[ExtractedClause]:
        """
        Enhance clause detection with AI
        
        Args:
            text: Document text
            fallback_clauses: Clauses from regex detection
            
        Returns:
            List of ExtractedClause objects (AI-enhanced or fallback)
        """
        logger.info("Attempting AI clause boundary detection...")
        
        try:
            # For now, use fallback and enhance classification
            # Full AI boundary detection is expensive with TinyLlama
            enhanced_clauses = []
            
            for clause in fallback_clauses:
                # Use AI to reclassify
                ai_type = self.requirement_classifier.classify_clause(clause)
                
                # Update clause type
                clause.clause_type = ai_type
                enhanced_clauses.append(clause)
            
            logger.info(f"AI enhanced classification for {len(enhanced_clauses)} clauses")
            return enhanced_clauses
            
        except Exception as e:
            logger.error(f"AI clause enhancement error: {e}")
            return fallback_clauses
    
    def generate_smart_templates(
        self,
        clauses: List[ExtractedClause],
        industry: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate templates for all requirement clauses using AI
        
        Args:
            clauses: List of ExtractedClause objects
            industry: Optional industry for customization
            
        Returns:
            Dictionary mapping clause_number to template content
        """
        logger.info(f"Generating AI templates for {len(clauses)} clauses...")
        
        templates = {}
        requirement_clauses = [c for c in clauses if c.clause_type == ClauseType.REQUIREMENT]
        
        for i, clause in enumerate(requirement_clauses, 1):
            logger.info(f"Generating template {i}/{len(requirement_clauses)}: {clause.clause_number}")
            
            try:
                template = self.template_generator.generate_template(clause, industry)
                templates[clause.clause_number] = template
            except Exception as e:
                logger.error(f"Error generating template for {clause.clause_number}: {e}")
        
        logger.info(f"Generated {len(templates)} AI-powered templates")
        return templates


if __name__ == "__main__":
    # Test the AI parser
    logging.basicConfig(level=logging.INFO)
    
    print("AI-Powered ISO Parser")
    print("=" * 50)
    print("\nThis module uses TinyLlama to enhance ISO import:")
    print("  • Semantic metadata extraction")
    print("  • Context-aware clause classification")
    print("  • Smart template generation")
    print("\nRequires: Ollama running with TinyLlama model")
    print(f"LLM URL: {settings.LOCAL_LLM_URL}")
    print(f"Model: {settings.LOCAL_LLM_MODEL}")
