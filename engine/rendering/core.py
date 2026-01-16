"""
Rendering Engine Module
=======================
Terminal rendering system with frame budgeting and performance guards.

This module provides:
- Frame timing and budget management
- Double buffering (conceptual, via asciimatics)
- Render layer system (background, particles, UI)
- Performance profiling hooks
- Dirty rectangle optimization

Design Philosophy:
Terminal rendering is fundamentally different from GPU rendering.
We optimize for:
- Minimal screen updates
- Character-level precision
- Color palette constraints
- VT100/ANSI compatibility
"""
from __future__ import annotations
import time
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
from functools import wraps
import statistics


class RenderLayer(Enum):
    """Render layers from back to front."""
    BACKGROUND = 0
    CLOUDS = 10
    PRECIPITATION = 20
    EFFECTS = 30
    CREATURES = 40
    UI_BACKGROUND = 50
    UI_FOREGROUND = 60
    DEBUG = 100


@dataclass
class RenderStats:
    """Frame rendering statistics."""
    frame_times: List[float] = field(default_factory=list)
    layer_times: Dict[str, List[float]] = field(default_factory=dict)
    particle_counts: List[int] = field(default_factory=list)
    dropped_frames: int = 0
    total_frames: int = 0
    
    # Settings
    sample_window: int = 60  # Frames to keep for averaging
    
    def record_frame(self, frame_time: float, particle_count: int = 0):
        """Record frame statistics."""
        self.total_frames += 1
        self.frame_times.append(frame_time)
        self.particle_counts.append(particle_count)
        
        # Trim to window
        if len(self.frame_times) > self.sample_window:
            self.frame_times.pop(0)
        if len(self.particle_counts) > self.sample_window:
            self.particle_counts.pop(0)
    
    def record_layer(self, layer_name: str, render_time: float):
        """Record layer render time."""
        if layer_name not in self.layer_times:
            self.layer_times[layer_name] = []
        
        self.layer_times[layer_name].append(render_time)
        
        if len(self.layer_times[layer_name]) > self.sample_window:
            self.layer_times[layer_name].pop(0)
    
    @property
    def avg_frame_time(self) -> float:
        """Average frame time in ms."""
        if not self.frame_times:
            return 0
        return statistics.mean(self.frame_times) * 1000
    
    @property
    def fps(self) -> float:
        """Current FPS estimate."""
        avg = self.avg_frame_time
        return 1000 / avg if avg > 0 else 0
    
    @property
    def percentile_95(self) -> float:
        """95th percentile frame time (ms)."""
        if len(self.frame_times) < 2:
            return 0
        sorted_times = sorted(self.frame_times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[idx] * 1000
    
    def get_report(self) -> Dict[str, Any]:
        """Get performance report."""
        return {
            'fps': round(self.fps, 1),
            'avg_ms': round(self.avg_frame_time, 2),
            'p95_ms': round(self.percentile_95, 2),
            'total_frames': self.total_frames,
            'dropped': self.dropped_frames,
            'avg_particles': round(statistics.mean(self.particle_counts), 0) if self.particle_counts else 0,
            'layers': {
                name: round(statistics.mean(times) * 1000, 2)
                for name, times in self.layer_times.items()
                if times
            }
        }


class FrameBudget:
    """
    Frame budget manager for consistent frame rates.
    
    Allocates time budget across render phases and
    enables adaptive quality reduction when over budget.
    """
    
    def __init__(self, target_fps: float = 30.0):
        self.target_fps = target_fps
        self.frame_budget_ms = 1000 / target_fps
        
        # Phase budgets (percentage of frame)
        self.phase_budgets = {
            'physics': 0.3,      # 30% for physics
            'render': 0.5,      # 50% for rendering
            'particles': 0.15,  # 15% for particle spawn/update
            'misc': 0.05,       # 5% buffer
        }
        
        # Current frame tracking
        self.frame_start = 0
        self.phase_start = 0
        self.phase_times: Dict[str, float] = {}
        
        # Adaptive quality
        self.quality_level = 1.0  # 1.0 = full quality
        self.overrun_count = 0
    
    def begin_frame(self):
        """Start frame timing."""
        self.frame_start = time.perf_counter()
        self.phase_times.clear()
    
    def begin_phase(self, phase_name: str):
        """Start timing a phase."""
        self.phase_start = time.perf_counter()
    
    def end_phase(self, phase_name: str) -> float:
        """End phase timing, return time in ms."""
        elapsed = (time.perf_counter() - self.phase_start) * 1000
        self.phase_times[phase_name] = elapsed
        return elapsed
    
    def time_remaining_ms(self) -> float:
        """Get remaining frame budget in ms."""
        elapsed = (time.perf_counter() - self.frame_start) * 1000
        return max(0, self.frame_budget_ms - elapsed)
    
    def is_over_budget(self) -> bool:
        """Check if frame is over budget."""
        return self.time_remaining_ms() <= 0
    
    def phase_budget_ms(self, phase_name: str) -> float:
        """Get budget for a specific phase in ms."""
        ratio = self.phase_budgets.get(phase_name, 0.1)
        return self.frame_budget_ms * ratio * self.quality_level
    
    def adjust_quality(self, frame_time_ms: float):
        """Adjust quality level based on frame time."""
        if frame_time_ms > self.frame_budget_ms * 1.2:
            # Significantly over budget
            self.overrun_count += 1
            if self.overrun_count > 5:
                self.quality_level = max(0.3, self.quality_level - 0.1)
                self.overrun_count = 0
        elif frame_time_ms < self.frame_budget_ms * 0.7:
            # Under budget, can increase quality
            self.quality_level = min(1.0, self.quality_level + 0.02)
            self.overrun_count = max(0, self.overrun_count - 1)
    
    def end_frame(self) -> float:
        """End frame, return total time in ms."""
        frame_time = (time.perf_counter() - self.frame_start) * 1000
        self.adjust_quality(frame_time)
        return frame_time


def profile_function(stats: RenderStats, layer_name: str):
    """Decorator to profile function execution time."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            stats.record_layer(layer_name, elapsed)
            return result
        return wrapper
    return decorator


@dataclass
class RenderCommand:
    """Single render command (character placement)."""
    x: int
    y: int
    char: str
    colour: int
    attr: int = 0  # Attributes (bold, etc)
    layer: RenderLayer = RenderLayer.PRECIPITATION
    
    def __hash__(self):
        return hash((self.x, self.y, self.layer.value))


class RenderQueue:
    """
    Sorted render command queue.
    
    Commands are sorted by layer for proper z-ordering.
    Duplicate positions in same layer are overwritten (last wins).
    """
    
    def __init__(self):
        self.commands: Dict[Tuple[int, int, int], RenderCommand] = {}
    
    def add(self, cmd: RenderCommand):
        """Add render command."""
        key = (cmd.x, cmd.y, cmd.layer.value)
        self.commands[key] = cmd
    
    def add_text(self, x: int, y: int, text: str, colour: int,
                 layer: RenderLayer = RenderLayer.UI_FOREGROUND):
        """Add text string as multiple commands."""
        for i, char in enumerate(text):
            self.add(RenderCommand(x + i, y, char, colour, layer=layer))
    
    def clear(self):
        """Clear all commands."""
        self.commands.clear()
    
    def get_sorted(self) -> List[RenderCommand]:
        """Get commands sorted by layer."""
        return sorted(self.commands.values(), key=lambda c: c.layer.value)
    
    def execute(self, screen) -> int:
        """
        Execute all render commands.
        
        Returns number of characters rendered.
        """
        count = 0
        for cmd in self.get_sorted():
            try:
                screen.print_at(
                    cmd.char, cmd.x, cmd.y,
                    colour=cmd.colour, attr=cmd.attr
                )
                count += 1
            except:
                pass
        return count


class Renderer(ABC):
    """Abstract base renderer."""
    
    @abstractmethod
    def render(self, queue: RenderQueue, state: Any):
        """Render to queue."""
        pass
    
    @property
    @abstractmethod
    def layer(self) -> RenderLayer:
        """Get render layer."""
        pass


class ParticleRenderer(Renderer):
    """Renders particles to queue."""
    
    def __init__(self, bounds: Tuple[int, int, int, int]):
        self.bounds = bounds  # x_min, y_min, x_max, y_max
    
    @property
    def layer(self) -> RenderLayer:
        return RenderLayer.PRECIPITATION
    
    def render(self, queue: RenderQueue, particles: List):
        """Render particles to queue."""
        x_min, y_min, x_max, y_max = self.bounds
        
        for p in particles:
            x, y = int(p.position.x), int(p.position.y)
            
            if x_min <= x < x_max and y_min <= y < y_max:
                queue.add(RenderCommand(
                    x=x, y=y,
                    char=p.char,
                    colour=p.colour,
                    layer=self.layer
                ))


class RenderEngine:
    """
    Main render engine coordinating all rendering.
    
    Features:
    - Layer-based rendering
    - Performance monitoring
    - Adaptive quality
    - Frame budgeting
    """
    
    def __init__(self, screen, target_fps: float = 30.0):
        self.screen = screen
        self.width = screen.width
        self.height = screen.height
        
        self.queue = RenderQueue()
        self.stats = RenderStats()
        self.budget = FrameBudget(target_fps)
        
        self.renderers: List[Renderer] = []
    
    def add_renderer(self, renderer: Renderer):
        """Register a renderer."""
        self.renderers.append(renderer)
        # Sort by layer
        self.renderers.sort(key=lambda r: r.layer.value)
    
    def begin_frame(self):
        """Start new frame."""
        self.budget.begin_frame()
        self.queue.clear()
    
    def render_layer(self, layer_name: str, render_func: Callable):
        """Render a layer with timing."""
        self.budget.begin_phase(layer_name)
        render_func(self.queue)
        self.budget.end_phase(layer_name)
    
    def end_frame(self, particle_count: int = 0):
        """End frame, execute commands, record stats."""
        # Execute render queue
        self.budget.begin_phase('execute')
        self.queue.execute(self.screen)
        self.budget.end_phase('execute')
        
        # Refresh screen
        self.screen.refresh()
        
        # Record stats
        frame_time = self.budget.end_frame()
        self.stats.record_frame(frame_time / 1000, particle_count)
    
    @property
    def quality_level(self) -> float:
        """Current quality level for adaptive rendering."""
        return self.budget.quality_level
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report."""
        return self.stats.get_report()
    
    def draw_debug_overlay(self, x: int = 0, y: int = 0):
        """Draw performance debug overlay."""
        report = self.get_performance_report()
        
        lines = [
            f"FPS: {report['fps']:.1f}",
            f"Frame: {report['avg_ms']:.1f}ms",
            f"P95: {report['p95_ms']:.1f}ms",
            f"Quality: {self.quality_level:.0%}",
            f"Particles: {report['avg_particles']:.0f}",
        ]
        
        for i, line in enumerate(lines):
            self.queue.add_text(x, y + i, line, 7, RenderLayer.DEBUG)


# Performance guard decorator
def guard_performance(max_ms: float = 16.0, fallback: Callable = None):
    """
    Guard against functions taking too long.
    
    If execution exceeds max_ms, calls fallback instead next time.
    """
    skip_next = False
    
    def decorator(func: Callable) -> Callable:
        nonlocal skip_next
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal skip_next
            
            if skip_next and fallback:
                skip_next = False
                return fallback(*args, **kwargs)
            
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            
            if elapsed > max_ms:
                skip_next = True
            
            return result
        return wrapper
    return decorator
