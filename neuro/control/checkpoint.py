# Checkpoint & Resume System
# Enables long-running agent tasks to survive crashes/interruptions
# Inspired by SWE-AF's checkpointed execution

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum


class CheckpointStatus(Enum):
    """Status of a checkpoint."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class Checkpoint:
    """A checkpoint for resuming long-running tasks."""
    task_id: str
    status: CheckpointStatus
    current_step: int
    total_steps: int
    progress_pct: float
    data: Dict[str, Any]
    created_at: str
    updated_at: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Checkpoint":
        d["status"] = CheckpointStatus(d["status"])
        return cls(**d)


class CheckpointManager:
    """
    Manages checkpoints for resumable agent execution.
    
    Usage:
        manager = CheckpointManager("./checkpoints")
        manager.save(task_id, step, total, {"result": data})
        # Later...
        state = manager.load(task_id)
        if state:
            resume_from_step(state.current_step)
    """
    
    def __init__(self, checkpoint_dir: str = "./checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._current_checkpoint: Optional[Checkpoint] = None
        
    def _get_path(self, task_id: str) -> Path:
        """Get path for checkpoint file."""
        return self.checkpoint_dir / f"{task_id}.json"
    
    def save(
        self,
        task_id: str,
        current_step: int,
        total_steps: int,
        data: Dict[str, Any],
        status: CheckpointStatus = CheckpointStatus.RUNNING,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save a checkpoint."""
        now = datetime.now().isoformat()
        
        # Check if this is a new checkpoint or update
        existing = self.load(task_id)
        created_at = now
        if existing:
            created_at = existing.created_at
            
        checkpoint = Checkpoint(
            task_id=task_id,
            status=status,
            current_step=current_step,
            total_steps=total_steps,
            progress_pct=round((current_step / total_steps) * 100, 2) if total_steps > 0 else 0,
            data=data,
            created_at=created_at,
            updated_at=now,
            error=error,
            metadata=metadata or {},
        )
        
        path = self._get_path(task_id)
        with open(path, "w") as f:
            json.dump(checkpoint.to_dict(), f, indent=2)
            
        self._current_checkpoint = checkpoint
        return str(path)
    
    def load(self, task_id: str) -> Optional[Checkpoint]:
        """Load a checkpoint if it exists."""
        path = self._get_path(task_id)
        if not path.exists():
            return None
            
        try:
            with open(path) as f:
                d = json.load(f)
            return Checkpoint.from_dict(d)
        except Exception:
            return None
    
    def delete(self, task_id: str) -> bool:
        """Delete a checkpoint."""
        path = self._get_path(task_id)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def list_checkpoints(self, status: Optional[CheckpointStatus] = None) -> List[Checkpoint]:
        """List all checkpoints, optionally filtered by status."""
        checkpoints = []
        for path in self.checkpoint_dir.glob("*.json"):
            try:
                with open(path) as f:
                    d = json.load(f)
                cp = Checkpoint.from_dict(d)
                if status is None or cp.status == status:
                    checkpoints.append(cp)
            except:
                pass
        return sorted(checkpoints, key=lambda c: c.updated_at, reverse=True)
    
    def resume_build(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get data needed to resume a build from checkpoint.
        
        Returns dict with step info and previous data, or None if no checkpoint.
        """
        checkpoint = self.load(task_id)
        if not checkpoint:
            return None
            
        if checkpoint.status == CheckpointStatus.COMPLETED:
            return {"already_completed": True, "result": checkpoint.data}
            
        return {
            "task_id": task_id,
            "current_step": checkpoint.current_step,
            "total_steps": checkpoint.total_steps,
            "previous_data": checkpoint.data,
            "error": checkpoint.error,
            "resume_from_step": checkpoint.current_step + 1,
        }
    
    def mark_completed(self, task_id: str, result: Dict[str, Any]) -> str:
        """Mark a task as completed."""
        return self.save(task_id, 0, 0, result, CheckpointStatus.COMPLETED)
    
    def mark_failed(self, task_id: str, error: str) -> str:
        """Mark a task as failed."""
        if self._current_checkpoint and self._current_checkpoint.task_id == task_id:
            return self.save(
                self._current_checkpoint.task_id,
                self._current_checkpoint.current_step,
                self._current_checkpoint.total_steps,
                self._current_checkpoint.data,
                CheckpointStatus.FAILED,
                error=error,
            )
        return self.save(task_id, 0, 0, {}, CheckpointStatus.FAILED, error=error)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get checkpoint statistics."""
        all_checkpoints = self.list_checkpoints()
        by_status = {}
        for cp in all_checkpoints:
            status_val = cp.status.value
            by_status[status_val] = by_status.get(status_val, 0) + 1
            
        return {
            "total": len(all_checkpoints),
            "by_status": by_status,
            "directory": str(self.checkpoint_dir),
        }


# Convenience instance
_default_manager: Optional[CheckpointManager] = None

def get_checkpoint_manager(dir: str = "./checkpoints") -> CheckpointManager:
    """Get or create the default checkpoint manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = CheckpointManager(dir)
    return _default_manager