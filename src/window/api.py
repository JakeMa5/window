from __future__ import annotations

from typing import TYPE_CHECKING, Final, Protocol

from framework import capability

if TYPE_CHECKING:
    from collections.abc import Sequence

    from gfx import RenderPass, Unregister

__all__ = ["DISPLAY", "RENDER_GRAPH", "Display", "RenderGraph"]

DISPLAY: Final = "snowdon.display"
RENDER_GRAPH: Final = "snowdon.render_graph"


@capability(DISPLAY)
class Display(Protocol):
    """The window the game is drawn into."""

    @property
    def size(self) -> tuple[int, int]:
        """The drawing surface's size in physical pixels."""
        ...

    @property
    def logical_size(self) -> tuple[int, int]: ...
    @property
    def format(self) -> str:
        """The surface's wgpu texture format."""
        ...

    @property
    def title(self) -> str: ...
    def set_title(self, title: str) -> None: ...
    def resize(self, width: int, height: int) -> None: ...
    def close(self) -> None: ...


@capability(RENDER_GRAPH)
class RenderGraph(Protocol):
    def add_pass(self, render_pass: RenderPass, *, order: int = 0) -> Unregister:
        """Registers a pass; lower ``order`` draws first."""
        ...

    def remove_pass(self, render_pass: RenderPass) -> bool: ...

    @property
    def clear_colour(self) -> tuple[float, ...]: ...

    def set_clear_colour(self, colour: Sequence[float]) -> None: ...


