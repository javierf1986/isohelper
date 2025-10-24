"""
Document Parsing Service
Extracts text from PDF, DOCX, and TXT files for gap analysis
"""

import os
from typing import Dict, Optional, Any, List
from pathlib import Path


class DocumentParsingError(Exception):
    """Custom exception for document parsing errors"""
    pass


class DocumentParser:
    """Service for extracting text from various document formats"""
    
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt', '.doc']
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    
    @staticmethod
    def parse_document(file_path: str) -> Dict[str, Any]:
        """
        Parse document and extract text content
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing:
                - text: Extracted text content
                - page_count: Number of pages (if applicable)
                - word_count: Approximate word count
                - char_count: Character count
                - file_size: File size in bytes
                - format: Document format
        """
        if not os.path.exists(file_path):
            raise DocumentParsingError(f"File not found: {file_path}")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > DocumentParser.MAX_FILE_SIZE:
            raise DocumentParsingError(f"File too large. Max size: {DocumentParser.MAX_FILE_SIZE / 1024 / 1024}MB")
        
        # Determine file format
        file_extension = Path(file_path).suffix.lower()
        if file_extension not in DocumentParser.SUPPORTED_FORMATS:
            raise DocumentParsingError(f"Unsupported format: {file_extension}")
        
        # Parse based on format
        try:
            if file_extension == '.pdf':
                result = DocumentParser._parse_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                result = DocumentParser._parse_docx(file_path)
            elif file_extension == '.txt':
                result = DocumentParser._parse_txt(file_path)
            else:
                raise DocumentParsingError(f"Format not implemented: {file_extension}")
            
            # Add metadata
            result['file_size'] = file_size
            result['format'] = file_extension[1:].upper()
            result['char_count'] = len(result['text'])
            result['word_count'] = len(result['text'].split())
            
            return result
            
        except Exception as e:
            raise DocumentParsingError(f"Error parsing document: {str(e)}")
    
    @staticmethod
    def _parse_pdf(file_path: str) -> Dict[str, Any]:
        """Extract text from PDF file"""
        try:
            import PyPDF2
        except ImportError:
            raise DocumentParsingError("PyPDF2 not installed. Install with: pip install PyPDF2")
        
        text_content = []
        page_count = 0
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page_num in range(page_count):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            full_text = '\n\n'.join(text_content)
            
            if not full_text.strip():
                raise DocumentParsingError("No text could be extracted from PDF. It may be scanned/image-based.")
            
            return {
                'text': full_text,
                'page_count': page_count
            }
            
        except Exception as e:
            raise DocumentParsingError(f"PDF parsing error: {str(e)}")
    
    @staticmethod
    def _parse_docx(file_path: str) -> Dict[str, Any]:
        """Extract text from DOCX file"""
        try:
            from docx import Document
        except ImportError:
            raise DocumentParsingError("python-docx not installed. Install with: pip install python-docx")
        
        try:
            doc = Document(file_path)
            
            # Extract paragraphs
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            
            # Extract tables
            table_text = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text for cell in row.cells]
                    table_text.append(' | '.join(row_text))
            
            # Combine all text
            all_text = '\n\n'.join(paragraphs)
            if table_text:
                all_text += '\n\n=== TABLES ===\n\n' + '\n'.join(table_text)
            
            if not all_text.strip():
                raise DocumentParsingError("No text could be extracted from DOCX file.")
            
            return {
                'text': all_text,
                'page_count': len(doc.sections)  # Approximate
            }
            
        except Exception as e:
            raise DocumentParsingError(f"DOCX parsing error: {str(e)}")
    
    @staticmethod
    def _parse_txt(file_path: str) -> Dict[str, Any]:
        """Extract text from TXT file"""
        try:
            # Try UTF-8 first, fall back to other encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text = file.read()
                    
                    if not text.strip():
                        raise DocumentParsingError("TXT file is empty.")
                    
                    return {
                        'text': text,
                        'page_count': 1
                    }
                except UnicodeDecodeError:
                    continue
            
            raise DocumentParsingError("Could not decode TXT file with any common encoding.")
            
        except Exception as e:
            raise DocumentParsingError(f"TXT parsing error: {str(e)}")
    
    @staticmethod
    def validate_content(text: str, min_words: int = 100) -> bool:
        """
        Validate that extracted content is sufficient for analysis
        
        Args:
            text: Extracted text
            min_words: Minimum word count required
            
        Returns:
            True if content is valid, raises exception otherwise
        """
        if not text or not text.strip():
            raise DocumentParsingError("No content extracted from document.")
        
        word_count = len(text.split())
        if word_count < min_words:
            raise DocumentParsingError(
                f"Document too short for analysis. Found {word_count} words, need at least {min_words}."
            )
        
        return True
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks for AI processing
        
        Args:
            text: Full text to chunk
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within last 200 chars
                search_start = max(start, end - 200)
                last_period = text.rfind('.', search_start, end)
                last_newline = text.rfind('\n\n', search_start, end)
                
                break_point = max(last_period, last_newline)
                if break_point > start:
                    end = break_point + 1
            
            chunks.append(text[start:end])
            start = end - overlap if end < len(text) else end
        
        return chunks
    
    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, Any]:
        """Extract basic file metadata without parsing content"""
        if not os.path.exists(file_path):
            raise DocumentParsingError(f"File not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        file_size = os.path.getsize(file_path)
        file_name = Path(file_path).name
        
        return {
            'file_name': file_name,
            'file_size': file_size,
            'format': file_extension[1:].upper() if file_extension else 'UNKNOWN',
            'extension': file_extension,
            'is_supported': file_extension in DocumentParser.SUPPORTED_FORMATS
        }
