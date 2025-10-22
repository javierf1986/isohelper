"""
Document Generation Service
Epic 1, Feature 1.1: Core document generation logic
"""
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from jinja2 import Template

from config.settings import settings
from templates.iso9001 import ISO_CLAUSES

class DocumentGenerator:
    """
    Main document generation engine
    Combines templates with company data to generate ISO 9001 documents
    """
    
    def __init__(self):
        self.templates_path = Path(settings.TEMPLATES_PATH)
        self.output_path = Path(settings.DOCUMENTS_PATH)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def generate_document(
        self,
        clause: str,
        company_data: Dict,
        language: str = "en"
    ) -> Optional[str]:
        """
        Generate a document for a specific ISO 9001 clause
        
        Args:
            clause: ISO clause number (e.g., "4.1", "5.1")
            company_data: Dictionary with company information
            language: Target language (default: "en")
            
        Returns:
            str: Path to generated document, or None if failed
        """
        try:
            # Load template
            template_content = self._load_template(clause)
            if not template_content:
                logging.error(f"Template not found for clause {clause}")
                return None
            
            # Prepare template variables
            template_vars = self._prepare_template_vars(company_data)
            
            # Render template
            rendered = self._render_template(template_content, template_vars)
            
            # Save output
            output_file = self._save_document(clause, rendered, company_data.get("company_name", "Unknown"))
            
            logging.info(f"Generated document for clause {clause}: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logging.error(f"Document generation failed for clause {clause}: {str(e)}")
            return None
    
    def generate_full_manual(
        self,
        clauses: List[str],
        company_data: Dict
    ) -> Optional[str]:
        """
        Generate complete ISO 9001 manual with multiple clauses
        
        Args:
            clauses: List of ISO clause numbers to include
            company_data: Company information dictionary
            
        Returns:
            str: Path to complete manual, or None if failed
        """
        try:
            generated_docs = []
            
            for clause in clauses:
                doc_path = self.generate_document(clause, company_data)
                if doc_path:
                    generated_docs.append(doc_path)
            
            # Combine documents into single manual
            if generated_docs:
                manual_path = self._combine_documents(
                    generated_docs,
                    company_data.get("company_name", "Unknown")
                )
                return str(manual_path)
            
            return None
            
        except Exception as e:
            logging.error(f"Full manual generation failed: {str(e)}")
            return None
    
    def _load_template(self, clause: str) -> Optional[str]:
        """Load template file for given clause"""
        # Get template from ISO_CLAUSES metadata
        if clause not in ISO_CLAUSES:
            return None
        
        template_file = ISO_CLAUSES[clause]["template"]
        template_path = self.templates_path / template_file
        
        if not template_path.exists():
            return None
        
        return template_path.read_text(encoding="utf-8")
    
    def _prepare_template_vars(self, company_data: Dict) -> Dict:
        """Prepare variables for template rendering"""
        now = datetime.now()
        
        return {
            "company_name": company_data.get("company_name", "[Company Name]"),
            "industry": company_data.get("industry", "[Industry]"),
            "company_size": company_data.get("company_size", "medium"),
            "generation_date": now.strftime("%Y-%m-%d"),
            "next_review_date": (now + timedelta(days=365)).strftime("%Y-%m-%d"),
            **company_data  # Include any additional custom fields
        }
    
    def _render_template(self, template_content: str, variables: Dict) -> str:
        """Render Jinja2 template with variables"""
        template = Template(template_content)
        return template.render(**variables)
    
    def _save_document(self, clause: str, content: str, company_name: str) -> Path:
        """Save generated document to file"""
        filename = f"{company_name.replace(' ', '_')}_ISO9001_Clause_{clause.replace('.', '_')}.md"
        output_file = self.output_path / filename
        output_file.write_text(content, encoding="utf-8")
        return output_file
    
    def _combine_documents(self, doc_paths: List[str], company_name: str) -> Path:
        """Combine multiple documents into single manual"""
        combined_content = [
            f"# ISO 9001:2015 Quality Manual",
            f"## {company_name}",
            f"",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"",
            "---",
            ""
        ]
        
        for doc_path in doc_paths:
            content = Path(doc_path).read_text(encoding="utf-8")
            combined_content.append(content)
            combined_content.append("\n---\n")
        
        manual_filename = f"{company_name.replace(' ', '_')}_ISO9001_Complete_Manual.md"
        manual_path = self.output_path / manual_filename
        manual_path.write_text("\n".join(combined_content), encoding="utf-8")
        
        return manual_path

# Singleton instance
generator_service = DocumentGenerator()
