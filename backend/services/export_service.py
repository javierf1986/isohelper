"""
Document Export Service
Phase 3: PDF/DOCX/HTML Export Implementation

Converts Markdown documents to professional PDF, DOCX, and HTML formats
with optional company branding, headers, and footers.
"""
import os
from pathlib import Path
from typing import Optional, Literal
from datetime import datetime
from io import BytesIO
import markdown
from xhtml2pdf import pisa
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

ExportFormat = Literal["pdf", "docx", "html"]


class ExportService:
    """Service for exporting ISO documents to various formats"""
    
    def __init__(self):
        self.documents_path = Path(settings.DOCUMENTS_PATH)
        self.exports_path = self.documents_path / "exports"
        self.exports_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Export service initialized. Output path: {self.exports_path}")
    
    def export_document(
        self,
        document_path: str,
        format: ExportFormat,
        company_name: Optional[str] = None,
        include_branding: bool = True,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Export a document to the specified format.
        
        Args:
            document_path: Path to source markdown document
            format: Output format (pdf, docx, html)
            company_name: Company name for branding/headers
            include_branding: Whether to include headers/footers
            output_filename: Custom output filename (without extension)
            
        Returns:
            Path to exported file
            
        Raises:
            FileNotFoundError: If source document not found
            ValueError: If unsupported format specified
        """
        logger.info(f"Exporting document {document_path} to {format}")
        
        # Read source document
        source_file = Path(document_path)
        if not source_file.exists():
            raise FileNotFoundError(f"Document {document_path} not found")
        
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine output filename
        if output_filename:
            base_name = output_filename
        else:
            base_name = source_file.stem
        
        # Export based on format
        if format == "pdf":
            return self._export_to_pdf(base_name, content, company_name, include_branding)
        elif format == "docx":
            return self._export_to_docx(base_name, content, company_name, include_branding)
        elif format == "html":
            return self._export_to_html(base_name, content, company_name, include_branding)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_to_pdf(
        self,
        base_name: str,
        content: str,
        company_name: Optional[str],
        include_branding: bool
    ) -> str:
        """Export to PDF using WeasyPrint"""
        logger.info(f"Generating PDF: {base_name}.pdf")
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            content,
            extensions=['tables', 'fenced_code', 'toc', 'nl2br']
        )
        
        # Create styled HTML
        styled_html = self._create_styled_html(
            html_content,
            company_name,
            include_branding,
            format="pdf"
        )
        
        # Generate PDF using xhtml2pdf
        output_file = self.exports_path / f"{base_name}.pdf"
        
        # Combine HTML with inline CSS for xhtml2pdf
        full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {self._get_pdf_styles()}
    </style>
</head>
<body>
    {styled_html}
</body>
</html>
"""
        
        # Create PDF
        with open(output_file, 'wb') as pdf_file:
            pisa_status = pisa.CreatePDF(full_html, dest=pdf_file)
        
        # Check if PDF generation was successful
        if not pisa_status or (hasattr(pisa_status, 'err') and pisa_status.err):
            raise Exception(f"PDF generation failed")
        
        logger.info(f"PDF generated successfully: {output_file}")
        return str(output_file)
    
    def _export_to_docx(
        self,
        base_name: str,
        content: str,
        company_name: Optional[str],
        include_branding: bool
    ) -> str:
        """Export to DOCX using python-docx"""
        logger.info(f"Generating DOCX: {base_name}.docx")
        
        doc = Document()
        
        # Set document properties
        doc.core_properties.title = "ISO Quality Management System Documentation"
        doc.core_properties.subject = "ISO 9001:2015 Compliance"
        doc.core_properties.author = company_name or "ISO Helper"
        doc.core_properties.created = datetime.now()
        
        # Add header if branding enabled
        if include_branding:
            self._add_docx_header(doc, company_name)
        
        # Parse markdown and add to document
        lines = content.split('\n')
        i = 0
        in_list = False
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                if in_list:
                    in_list = False
                i += 1
                continue
            
            # Headers (must be at line start)
            if line.startswith('# '):
                self._add_docx_heading(doc, line[2:].strip(), level=1)
                in_list = False
            elif line.startswith('## '):
                self._add_docx_heading(doc, line[3:].strip(), level=2)
                in_list = False
            elif line.startswith('### '):
                self._add_docx_heading(doc, line[4:].strip(), level=3)
                in_list = False
            elif line.startswith('#### '):
                self._add_docx_heading(doc, line[5:].strip(), level=4)
                in_list = False
            
            # Bullet lists
            elif stripped.startswith('- ') or stripped.startswith('* '):
                self._add_docx_list_item(doc, stripped[2:])
                in_list = True
            
            # Numbered lists
            elif len(stripped) > 2 and stripped[0].isdigit() and stripped[1] == '.':
                self._add_docx_numbered_item(doc, stripped[3:])
                in_list = True
            
            # Bold paragraph (entire line)
            elif stripped.startswith('**') and stripped.endswith('**') and len(stripped) > 4:
                self._add_docx_bold(doc, stripped[2:-2])
                in_list = False
            
            # Regular paragraph
            else:
                # Only add if not empty
                if stripped:
                    self._add_docx_paragraph(doc, stripped)
                in_list = False
            
            i += 1
        
        # Add footer if branding enabled
        if include_branding:
            self._add_docx_footer(doc)
        
        # Save
        output_file = self.exports_path / f"{base_name}.docx"
        doc.save(str(output_file))
        
        logger.info(f"DOCX generated successfully: {output_file}")
        return str(output_file)
    
    def _export_to_html(
        self,
        base_name: str,
        content: str,
        company_name: Optional[str],
        include_branding: bool
    ) -> str:
        """Export to standalone HTML"""
        logger.info(f"Generating HTML: {base_name}.html")
        
        # Convert markdown to HTML with extensions
        html_content = markdown.markdown(
            content,
            extensions=['tables', 'fenced_code', 'toc', 'codehilite', 'nl2br']
        )
        
        # Create styled HTML
        styled_html = self._create_styled_html(
            html_content,
            company_name,
            include_branding,
            format="html"
        )
        
        # Save
        output_file = self.exports_path / f"{base_name}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(styled_html)
        
        logger.info(f"HTML generated successfully: {output_file}")
        return str(output_file)
    
    def _create_styled_html(
        self,
        content: str,
        company_name: Optional[str],
        include_branding: bool,
        format: str
    ) -> str:
        """Create styled HTML with optional branding"""
        
        header = ""
        if include_branding:
            header = f"""
            <header>
                <h1 class="header-title">{company_name or 'Company Name'}</h1>
                <p class="header-subtitle">Quality Management System Documentation</p>
                <p class="header-date">Generated: {datetime.now().strftime('%B %d, %Y')}</p>
            </header>
            <hr class="header-divider">
            """
        
        footer = ""
        if include_branding:
            footer = """
            <footer>
                <hr class="footer-divider">
                <p>Generated by ISO Helper | Confidential</p>
            </footer>
            """
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ISO Documentation</title>
    <style>
{self._get_html_styles(format)}
    </style>
</head>
<body>
    {header}
    <main>
{content}
    </main>
    {footer}
</body>
</html>"""
    
    def _get_pdf_styles(self) -> str:
        """Get CSS styles for PDF export (simplified for xhtml2pdf)"""
        return """
@page {
    size: a4;
    margin: 2cm;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

header {
    text-align: center;
    border-bottom: 3px solid #0066cc;
    padding-bottom: 20px;
    margin-bottom: 30px;
}

.header-title {
    color: #0066cc;
    font-size: 24pt;
    margin: 0 0 10px 0;
}

.header-subtitle {
    color: #666;
    font-size: 12pt;
    margin: 5px 0;
}

.header-date {
    color: #999;
    font-size: 10pt;
    margin: 5px 0;
}

h1 {
    color: #0066cc;
    font-size: 20pt;
    border-bottom: 2px solid #0066cc;
    padding-bottom: 10px;
    margin-top: 30px;
}

h2 {
    color: #0066cc;
    font-size: 16pt;
    margin-top: 25px;
}

h3 {
    color: #333;
    font-size: 14pt;
    margin-top: 20px;
}

h4 {
    color: #333;
    font-size: 12pt;
    margin-top: 15px;
}

p {
    margin: 10px 0;
}

ul, ol {
    margin: 10px 0;
    padding-left: 30px;
}

li {
    margin: 5px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #0066cc;
    color: white;
    font-weight: bold;
}

code {
    background-color: #f4f4f4;
    padding: 2px 5px;
    font-family: Courier New, monospace;
    font-size: 10pt;
}

pre {
    background-color: #f4f4f4;
    padding: 15px;
    overflow-x: auto;
}

footer {
    text-align: center;
    color: #666;
    font-size: 9pt;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
}

.header-divider, .footer-divider {
    border: none;
    border-top: 1px solid #ddd;
    margin: 20px 0;
}
"""
    
    def _get_html_styles(self, format: str) -> str:
        """Get CSS styles for HTML export"""
        return """
body {
    font-family: 'Arial', 'Helvetica', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f9f9f9;
}

main {
    background-color: white;
    padding: 40px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
    border-radius: 5px;
}

header {
    text-align: center;
    border-bottom: 3px solid #0066cc;
    padding-bottom: 20px;
    margin-bottom: 30px;
}

.header-title {
    color: #0066cc;
    font-size: 28pt;
    margin: 0 0 10px 0;
}

.header-subtitle {
    color: #666;
    font-size: 13pt;
    margin: 5px 0;
}

.header-date {
    color: #999;
    font-size: 11pt;
    margin: 5px 0;
}

h1 {
    color: #0066cc;
    font-size: 22pt;
    border-bottom: 2px solid #0066cc;
    padding-bottom: 10px;
    margin-top: 30px;
}

h2 {
    color: #0066cc;
    font-size: 18pt;
    margin-top: 25px;
}

h3 {
    color: #333;
    font-size: 15pt;
    margin-top: 20px;
}

h4 {
    color: #333;
    font-size: 13pt;
    margin-top: 15px;
}

p {
    margin: 10px 0;
    text-align: justify;
}

ul, ol {
    margin: 10px 0;
    padding-left: 30px;
}

li {
    margin: 5px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
}

th {
    background-color: #0066cc;
    color: white;
    font-weight: bold;
}

tr:nth-child(even) {
    background-color: #f9f9f9;
}

code {
    background-color: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 10pt;
}

pre {
    background-color: #f4f4f4;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
}

pre code {
    background-color: transparent;
    padding: 0;
}

footer {
    text-align: center;
    color: #666;
    font-size: 9pt;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
}

.header-divider, .footer-divider {
    border: none;
    border-top: 1px solid #ddd;
    margin: 20px 0;
}
"""
    
    # ===== DOCX Helper Methods =====
    
    def _add_docx_header(self, doc: Document, company_name: Optional[str]):
        """Add header to DOCX document"""
        section = doc.sections[0]
        header = section.header
        header_para = header.paragraphs[0]
        header_para.text = company_name or "Company Name"
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = header_para.runs[0]
        run.font.color.rgb = RGBColor(0, 102, 204)
        run.font.size = Pt(14)
        run.font.bold = True
    
    def _add_docx_footer(self, doc: Document):
        """Add footer to DOCX document"""
        section = doc.sections[0]
        footer = section.footer
        footer_para = footer.paragraphs[0]
        footer_para.text = f"Generated by ISO Helper | {datetime.now().strftime('%B %d, %Y')} | Confidential"
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = footer_para.runs[0]
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(102, 102, 102)
    
    def _add_docx_heading(self, doc: Document, text: str, level: int):
        """Add heading to DOCX"""
        heading = doc.add_heading(text, level=level)
        if level == 1:
            run = heading.runs[0]
            run.font.color.rgb = RGBColor(0, 102, 204)
    
    def _add_docx_paragraph(self, doc: Document, text: str):
        """Add paragraph to DOCX"""
        para = doc.add_paragraph(text)
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    def _add_docx_bold(self, doc: Document, text: str):
        """Add bold paragraph to DOCX"""
        para = doc.add_paragraph()
        run = para.add_run(text)
        run.bold = True
    
    def _add_docx_list_item(self, doc: Document, text: str):
        """Add bullet list item to DOCX"""
        doc.add_paragraph(text, style='List Bullet')
    
    def _add_docx_numbered_item(self, doc: Document, text: str):
        """Add numbered list item to DOCX"""
        doc.add_paragraph(text, style='List Number')


# Global instance
export_service = ExportService()
