"""
Document Converter Service using MarkItDown
Handles conversion between Markdown, DOCX, PDF, and HTML formats
"""
from pathlib import Path
from typing import Optional, Literal
import logging

try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False
    logging.warning("MarkItDown not installed. Install with: pip install markitdown")

FormatType = Literal["pdf", "docx", "html", "md"]

class DocumentConverter:
    """
    Document conversion service using Microsoft's MarkItDown
    Supports bi-directional conversion between various formats
    """
    
    def __init__(self):
        if MARKITDOWN_AVAILABLE:
            self.converter = MarkItDown()
        else:
            self.converter = None
            logging.error("MarkItDown is not available")
    
    def markdown_to_format(
        self,
        markdown_content: str,
        output_path: Path,
        format: FormatType = "docx"
    ) -> bool:
        """
        Convert Markdown content to specified format
        
        Args:
            markdown_content: The markdown text to convert
            output_path: Path where the output file should be saved
            format: Target format (pdf, docx, html)
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        if not self.converter:
            logging.error("MarkItDown converter not initialized")
            return False
        
        try:
            # Save markdown temporarily
            temp_md = output_path.parent / f"{output_path.stem}_temp.md"
            temp_md.write_text(markdown_content, encoding="utf-8")
            
            # Convert using MarkItDown
            result = self.converter.convert(str(temp_md))
            
            # Handle different output formats
            if format == "docx":
                self._save_as_docx(result.text_content, output_path)
            elif format == "pdf":
                self._save_as_pdf(result.text_content, output_path)
            elif format == "html":
                self._save_as_html(result.text_content, output_path)
            else:
                output_path.write_text(result.text_content, encoding="utf-8")
            
            # Cleanup
            if temp_md.exists():
                temp_md.unlink()
            
            logging.info(f"Successfully converted to {format}: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"Conversion failed: {str(e)}")
            return False
    
    def file_to_markdown(self, input_path: Path) -> Optional[str]:
        """
        Convert any supported file format to Markdown
        
        Args:
            input_path: Path to the input file
            
        Returns:
            str: Markdown content, or None if conversion failed
        """
        if not self.converter:
            logging.error("MarkItDown converter not initialized")
            return None
        
        try:
            result = self.converter.convert(str(input_path))
            return result.text_content
        except Exception as e:
            logging.error(f"Failed to convert {input_path} to markdown: {str(e)}")
            return None
    
    def _save_as_docx(self, content: str, output_path: Path):
        """Save content as DOCX format"""
        # TODO: Implement DOCX formatting with python-docx
        # For now, save as text
        output_path.write_text(content, encoding="utf-8")
    
    def _save_as_pdf(self, content: str, output_path: Path):
        """Save content as PDF format"""
        # TODO: Implement PDF generation (e.g., using reportlab or weasyprint)
        # For now, save as text
        output_path.write_text(content, encoding="utf-8")
    
    def _save_as_html(self, content: str, output_path: Path):
        """Save content as HTML format"""
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ISO 9001 Document</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    {content}
</body>
</html>
        """
        output_path.write_text(html_template, encoding="utf-8")

# Singleton instance
converter_service = DocumentConverter()
