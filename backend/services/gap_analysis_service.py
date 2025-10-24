"""
Gap Analysis Service
AI-powered compliance gap identification and analysis
"""

import uuid
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.gap_models import (
    GapAnalysis, Gap, ComplianceEvidence, RoadmapItem,
    AnalysisStatus, GapSeverity, RoadmapItemStatus
)
from backend.models.iso_models import ISOStandard, ISOClause
from backend.services.document_parser import DocumentParser


class GapAnalysisService:
    """Service for AI-powered gap analysis"""
    
    @staticmethod
    def create_analysis(
        db: Session,
        workspace_id: str,
        user_id: str,
        document_name: str,
        document_path: str,
        iso_standard_id: str
    ) -> GapAnalysis:
        """
        Create a new gap analysis record
        
        Args:
            db: Database session
            workspace_id: Workspace ID
            user_id: User creating the analysis
            document_name: Name of uploaded document
            document_path: Path to stored document
            iso_standard_id: ISO standard to analyze against
            
        Returns:
            New GapAnalysis instance
        """
        # Generate analysis number
        count = db.query(GapAnalysis).filter(
            GapAnalysis.workspace_id == workspace_id
        ).count()
        analysis_number = f"GA-{datetime.utcnow().year}-{count + 1:03d}"
        
        # Create analysis record
        analysis = GapAnalysis(
            id=str(uuid.uuid4()),
            analysis_number=analysis_number,
            workspace_id=workspace_id,
            document_name=document_name,
            document_path=document_path,
            iso_standard_id=iso_standard_id,
            status=AnalysisStatus.PENDING,
            created_by=user_id
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return analysis
    
    @staticmethod
    def parse_document(
        db: Session,
        analysis_id: str,
        document_path: str
    ) -> Dict[str, Any]:
        """
        Parse uploaded document and extract text
        
        Args:
            db: Database session
            analysis_id: Gap analysis ID
            document_path: Path to document file
            
        Returns:
            Parsing result with text and metadata
        """
        analysis = db.query(GapAnalysis).filter(GapAnalysis.id == analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis not found: {analysis_id}")
        
        try:
            # Update status
            analysis.status = AnalysisStatus.PROCESSING
            analysis.progress_percent = 10
            db.commit()
            
            # Parse document
            result = DocumentParser.parse_document(document_path)
            
            # Store extracted text
            analysis.extracted_text = result['text']
            analysis.text_length = result['char_count']
            analysis.file_size = result['file_size']
            analysis.document_type = result['format']
            analysis.progress_percent = 20
            db.commit()
            
            return result
            
        except Exception as e:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            db.commit()
            raise
    
    @staticmethod
    def analyze_gaps_with_ai(
        db: Session,
        analysis_id: str,
        openai_api_key: Optional[str] = None
    ) -> List[Gap]:
        """
        Perform AI-powered gap analysis
        
        Args:
            db: Database session
            analysis_id: Gap analysis ID
            openai_api_key: OpenAI API key (optional, falls back to env)
            
        Returns:
            List of identified gaps
        """
        analysis = db.query(GapAnalysis).filter(GapAnalysis.id == analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis not found: {analysis_id}")
        
        if not analysis.extracted_text:
            raise ValueError("No text extracted from document")
        
        try:
            # Get ISO standard and clauses
            iso_standard = db.query(ISOStandard).filter(
                ISOStandard.id == analysis.iso_standard_id
            ).first()
            
            if not iso_standard:
                raise ValueError(f"ISO standard not found: {analysis.iso_standard_id}")
            
            iso_clauses = db.query(ISOClause).filter(
                ISOClause.iso_standard_id == iso_standard.id
            ).order_by(ISOClause.clause_number).all()
            
            analysis.total_requirements = len(iso_clauses)
            analysis.progress_percent = 30
            db.commit()
            
            # Analyze gaps using AI
            gaps = GapAnalysisService._perform_ai_analysis(
                db=db,
                analysis=analysis,
                iso_standard=iso_standard,
                iso_clauses=iso_clauses,
                document_text=analysis.extracted_text,
                openai_api_key=openai_api_key
            )
            
            # Update analysis summary
            analysis.total_gaps = len(gaps)
            analysis.critical_gaps = sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL)
            analysis.major_gaps = sum(1 for g in gaps if g.severity == GapSeverity.MAJOR)
            analysis.minor_gaps = sum(1 for g in gaps if g.severity == GapSeverity.MINOR)
            analysis.observations = sum(1 for g in gaps if g.severity == GapSeverity.OBSERVATION)
            
            # Calculate compliance score
            total_possible = len(iso_clauses) * 100
            gap_penalty = sum(
                100 if g.severity == GapSeverity.CRITICAL else
                75 if g.severity == GapSeverity.MAJOR else
                30 if g.severity == GapSeverity.MINOR else 10
                for g in gaps
            )
            analysis.compliance_score = max(0, 100 - (gap_penalty / total_possible * 100))
            analysis.coverage_percent = ((len(iso_clauses) - len(gaps)) / len(iso_clauses) * 100) if iso_clauses else 0
            
            analysis.status = AnalysisStatus.COMPLETED
            analysis.progress_percent = 100
            analysis.completed_at = datetime.utcnow()
            db.commit()
            
            return gaps
            
        except Exception as e:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            db.commit()
            raise
    
    @staticmethod
    def _perform_ai_analysis(
        db: Session,
        analysis: GapAnalysis,
        iso_standard: ISOStandard,
        iso_clauses: List[ISOClause],
        document_text: str,
        openai_api_key: Optional[str] = None
    ) -> List[Gap]:
        """
        Core AI analysis logic using OpenAI GPT-4
        
        Args:
            db: Database session
            analysis: GapAnalysis instance
            iso_standard: ISO standard being analyzed
            iso_clauses: List of ISO clauses/requirements
            document_text: Extracted document text
            openai_api_key: OpenAI API key
            
        Returns:
            List of Gap instances
        """
        try:
            import openai
            import os
            
            # Set API key
            api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not provided")
            
            client = openai.OpenAI(api_key=api_key)
            
        except ImportError:
            raise ValueError("openai package not installed. Install with: pip install openai")
        
        gaps = []
        total_tokens = 0
        start_time = datetime.utcnow()
        
        # Chunk document for analysis
        chunks = DocumentParser.chunk_text(document_text, chunk_size=6000, overlap=300)
        
        # Analyze each ISO clause
        for idx, clause in enumerate(iso_clauses):
            analysis.progress_percent = 30 + int((idx / len(iso_clauses)) * 60)
            db.commit()
            
            # Build prompt for this clause
            prompt = GapAnalysisService._build_analysis_prompt(
                iso_standard=iso_standard,
                clause=clause,
                document_chunks=chunks
            )
            
            try:
                # Call GPT-4
                response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert ISO compliance auditor. Analyze documents for compliance gaps against ISO requirements. Provide detailed, accurate assessments."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1500
                )
                
                total_tokens += response.usage.total_tokens
                result_text = response.choices[0].message.content
                
                # Parse AI response
                gap_data = GapAnalysisService._parse_ai_response(result_text, clause)
                
                # Only create gap if one was identified
                if gap_data['has_gap']:
                    gap = Gap(
                        id=str(uuid.uuid4()),
                        analysis_id=analysis.id,
                        workspace_id=analysis.workspace_id,
                        iso_clause=clause.clause_number,
                        iso_clause_title=clause.title,
                        iso_requirement=clause.requirement,
                        severity=gap_data['severity'],
                        gap_description=gap_data['description'],
                        current_state=gap_data['current_state'],
                        required_state=gap_data['required_state'],
                        impact_description=gap_data['impact'],
                        risk_level=gap_data['risk_level'],
                        evidence_found=gap_data['evidence'],
                        evidence_score=gap_data['evidence_score'],
                        ai_confidence=gap_data['confidence'],
                        ai_reasoning=gap_data['reasoning'],
                        recommended_action=gap_data['recommendation'],
                        implementation_effort=gap_data['effort'],
                        priority_score=gap_data['priority']
                    )
                    
                    db.add(gap)
                    gaps.append(gap)
            
            except Exception as e:
                # Log error but continue with other clauses
                print(f"Error analyzing clause {clause.clause_number}: {str(e)}")
                continue
        
        # Update analysis metadata
        analysis.ai_model_used = "gpt-4-turbo-preview"
        analysis.analysis_tokens = total_tokens
        analysis.analysis_duration = int((datetime.utcnow() - start_time).total_seconds())
        db.commit()
        
        return gaps
    
    @staticmethod
    def _build_analysis_prompt(
        iso_standard: ISOStandard,
        clause: ISOClause,
        document_chunks: List[str]
    ) -> str:
        """Build prompt for AI analysis of a specific clause"""
        
        # Combine relevant chunks (for simplicity, use all for now)
        document_excerpt = "\n\n".join(document_chunks[:3])  # First 3 chunks
        
        prompt = f"""Analyze the following QMS documentation for compliance with this ISO {iso_standard.standard_number} requirement:

**ISO Clause: {clause.clause_number}**
**Title: {clause.title}**
**Requirement:**
{clause.requirement}

**Document Content to Analyze:**
{document_excerpt}

**Analysis Task:**
1. Determine if there is a compliance GAP for this requirement
2. If yes, assess the severity and provide details
3. If no gap exists, confirm adequate evidence

**Respond in this JSON format:**
{{
    "has_gap": true/false,
    "severity": "critical/major/minor/observation",
    "description": "What is missing or inadequate",
    "current_state": "What exists now in the documentation",
    "required_state": "What should exist per ISO requirement",
    "impact": "Business/compliance impact of this gap",
    "risk_level": "low/medium/high/critical",
    "evidence": "Any partial evidence found (text excerpts)",
    "evidence_score": 0-100,
    "confidence": 0.0-1.0,
    "reasoning": "Why you identified this as a gap",
    "recommendation": "Specific action to close the gap",
    "effort": "low/medium/high",
    "priority": 1-10
}}

Be precise and specific. Base your analysis only on the provided document content."""
        
        return prompt
    
    @staticmethod
    def _parse_ai_response(response_text: str, clause: ISOClause) -> Dict[str, Any]:
        """Parse AI response into structured gap data"""
        
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
            else:
                data = json.loads(response_text)
            
            # Map severity string to enum
            severity_map = {
                'critical': GapSeverity.CRITICAL,
                'major': GapSeverity.MAJOR,
                'minor': GapSeverity.MINOR,
                'observation': GapSeverity.OBSERVATION
            }
            
            return {
                'has_gap': data.get('has_gap', False),
                'severity': severity_map.get(data.get('severity', 'minor').lower(), GapSeverity.MINOR),
                'description': data.get('description', 'Gap identified'),
                'current_state': data.get('current_state', 'Not documented'),
                'required_state': data.get('required_state', clause.requirement[:200]),
                'impact': data.get('impact', 'Compliance risk'),
                'risk_level': data.get('risk_level', 'medium'),
                'evidence': data.get('evidence', ''),
                'evidence_score': float(data.get('evidence_score', 0)),
                'confidence': float(data.get('confidence', 0.7)),
                'reasoning': data.get('reasoning', 'AI analysis'),
                'recommendation': data.get('recommendation', 'Review and document'),
                'effort': data.get('effort', 'medium'),
                'priority': int(data.get('priority', 5))
            }
            
        except Exception as e:
            # Fallback if parsing fails
            return {
                'has_gap': False,
                'severity': GapSeverity.OBSERVATION,
                'description': 'Could not parse AI response',
                'current_state': 'Unknown',
                'required_state': clause.requirement[:200],
                'impact': 'Unknown',
                'risk_level': 'medium',
                'evidence': response_text[:500],
                'evidence_score': 0,
                'confidence': 0.5,
                'reasoning': f'Parse error: {str(e)}',
                'recommendation': 'Manual review required',
                'effort': 'medium',
                'priority': 5
            }
    
    @staticmethod
    def get_analysis(db: Session, analysis_id: str, workspace_id: str) -> Optional[GapAnalysis]:
        """Get gap analysis by ID"""
        return db.query(GapAnalysis).filter(
            GapAnalysis.id == analysis_id,
            GapAnalysis.workspace_id == workspace_id
        ).first()
    
    @staticmethod
    def get_workspace_analyses(
        db: Session,
        workspace_id: str,
        limit: int = 50
    ) -> List[GapAnalysis]:
        """Get all gap analyses for a workspace"""
        return db.query(GapAnalysis).filter(
            GapAnalysis.workspace_id == workspace_id
        ).order_by(GapAnalysis.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_gaps(
        db: Session,
        analysis_id: str,
        workspace_id: str
    ) -> List[Gap]:
        """Get all gaps for an analysis"""
        return db.query(Gap).filter(
            Gap.analysis_id == analysis_id,
            Gap.workspace_id == workspace_id
        ).order_by(Gap.priority_score.desc()).all()
