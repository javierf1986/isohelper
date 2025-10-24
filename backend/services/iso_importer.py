"""
Universal ISO Importer - Extract text and structure from ISO standard documents

This module provides functionality to:
1. Extract text from PDF and DOCX files
2. Clean and normalize extracted text
3. Detect clause structure and hierarchy
4. Identify clause numbers and titles
5. Classify content as requirements vs guidance
6. Prepare data for database import

Supports any ISO standard format (9001, 14001, 27001, 45001, etc.)
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)


class ClauseType(str, Enum):
    """Types of ISO clauses"""
    REQUIREMENT = "requirement"  # Mandatory "shall" statements
    GUIDANCE = "guidance"  # Optional "should" or explanatory text
    DEFINITION = "definition"  # Terms and definitions
    NOTE = "note"  # Additional information
    EXAMPLE = "example"  # Illustrative examples


@dataclass
class ExtractedClause:
    """Represents a clause extracted from an ISO document"""
    clause_number: str  # e.g., "4.1", "7.5.3"
    title: str  # Clause title
    content: str  # Full text content
    clause_type: ClauseType
    level: int  # Hierarchy level (1 = top, 2 = sub, 3 = sub-sub)
    parent_number: Optional[str] = None  # Parent clause number
    page_number: Optional[int] = None  # Source page
    
    @property
    def is_requirement(self) -> bool:
        """Check if clause contains requirements"""
        return self.clause_type == ClauseType.REQUIREMENT


@dataclass
class ISOMetadata:
    """Metadata extracted from ISO document"""
    standard_number: str  # e.g., "ISO 9001"
    year: str  # e.g., "2015"
    title: str  # Full standard title
    category: str  # QMS, EMS, ISMS, etc.
    total_pages: int
    extraction_date: str
    

class ISOTextExtractor:
    """Extract and clean text from ISO documents"""
    
    def __init__(self):
        self.clause_pattern = re.compile(
            r'^(\d+(?:\.\d+)*)\s+(.+?)$',  # Matches "4.1 Title" or "7.5.3.1 Title"
            re.MULTILINE
        )
        
    def extract_from_pdf(self, file_path: Path) -> Tuple[str, int]:
        """
        Extract text from PDF file with improved text flow handling
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (extracted_text, page_count)
        """
        try:
            full_text = []
            
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                logger.info(f"Extracting text from {page_count} pages in {file_path.name}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text without strict layout to avoid mid-word line breaks
                    # This allows text to flow naturally instead of preserving column positions
                    text = page.extract_text(layout=False)
                    
                    if text:
                        # Add page marker for reference
                        full_text.append(f"\n--- Page {page_num} ---\n")
                        full_text.append(text)
                        
                logger.info(f"Successfully extracted {len(''.join(full_text))} characters")
                
            return ''.join(full_text), page_count
            
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    def extract_from_docx(self, file_path: Path) -> Tuple[str, int]:
        """
        Extract text from DOCX file
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Tuple of (extracted_text, paragraph_count)
        """
        try:
            doc = Document(str(file_path))
            paragraphs = []
            
            logger.info(f"Extracting text from {len(doc.paragraphs)} paragraphs in {file_path.name}")
            
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
                    
            full_text = '\n'.join(paragraphs)
            logger.info(f"Successfully extracted {len(full_text)} characters")
            
            return full_text, len(paragraphs)
            
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
            raise
    
    def extract_from_txt(self, file_path: Path) -> Tuple[str, int]:
        """
        Extract text from TXT file (for testing)
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Tuple of (extracted_text, line_count)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            line_count = len([line for line in text.split('\n') if line.strip()])
            logger.info(f"Successfully loaded {len(text)} characters from {file_path.name}")
            
            return text, line_count
            
        except Exception as e:
            logger.error(f"Error reading TXT file: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text while preserving structure
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove page markers but keep line structure
        text = re.sub(r'--- Page \d+ ---\s*', '', text)
        
        # Remove table of contents entries (lines with dots leading to page numbers)
        # e.g., "4.1 Context..................... 12"
        text = re.sub(r'^.+?\.{3,}\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove figure captions and references
        text = re.sub(r'^\s*Figura\s+\d+\s*[—–-].*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*Figure\s+\d+\s*[—–-].*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*Tabla\s+\d+\s*[—–-].*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*Table\s+\d+\s*[—–-].*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'\(véase\s+[Ff]igura\s+\d+\)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(see\s+[Ff]igure\s+\d+\)', '', text, flags=re.IGNORECASE)
        
        # Remove annex headers and references
        text = re.sub(r'^\s*Anexo\s+[A-Z]\s+\(.*?\).*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*Annex\s+[A-Z]\s+\(.*?\).*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove bibliography references
        text = re.sub(r'^\s*Bibliograf[ií]a\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^\s*Bibliography\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Fix hyphenated words split across lines (e.g., "conside-\nraciones" -> "consideraciones")
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Join lines that end without punctuation and continue on next line
        # This fixes text flow issues from PDFs (e.g., "la calidad\nincluidas" -> "la calidad incluidas")
        text = re.sub(r'([a-záéíóúñ])\s*\n\s*([a-záéíóúñ])', r'\1 \2', text, flags=re.IGNORECASE)
        
        # Remove common ISO PDF headers/footers
        text = re.sub(r'© ISO \d{4}[^\n]*', '', text)  # Copyright lines
        text = re.sub(r'ISO \d+:\d{4}[^\n]{0,50}traducción oficial[^\n]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'PDF\s*[–-]\s*Exoneración de responsabilidad[^\n]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Traducción oficial/Official translation/Traduction officielle[^\n]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Todos los derechos reservados[^\n]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'All rights reserved[^\n]*', '', text, flags=re.IGNORECASE)
        
        # Remove standalone page numbers at line start or end
        text = re.sub(r'^\s*\d{1,3}\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*[ivxlcdm]+\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)  # Roman numerals
        
        # Remove page number suffixes from clause titles (e.g., "4.1 Title 12" -> "4.1 Title")
        # This pattern finds clause numbers followed by text and trailing page numbers
        text = re.sub(r'(\d+(?:\.\d+)*\s+[^\n]+?)\s+\d{1,3}\s*$', r'\1', text, flags=re.MULTILINE)
        
        # Normalize multiple blank lines to double newline
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove trailing whitespace from each line but keep newlines
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove leading/trailing whitespace from whole text
        text = text.strip()
        
        return text
    
    def extract_metadata_from_text(self, text: str) -> Optional[ISOMetadata]:
        """
        Extract ISO metadata from document text
        
        Args:
            text: Full document text
            
        Returns:
            ISOMetadata object or None if not found
        """
        # Pattern for ISO standard number and year
        # Examples: "ISO 9001:2015", "ISO/IEC 27001:2013", "ISO 14001:2015"
        iso_pattern = re.compile(r'(ISO(?:/IEC)?\s*\d+):(\d{4})')
        match = iso_pattern.search(text)
        
        if not match:
            logger.warning("Could not extract ISO metadata from text")
            return None
            
        standard_number = match.group(1).replace(' ', ' ')  # Normalize spacing
        year = match.group(2)
        
        # Try to extract title (usually follows the ISO number)
        title_pattern = re.compile(
            rf'{re.escape(standard_number)}:{year}\s*\n?\s*(.+?)(?:\n|$)',
            re.MULTILINE
        )
        title_match = title_pattern.search(text)
        title = title_match.group(1).strip() if title_match else "Unknown Title"
        
        # Determine category based on standard number
        category = self._determine_category(standard_number)
        
        from datetime import datetime
        
        return ISOMetadata(
            standard_number=standard_number,
            year=year,
            title=title,
            category=category,
            total_pages=text.count('--- Page'),
            extraction_date=datetime.now().isoformat()
        )
    
    def _determine_category(self, standard_number: str) -> str:
        """Determine ISO category from standard number"""
        if '9001' in standard_number:
            return 'QMS'  # Quality Management System
        elif '14001' in standard_number:
            return 'EMS'  # Environmental Management System
        elif '27001' in standard_number:
            return 'ISMS'  # Information Security Management System
        elif '45001' in standard_number:
            return 'OHSMS'  # Occupational Health and Safety Management System
        elif '22000' in standard_number:
            return 'FSMS'  # Food Safety Management System
        elif '50001' in standard_number:
            return 'EnMS'  # Energy Management System
        else:
            return 'OTHER'


class ISOClauseDetector:
    """Detect and parse ISO clause structure"""
    
    def __init__(self):
        # Pattern for clause headers: "4.1 Title", "7.5.3.1 Title"
        # Must be at start of line with optional whitespace
        # Captures only up to first sentence/reasonable title length
        self.clause_header_pattern = re.compile(
            r'^\s*(\d+(?:\.\d+)*)\s+([A-ZÁÉÍÓÚÑ][^\n]{2,150}?)(?:\s+[A-Z][a-záéíóúñ]|\.|$)',
            re.MULTILINE
        )
        
        # Backup pattern if first doesn't work well - captures everything on the line
        self.clause_header_simple_pattern = re.compile(
            r'^\s*(\d+(?:\.\d+)*)\s+(.+?)$',
            re.MULTILINE
        )
        
        # Pattern for "shall" requirements (debe in Spanish, shall in English)
        self.requirement_pattern = re.compile(r'\b(shall|debe|deben)\b', re.IGNORECASE)
        
        # Pattern for guidance (should, may, can)
        self.guidance_pattern = re.compile(r'\b(should|may|can|could|debería|puede|pueden)\b', re.IGNORECASE)
        
        # Pattern for notes
        self.note_pattern = re.compile(r'^NOTE\s+\d*:?|^NOTA\s+\d*:?', re.MULTILINE | re.IGNORECASE)
        
        # Pattern for examples
        self.example_pattern = re.compile(r'^EXAMPLE\s+\d*:?|^EJEMPLO\s+\d*:?', re.MULTILINE | re.IGNORECASE)
    
    def detect_clauses(self, text: str) -> List[ExtractedClause]:
        """
        Detect all clauses in the document
        
        Args:
            text: Full document text
            
        Returns:
            List of ExtractedClause objects
        """
        clauses = []
        
        # Find all clause headers with their positions
        matches = list(self.clause_header_pattern.finditer(text))
        
        logger.info(f"Found {len(matches)} potential clause headers")
        
        for i, match in enumerate(matches):
            clause_number = match.group(1)
            clause_title = match.group(2).strip()
            
            # Skip if clause number looks like it's from a table or list (too many dots)
            if clause_number.count('.') > 4:
                continue
            
            # Skip if it's just a number without proper formatting
            if len(clause_number) == 1 and not clause_title:
                continue
            
            # Clean up the clause title
            clause_title = self._clean_clause_title(clause_title)
            
            # Skip if title is too short or looks like junk
            if len(clause_title) < 3 or self._is_junk_clause(clause_title):
                continue
            
            # Skip if title is all uppercase and short (likely a section header, not a clause)
            if len(clause_title) < 30 and clause_title.isupper() and clause_number in ['1', '2', '3']:
                # Allow it - main sections can be uppercase
                pass
            
            # Get clause content (text between this header and next header)
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start_pos:end_pos].strip()
            
            # Clean the content
            content = self._clean_clause_content(content)
            
            # Skip if content is empty or too short (likely not a real clause)
            if len(content) < 20:
                continue
            
            # Skip if content looks like table data (lots of numbers, minimal text)
            words = re.findall(r'\b[a-záéíóúñA-ZÁÉÍÓÚÑ]{3,}\b', content)
            numbers = re.findall(r'\b\d+\b', content)
            if len(numbers) > len(words) * 2:  # More than 2x as many numbers as words
                continue
            
            # Determine clause type
            clause_type = self._classify_clause(content)
            
            # Calculate hierarchy level
            level = clause_number.count('.') + 1
            
            # Determine parent clause number
            parent_number = self._get_parent_number(clause_number)
            
            clause = ExtractedClause(
                clause_number=clause_number,
                title=clause_title,
                content=content,
                clause_type=clause_type,
                level=level,
                parent_number=parent_number
            )
            
            clauses.append(clause)
            
        logger.info(f"Successfully detected {len(clauses)} valid clauses")
        return clauses
    
    def _clean_clause_title(self, title: str) -> str:
        """Clean clause title by removing page numbers and junk"""
        # Remove trailing page numbers (e.g., "Title 12" -> "Title")
        title = re.sub(r'\s+\d{1,3}\s*$', '', title)
        
        # If title is too long (>150 chars), try to extract just the heading part
        if len(title) > 150:
            # Try to find the end of the title (usually before "La organización", "El", "Los", etc.)
            spanish_content_start = re.search(r'\s+(La organización|El|Los|Las|Una|Un|Este|Esta|Cuando|Para)\s+', title)
            english_content_start = re.search(r'\s+(The organization|The|This|When|For)\s+', title)
            
            if spanish_content_start:
                title = title[:spanish_content_start.start()].strip()
            elif english_content_start:
                title = title[:english_content_start.start()].strip()
            else:
                # Just take first 150 characters
                title = title[:150].strip()
        
        # Remove trailing dots and whitespace
        title = title.rstrip('. ')
        
        # Remove any remaining copyright or header fragments
        title = re.sub(r'©\s*ISO.*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'traducción oficial.*', '', title, flags=re.IGNORECASE)
        
        return title.strip()
    
    def _clean_clause_content(self, content: str) -> str:
        """Clean clause content by removing headers, footers, tables, and junk"""
        # Remove copyright notices
        content = re.sub(r'©\s*ISO\s*\d{4}[^\n]*\n?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'ISO\s*\d+:\d{4}\s*\(traducción oficial\)[^\n]*\n?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'PDF\s*[–-]\s*Exoneración[^\n]+\n?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Traducción oficial/Official translation[^\n]*\n?', '', content, flags=re.IGNORECASE)
        
        # Remove figure and table references
        content = re.sub(r'^\s*Figura\s+\d+\s*[—–-].*$', '', content, flags=re.MULTILINE | re.IGNORECASE)
        content = re.sub(r'^\s*Figure\s+\d+\s*[—–-].*$', '', content, flags=re.MULTILINE | re.IGNORECASE)
        content = re.sub(r'^\s*Tabla\s+\d+\s*[—–-].*$', '', content, flags=re.MULTILINE | re.IGNORECASE)
        content = re.sub(r'^\s*Table\s+\d+\s*[—–-].*$', '', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove table of contents entries with dots
        content = re.sub(r'^.+?\.{3,}\s*\d+\s*$', '', content, flags=re.MULTILINE)
        
        # Remove annex headers that might appear in content
        content = re.sub(r'Anexo\s+[A-Z]\s+\(inform\s*ativo\)[^\n]*\n?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Annex\s+[A-Z]\s+\(informative\)[^\n]*\n?', '', content, flags=re.IGNORECASE)
        
        # Remove standalone page numbers
        content = re.sub(r'^\s*\d{1,3}\s*\n', '', content, flags=re.MULTILINE)
        
        # Remove lines that are mostly numbers (likely table data)
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Count alphanumeric words vs pure numbers
            words = re.findall(r'\b[a-záéíóúñA-ZÁÉÍÓÚÑ]+\b', line)
            numbers = re.findall(r'\b\d+\b', line)
            # Keep line if it has more words than numbers, or at least some words
            if len(words) > 0 and (len(words) >= len(numbers) or len(line) > 50):
                cleaned_lines.append(line)
        content = '\n'.join(cleaned_lines)
        
        # Remove multiple newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
    
    def _is_junk_clause(self, title: str) -> bool:
        """Check if clause title looks like junk (headers, footers, tables, figures, etc.)"""
        junk_patterns = [
            r'^©',
            r'traducción oficial',
            r'official translation',
            r'traduction officielle',
            r'todos los derechos',
            r'all rights reserved',
            r'exoneración',
            r'disclaimer',
            r'^pdf\b',
            r'^\s*tabla\s+\d+',  # Table references
            r'^\s*table\s+\d+',
            r'^\s*figura\s+\d+',  # Figure references
            r'^\s*figure\s+\d+',
            r'^\s*anexo\s+[a-z]',  # Annex headers
            r'^\s*annex\s+[a-z]',
            r'^\s*bibliograf',  # Bibliography
            r'^\s*bibliography',
            r'\.{3,}',  # Lines with multiple dots (TOC entries)
            r'^\s*inform\s*ativo',  # Informative annex marker
            r'^\s*informative',
            r'^\s*normativo',  # Normative annex marker
            r'^\s*normative',
        ]
        
        title_lower = title.lower()
        for pattern in junk_patterns:
            if re.search(pattern, title_lower):
                return True
        
        return False
    
    def _classify_clause(self, content: str) -> ClauseType:
        """Classify clause as requirement, guidance, note, or example"""
        
        # Check for notes
        if self.note_pattern.search(content):
            return ClauseType.NOTE
        
        # Check for examples
        if self.example_pattern.search(content):
            return ClauseType.EXAMPLE
        
        # Check for requirements (contains "shall")
        if self.requirement_pattern.search(content):
            return ClauseType.REQUIREMENT
        
        # Check for guidance (contains "should", "may", etc.)
        if self.guidance_pattern.search(content):
            return ClauseType.GUIDANCE
        
        # Default to guidance if unclear
        return ClauseType.GUIDANCE
    
    def _get_parent_number(self, clause_number: str) -> Optional[str]:
        """Get parent clause number from child number"""
        parts = clause_number.split('.')
        if len(parts) > 1:
            return '.'.join(parts[:-1])
        return None
    
    def filter_by_level(self, clauses: List[ExtractedClause], level: int) -> List[ExtractedClause]:
        """Filter clauses by hierarchy level"""
        return [c for c in clauses if c.level == level]
    
    def filter_requirements_only(self, clauses: List[ExtractedClause]) -> List[ExtractedClause]:
        """Filter to get only requirement clauses"""
        return [c for c in clauses if c.is_requirement]


class UniversalISOImporter:
    """
    Main importer class that orchestrates the import process
    
    Usage:
        importer = UniversalISOImporter()
        result = importer.import_from_file(Path("ISO_9001_2015.pdf"))
        
        # Access extracted data
        metadata = result["metadata"]
        clauses = result["clauses"]
        requirements = result["requirements_only"]
    """
    
    def __init__(self):
        self.text_extractor = ISOTextExtractor()
        self.clause_detector = ISOClauseDetector()
    
    def import_from_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Import ISO standard from PDF or DOCX file
        
        Args:
            file_path: Path to ISO document
            
        Returns:
            Dictionary containing:
                - metadata: ISOMetadata object
                - raw_text: Full extracted text
                - clauses: List of ExtractedClause objects
                - requirements_only: List of requirement clauses only
                - statistics: Import statistics
        """
        logger.info(f"Starting import of {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract text based on file type
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            raw_text, page_count = self.text_extractor.extract_from_pdf(file_path)
        elif suffix in ['.docx', '.doc']:
            raw_text, page_count = self.text_extractor.extract_from_docx(file_path)
        elif suffix == '.txt':
            raw_text, page_count = self.text_extractor.extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}. Supported: .pdf, .docx, .doc, .txt")
        
        # Clean text
        clean_text = self.text_extractor.clean_text(raw_text)
        
        # Extract metadata
        metadata = self.text_extractor.extract_metadata_from_text(raw_text)
        
        # Detect clauses
        clauses = self.clause_detector.detect_clauses(clean_text)
        
        # Filter requirements only
        requirements = self.clause_detector.filter_requirements_only(clauses)
        
        # Calculate statistics
        statistics = {
            'total_clauses': len(clauses),
            'requirements': len(requirements),
            'guidance': len([c for c in clauses if c.clause_type == ClauseType.GUIDANCE]),
            'notes': len([c for c in clauses if c.clause_type == ClauseType.NOTE]),
            'examples': len([c for c in clauses if c.clause_type == ClauseType.EXAMPLE]),
            'max_level': max([c.level for c in clauses]) if clauses else 0,
            'character_count': len(clean_text),
            'pages': page_count
        }
        
        logger.info(f"Import complete: {statistics['total_clauses']} clauses detected")
        
        return {
            'metadata': metadata,
            'raw_text': raw_text,
            'clean_text': clean_text,
            'clauses': clauses,
            'requirements_only': requirements,
            'statistics': statistics,
            'file_path': str(file_path)
        }
    
    def export_to_database_format(self, import_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert import result to database-ready format
        
        Args:
            import_result: Output from import_from_file()
            
        Returns:
            Dictionary ready for database insertion
        """
        metadata = import_result['metadata']
        clauses = import_result['clauses']
        
        if not metadata:
            raise ValueError("No metadata found in import result")
        
        # Prepare standard data
        standard_data = {
            'number': metadata.standard_number,
            'year': metadata.year,
            'title': metadata.title,
            'category': metadata.category,
            'description': f"{metadata.title} - Imported on {metadata.extraction_date}",
            'version': f"{metadata.year}",
            'is_active': True
        }
        
        # Prepare clause data
        clause_data = []
        for clause in clauses:
            clause_dict = {
                'number': clause.clause_number,
                'title': clause.title,
                'content': clause.content,
                'level': clause.level,
                'parent_number': clause.parent_number,
                'clause_type': clause.clause_type.value,
                'is_requirement': clause.is_requirement
            }
            clause_data.append(clause_dict)
        
        return {
            'standard': standard_data,
            'clauses': clause_data,
            'statistics': import_result['statistics']
        }


if __name__ == "__main__":
    # Test the importer
    logging.basicConfig(level=logging.INFO)
    
    print("Universal ISO Importer - Test Module")
    print("=" * 50)
    print("\nThis module provides text extraction from ISO PDF/DOCX files.")
    print("It can detect clause structure, identify requirements, and prepare data for import.")
    print("\nUsage:")
    print("  importer = UniversalISOImporter()")
    print("  result = importer.import_from_file(Path('ISO_9001_2015.pdf'))")
    print("\nSupported formats: PDF, DOCX")
    print("Supported standards: Any ISO standard (9001, 14001, 27001, etc.)")
