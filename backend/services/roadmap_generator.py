"""
Roadmap Generator Service
Creates implementation roadmaps from gap analysis results
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.gap_models import (
    Gap, RoadmapItem, GapAnalysis, GapSeverity, RoadmapItemStatus
)


class RoadmapGeneratorService:
    """Service for generating compliance roadmaps"""
    
    # Effort estimates (hours)
    EFFORT_MAP = {
        'low': 20,
        'medium': 40,
        'high': 80
    }
    
    # Cost per hour (default rate)
    HOURLY_RATE = 150  # USD
    
    @staticmethod
    def generate_roadmap(
        db: Session,
        analysis_id: str,
        workspace_id: str
    ) -> List[RoadmapItem]:
        """
        Generate implementation roadmap from gap analysis
        
        Args:
            db: Database session
            analysis_id: Gap analysis ID
            workspace_id: Workspace ID
            
        Returns:
            List of roadmap items
        """
        # Get analysis and gaps
        analysis = db.query(GapAnalysis).filter(
            GapAnalysis.id == analysis_id,
            GapAnalysis.workspace_id == workspace_id
        ).first()
        
        if not analysis:
            raise ValueError(f"Analysis not found: {analysis_id}")
        
        gaps = db.query(Gap).filter(
            Gap.analysis_id == analysis_id,
            Gap.workspace_id == workspace_id
        ).order_by(Gap.priority_score.desc()).all()
        
        if not gaps:
            return []
        
        # Group gaps by logical implementation units
        grouped_gaps = RoadmapGeneratorService._group_gaps(gaps)
        
        # Create roadmap items
        roadmap_items = []
        item_counter = 1
        
        for group_name, group_gaps in grouped_gaps.items():
            roadmap_item = RoadmapGeneratorService._create_roadmap_item(
                db=db,
                analysis=analysis,
                group_name=group_name,
                gaps=group_gaps,
                item_number=item_counter
            )
            
            roadmap_items.append(roadmap_item)
            item_counter += 1
        
        # Set dependencies
        RoadmapGeneratorService._set_dependencies(roadmap_items)
        
        # Set milestones and dates
        RoadmapGeneratorService._assign_milestones(roadmap_items)
        
        # Save to database
        for item in roadmap_items:
            db.add(item)
        
        db.commit()
        
        return roadmap_items
    
    @staticmethod
    def _group_gaps(gaps: List[Gap]) -> Dict[str, List[Gap]]:
        """
        Group gaps into logical implementation units
        
        Groups by ISO clause prefix (e.g., all 4.x, 5.x, etc.)
        and combines related gaps
        """
        groups = {}
        
        for gap in gaps:
            # Extract main clause number (e.g., "4.4.2" -> "4")
            clause_parts = gap.iso_clause.split('.')
            main_clause = clause_parts[0] if clause_parts else "Other"
            
            # Group name based on clause
            group_name = RoadmapGeneratorService._get_group_name(main_clause)
            
            if group_name not in groups:
                groups[group_name] = []
            
            groups[group_name].append(gap)
        
        return groups
    
    @staticmethod
    def _get_group_name(clause_number: str) -> str:
        """Get friendly group name for ISO clause"""
        clause_map = {
            '4': 'Context of the Organization',
            '5': 'Leadership',
            '6': 'Planning',
            '7': 'Support',
            '8': 'Operation',
            '9': 'Performance Evaluation',
            '10': 'Improvement'
        }
        
        return clause_map.get(clause_number, f'Clause {clause_number}')
    
    @staticmethod
    def _create_roadmap_item(
        db: Session,
        analysis: GapAnalysis,
        group_name: str,
        gaps: List[Gap],
        item_number: int
    ) -> RoadmapItem:
        """Create a roadmap item from a group of gaps"""
        
        # Calculate aggregated metrics
        total_gaps = len(gaps)
        critical_count = sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL)
        major_count = sum(1 for g in gaps if g.severity == GapSeverity.MAJOR)
        
        # Determine overall priority (1-10)
        priority = min(10, critical_count * 3 + major_count * 2 + len(gaps))
        
        # Determine impact level
        if critical_count > 0:
            impact = 'critical'
        elif major_count > 2:
            impact = 'high'
        elif major_count > 0:
            impact = 'medium'
        else:
            impact = 'low'
        
        # Determine effort level (aggregate from gaps)
        effort_scores = {
            'low': sum(1 for g in gaps if g.implementation_effort == 'low'),
            'medium': sum(1 for g in gaps if g.implementation_effort == 'medium'),
            'high': sum(1 for g in gaps if g.implementation_effort == 'high')
        }
        effort = max(effort_scores, key=effort_scores.get)
        
        # Estimate hours and cost
        estimated_hours = sum(
            RoadmapGeneratorService.EFFORT_MAP.get(g.implementation_effort or 'medium', 40)
            for g in gaps
        )
        estimated_cost = estimated_hours * RoadmapGeneratorService.HOURLY_RATE
        estimated_duration_days = int(estimated_hours / 8) + 5  # 8 hours/day + buffer
        
        # Build title and description
        title = f"Implement {group_name} Requirements"
        gap_list = "\n".join([f"- {g.iso_clause}: {g.gap_description[:100]}" for g in gaps[:5]])
        if len(gaps) > 5:
            gap_list += f"\n- ...and {len(gaps) - 5} more gaps"
        
        description = f"""This implementation phase addresses {total_gaps} gap(s) in {group_name}.

**Gaps to Address:**
{gap_list}

