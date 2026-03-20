from typing import List, Optional, Tuple
from pydantic import BaseModel, Field, validator
from pathlib import Path
import os

class ToolCheck(BaseModel):
    tool_name: str
    available: bool
    path: Optional[str] = None

class GitCheck(BaseModel):
    is_clean: bool
    branch: str
    is_feature_branch: bool
    uncommitted_files: List[str] = Field(default_factory=list)

class BeadsCheck(BaseModel):
    bd_available: bool
    active_issues_count: int
    msg: str

class ContextCheck(BaseModel):
    roadmap_exists: bool
    implementation_plan_exists: bool
    missing_docs: List[str] = Field(default_factory=list)

class ApprovalCheck(BaseModel):
    approved: bool
    timestamp: Optional[str] = None
    age_hours: float = 0.0
    stale: bool = False

class FlightCheckResult(BaseModel):
    phase: str
    passed: bool
    blockers: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

# Validator logic
import subprocess
from datetime import datetime, timedelta

def check_git(project_root: Path) -> GitCheck:
    try:
        # Get branch
        branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
        is_feature = branch.startswith(("agent/", "feature/", "chore/"))
        
        # Get status
        status_out = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        uncommitted = [line[3:] for line in status_out.split("\n") if line.strip()]
        
        return GitCheck(
            is_clean=len(uncommitted) == 0,
            branch=branch,
            is_feature_branch=is_feature,
            uncommitted_files=uncommitted
        )
    except Exception as e:
        return GitCheck(is_clean=False, branch="unknown", is_feature_branch=False, uncommitted_files=[str(e)])

def check_planning_docs(project_root: Path) -> ContextCheck:
    roadmap = project_root / ".agent/rules/ROADMAP.md"
    impl_plan = project_root / ".agent/rules/ImplementationPlan.md"
    
    missing = []
    if not roadmap.exists():
        missing.append(".agent/rules/ROADMAP.md")
    if not impl_plan.exists():
        missing.append(".agent/rules/ImplementationPlan.md")
        
    return ContextCheck(
        roadmap_exists=roadmap.exists(),
        implementation_plan_exists=impl_plan.exists(),
        missing_docs=missing
    )

def check_approval(max_hours: int = 4) -> ApprovalCheck:
    task_paths = [Path(".agent/task.md"), Path("task.md")]
    
    # Check brain directory (most recent)
    brain_dir = Path.home() / ".gemini" / "antigravity" / "brain"
    if brain_dir.exists():
        session_dirs = sorted([d for d in brain_dir.iterdir() if d.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True)[:3]
        for d in session_dirs:
            task_paths.append(d / "task.md")

    for path in task_paths:
        if path.exists():
            content = path.read_text()
            if "## Approval" in content or "[x]" in content.lower():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                age = (datetime.now() - mtime).total_seconds() / 3600
                return ApprovalCheck(
                    approved=True,
                    timestamp=mtime.isoformat(),
                    age_hours=age,
                    stale=age > max_hours
                )
    return ApprovalCheck(approved=False)

def check_beads() -> BeadsCheck:
    try:
        result = subprocess.run(["bd", "ready"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            count = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            return BeadsCheck(bd_available=True, active_issues_count=count, msg=f"Issues ready: {count}")
        return BeadsCheck(bd_available=True, active_issues_count=0, msg="No ready issues")
    except Exception as e:
        return BeadsCheck(bd_available=False, active_issues_count=0, msg=str(e))

def validate_initialization(project_root: Path) -> FlightCheckResult:
    blockers = []
    warnings = []
    
    # 1. Context
    context = check_planning_docs(project_root)
    if not context.roadmap_exists or not context.implementation_plan_exists:
        warnings.append(f"Missing planning docs: {context.missing_docs}")
        
    # 2. Issues
    beads = check_beads()
    if not beads.bd_available:
        warnings.append(f"Beads issues: {beads.msg}")
        
    # 3. Approval
    approval = check_approval()
    if not approval.approved:
        warnings.append("No plan approval found in task.md")
    elif approval.stale:
        warnings.append(f"Plan approval is stale ({approval.age_hours:.1f} hours old)")
        
    passed = len(blockers) == 0
    return FlightCheckResult(
        phase="Initialization",
        passed=passed,
        blockers=blockers,
        warnings=warnings,
        metadata={
            "context": context.model_dump(),
            "beads": beads.model_dump(),
            "approval": approval.model_dump()
        }
    )
