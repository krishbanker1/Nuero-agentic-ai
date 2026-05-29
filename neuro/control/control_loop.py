# 3-Tier Control Loop System
# Inspired by SWE-AF architecture - adaptive factory control
# 
# Inner Loop: Single issue retry with feedback
# Middle Loop: New approach/split work when exhausted  
# Outer Loop: Restructure remaining DAG when escalated

import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ControlLoopLevel(Enum):
    """Levels of control loops in the factory architecture."""
    INNER = "inner"      # Single issue retry
    MIDDLE = "middle"    # New approach when exhausted
    OUTER = "outer"      # Restructure DAG on escalated failure


class EscalationReason(Enum):
    """Why a loop escalated to the next level."""
    INNER_EXHAUSTED = "inner_exhausted"
    MIDDLE_EXHAUSTED = "middle_exhausted"
    UNRECOVERABLE = "unrecoverable"
    SCOPE_RELAXED = "scope_relaxed"
    DEADLOCK = "deadlock"


@dataclass
class LoopMetrics:
    """Metrics for a control loop iteration."""
    level: ControlLoopLevel
    iteration: int
    action: str
    result: str
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass 
class Compromise:
    """Track when scope is relaxed or debt is accepted."""
    original_requirement: str
    relaxed_to: str
    severity: int
    typed: str = "scope"
    accepted_at: datetime = field(default_factory=datetime.now)


@dataclass
class ControlLoopState:
    """State maintained across control loop iterations."""
    inner_attempts: int = 0
    middle_attempts: int = 0
    outer_attempts: int = 0
    total_duration_ms: float = 0.0
    metrics: List[LoopMetrics] = field(default_factory=list)
    compromises: List[Compromise] = field(default_factory=list)
    escalated: bool = False
    current_level: ControlLoopLevel = ControlLoopLevel.INNER
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "inner_attempts": self.inner_attempts,
            "middle_attempts": self.middle_attempts,
            "outer_attempts": self.outer_attempts,
            "compromises_count": len(self.compromises),
            "escalated": self.escalated,
        }


class ControlLoop:
    """
    3-tier adaptive control loop for autonomous agent execution.
    
    Inspired by SWE-AF's factory architecture:
    - Inner loop: Quick retries with feedback
    - Middle loop: New approaches, work splitting
    - Outer loop: DAG restructuring when things fail badly
    """
    
    def __init__(
        self,
        max_inner: int = 3,
        max_middle: int = 3,
        max_outer: int = 2,
        enable_compromise_tracking: bool = True,
    ):
        self.max_inner = max_inner
        self.max_middle = max_middle
        self.max_outer = max_outer
        self.enable_compromise_tracking = enable_compromise_tracking
        self.state = ControlLoopState()
        
    def run(
        self,
        task_fn: Callable,
        feedback_fn: Optional[Callable] = None,
        split_fn: Optional[Callable] = None,
        restructure_fn: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Run the 3-tier control loop."""
        start_time = time.time()
        result = {"success": False, "result": None, "error": None}
        
        while True:
            try:
                # INNER LOOP
                inner_success = self._run_inner_loop(task_fn, feedback_fn)
                if inner_success:
                    result["success"] = True
                    break
                    
                # MIDDLE LOOP
                middle_success = self._run_middle_loop(task_fn, feedback_fn, split_fn)
                if middle_success:
                    result["success"] = True
                    break
                    
                # OUTER LOOP
                if self.state.outer_attempts >= self.max_outer:
                    result["error"] = f"All loops exhausted. Last error: {self.state.last_error}"
                    break
                    
                if not self._run_outer_loop(restructure_fn):
                    break
                    
            except Exception as e:
                self.state.last_error = str(e)
                result["error"] = str(e)
                break
                
        self.state.total_duration_ms = (time.time() - start_time) * 1000
        return {**result, "state": self.state.to_dict()}
    
    def _run_inner_loop(self, task_fn: Callable, feedback_fn: Optional[Callable]) -> bool:
        for i in range(self.max_inner):
            self.state.inner_attempts += 1
            try:
                task_fn()
                return True
            except Exception as e:
                self.state.last_error = str(e)
                if feedback_fn and i < self.max_inner - 1:
                    try:
                        feedback_fn(e)
                    except:
                        pass
        return False
    
    def _run_middle_loop(self, task_fn: Callable, feedback_fn: Optional[Callable], 
                         split_fn: Optional[Callable]) -> bool:
        for i in range(self.max_middle):
            self.state.middle_attempts += 1
            if split_fn:
                try:
                    sub_tasks = split_fn()
                    if sub_tasks:
                        all_success = True
                        for st in sub_tasks:
                            try:
                                if callable(st):
                                    st()
                            except:
                                all_success = False
                        if all_success:
                            return True
                except:
                    pass
            try:
                task_fn()
                return True
            except Exception as e:
                self.state.last_error = str(e)
        return False
    
    def _run_outer_loop(self, restructure_fn: Optional[Callable]) -> bool:
        self.state.outer_attempts += 1
        self.state.current_level = ControlLoopLevel.OUTER
        if restructure_fn:
            try:
                restructure_fn()
                return True
            except Exception as e:
                self.state.last_error = str(e)
                return False
        return False
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_attempts": self.state.inner_attempts + self.state.middle_attempts + self.state.outer_attempts,
            "by_level": {"inner": self.state.inner_attempts, "middle": self.state.middle_attempts, "outer": self.state.outer_attempts},
            "compromises": len(self.state.compromises),
        }


def run_with_control_loop(task_fn: Callable, feedback_fn: Optional[Callable] = None,
                          split_fn: Optional[Callable] = None, **kwargs) -> Dict[str, Any]:
    """Quick wrapper for control loop execution."""
    return ControlLoop(**kwargs).run(task_fn, feedback_fn, split_fn)