**Key Requirements:**
{', '.join(set(g.iso_clause for g in gaps))}"""
        
        # Create deliverables list
        deliverables = [
            "Updated QMS documentation",
            "Procedures and work instructions",
            "Training materials",
            "Implementation evidence",
            "Verification records"
        ]
        
        # Completion criteria
        completion_criteria = f"All {total_gaps} gaps closed with documented evidence"
        
        # Create roadmap item
        roadmap_item = RoadmapItem(
            id=str(uuid.uuid4()),
            analysis_id=analysis.id,
            workspace_id=analysis.workspace_id,
            item_number=f"RI-{item_number:03d}",
            title=title,
            description=description,
            priority=priority,
            impact=impact,
            effort=effort,
            complexity='moderate' if len(gaps) > 3 else 'simple',
            estimated_cost=estimated_cost,
            estimated_hours=estimated_hours,
            estimated_duration_days=estimated_duration_days,
            gap_ids=[g.id for g in gaps],
            gap_count=total_gaps,
            deliverables=deliverables,
            completion_criteria=completion_criteria,
            status=RoadmapItemStatus.NOT_STARTED,
            progress_percent=0
        )
        
        return roadmap_item
    
    @staticmethod
    def _set_dependencies(roadmap_items: List[RoadmapItem]) -> None:
        """
        Set dependencies between roadmap items
        
        Logic: Foundation clauses (4, 5, 6) should be completed before
        operational clauses (7, 8) and before improvement clauses (9, 10)
        """
        # Sort by priority to establish order
        sorted_items = sorted(roadmap_items, key=lambda x: x.priority, reverse=True)
        
        for i, item in enumerate(sorted_items):
            dependencies = []
            
            # Higher priority items may depend on foundational items
            if i > 0 and item.priority < sorted_items[0].priority - 2:
                # Depend on all critical items
                dependencies = [
                    dep_item.id for dep_item in sorted_items[:i]
                    if dep_item.impact == 'critical'
                ]
            
            item.dependencies = dependencies if dependencies else []
            
            # Update "blocks" for dependent items
            for dep_id in dependencies:
                dep_item = next((x for x in sorted_items if x.id == dep_id), None)
                if dep_item:
                    blocks = dep_item.blocks or []
                    blocks.append(item.id)
                    dep_item.blocks = blocks
    
    @staticmethod
    def _assign_milestones(roadmap_items: List[RoadmapItem]) -> None:
        """
        Assign milestones and estimated dates to roadmap items
        
        Creates 3-4 phases with dates
        """
        total_items = len(roadmap_items)
        
        # Sort by priority for phasing
        sorted_items = sorted(roadmap_items, key=lambda x: x.priority, reverse=True)
        
        # Assign to phases
        phase_size = max(1, total_items // 3)
        current_date = datetime.utcnow()
        
        for i, item in enumerate(sorted_items):
            phase_num = min(3, i // phase_size + 1)
            item.milestone = f"Phase {phase_num}: {'Foundation' if phase_num == 1 else 'Implementation' if phase_num == 2 else 'Completion'}"
            
            # Calculate dates based on phase and dependencies
            start_offset = (phase_num - 1) * 30 + (i % phase_size) * 7
            item.planned_start_date = current_date + timedelta(days=start_offset)
            item.planned_completion_date = item.planned_start_date + timedelta(days=item.estimated_duration_days)
    
    @staticmethod
    def update_roadmap_progress(
        db: Session,
        roadmap_item_id: str,
        workspace_id: str,
        status: RoadmapItemStatus,
        progress_percent: int,
        notes: Optional[str] = None
    ) -> RoadmapItem:
        """Update progress on a roadmap item"""
        
        item = db.query(RoadmapItem).filter(
            RoadmapItem.id == roadmap_item_id,
            RoadmapItem.workspace_id == workspace_id
        ).first()
        
        if not item:
            raise ValueError(f"Roadmap item not found: {roadmap_item_id}")
        
        item.status = status
        item.progress_percent = max(0, min(100, progress_percent))
        
        if status == RoadmapItemStatus.IN_PROGRESS and not item.actual_start_date:
            item.actual_start_date = datetime.utcnow()
        
        if status == RoadmapItemStatus.COMPLETED:
            item.actual_completion_date = datetime.utcnow()
            item.progress_percent = 100
        
        if notes:
            item.notes = (item.notes or '') + f"\n[{datetime.utcnow().strftime('%Y-%m-%d')}] {notes}"
        
        db.commit()
        db.refresh(item)
        
        return item
    
    @staticmethod
    def get_roadmap(
        db: Session,
        analysis_id: str,
        workspace_id: str
    ) -> List[RoadmapItem]:
        """Get roadmap for an analysis"""
        return db.query(RoadmapItem).filter(
            RoadmapItem.analysis_id == analysis_id,
            RoadmapItem.workspace_id == workspace_id
        ).order_by(RoadmapItem.priority.desc()).all()
    
    @staticmethod
    def get_roadmap_statistics(
        db: Session,
        analysis_id: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """Get summary statistics for a roadmap"""
        
        items = RoadmapGeneratorService.get_roadmap(db, analysis_id, workspace_id)
        
        if not items:
            return {
                'total_items': 0,
                'completed': 0,
                'in_progress': 0,
                'not_started': 0,
                'total_cost': 0,
                'total_hours': 0,
                'completion_percent': 0
            }
        
        return {
            'total_items': len(items),
            'completed': sum(1 for item in items if item.status == RoadmapItemStatus.COMPLETED),
            'in_progress': sum(1 for item in items if item.status == RoadmapItemStatus.IN_PROGRESS),
            'not_started': sum(1 for item in items if item.status == RoadmapItemStatus.NOT_STARTED),
            'total_cost': sum(item.estimated_cost or 0 for item in items),
            'total_hours': sum(item.estimated_hours or 0 for item in items),
            'completion_percent': int(sum(item.progress_percent for item in items) / len(items)) if items else 0,
            'phases': len(set(item.milestone for item in items if item.milestone))
        }
