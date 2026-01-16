"""Rendering Engine Module - Performance-aware frame rendering."""

from engine.rendering.core import (
    RenderEngine, RenderStats, FrameBudget, RenderQueue,
    RenderCommand, RenderLayer, profile_function, guard_performance
)

__all__ = [
    'RenderEngine', 'RenderStats', 'FrameBudget', 'RenderQueue',
    'RenderCommand', 'RenderLayer', 'profile_function', 'guard_performance',
]
