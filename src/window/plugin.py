from __future__ import annotations

from typing import TYPE_CHECKING, Final

from framework import App, Stage, get_logger
from gfx import GraphicsDevice, GraphicsError, Renderer, RenderHandlers, Window

from .api import Display, RenderGraph
from .config import WindowSection

if TYPE_CHECKING:
    from collections.abc import Sequence

    from framework import Frame, PluginContext
    from gfx import RenderPass, Unregister

SCOPE = "runtime"
HEADLESS = False

__all__ = ["WindowPlugin"]

_log: Final = get_logger(__name__)

_OWNER: Final = "window"


class WindowDisplay:
    __slots__ = ("_window",)

    def __init__(self, window: Window) -> None:
        self._window = window

    @property
    def size(self) -> tuple[int, int]:
        return self._window.size

    @property
    def logical_size(self) -> tuple[int, int]:
        return self._window.logical_size

    @property
    def format(self) -> str:
        return self._window.format

    @property
    def title(self) -> str:
        return self._window.title

    def set_title(self, title: str) -> None:
        self._window.set_title(title)

    def resize(self, width: int, height: int) -> None:
        self._window.resize(width, height)

    def close(self) -> None:
        self._window.close()


class WindowRenderGraph:
    __slots__ = ("_handlers", "_renderer")

    def __init__(self, handlers: RenderHandlers, renderer: Renderer) -> None:
        self._handlers = handlers
        self._renderer = renderer

    def add_pass(self, render_pass: RenderPass, *, order: int = 0) -> Unregister:
        return self._handlers.register(render_pass, order=order, owner=_OWNER)

    def remove_pass(self, render_pass: RenderPass) -> bool:
        return self._handlers.unregister(render_pass)

    @property
    def clear_colour(self) -> tuple[float, ...]:
        return self._renderer.clear_colour

    def set_clear_colour(self, colour: Sequence[float]) -> None:
        self._renderer.clear_colour = colour


class WindowPlugin:
    __slots__ = ("_device", "_renderer", "_window")

    def __init__(self) -> None:
        self._window: Window | None = None
        self._device: GraphicsDevice | None = None
        self._renderer: Renderer | None = None

    def build(self, ctx: PluginContext) -> None:
        settings = ctx.config_section(WindowSection)
        window = Window(settings, max_fps=ctx.config.runtime.max_fps)
        try:
            device = GraphicsDevice(canvas=window.canvas)
        except GraphicsError:
            window.dispose()
            raise

        window.configure(device)
        handlers = RenderHandlers()
        renderer = Renderer(device, handlers, settings.clear_colour)

        self._window = window
        self._device = device
        self._renderer = renderer

        ctx.register_service(window)
        ctx.register_service(device)
        ctx.register_service(handlers)
        ctx.register_service(renderer)
        ctx.provide(Display, WindowDisplay(window))
        ctx.provide(RenderGraph, WindowRenderGraph(handlers, renderer))

        ctx.add_system(Stage.PRE_UPDATE, self._pump, order=-1000)
        ctx.add_system(Stage.DRAW, self._draw, order=1000)

    def teardown(self, ctx: PluginContext) -> None:
        del ctx
        self._renderer = None
        self._device = None
        self._window = None

    def _pump(self, frame: Frame) -> None:
        window = self._window
        if window is not None and window.poll():
            app = frame.find(App)
            if app is not None:
                app.stop()

    def _draw(self, frame: Frame) -> None:
        window = self._window
        renderer = self._renderer
        if window is None or renderer is None:
            return

        alpha = frame.alpha

        def render_now() -> None:
            target = window.acquire()
            if target is None:
                return
            renderer.render(target, window.size, alpha, target_format=window.format)

        window.request_draw(render_now)
        window.force_draw()
