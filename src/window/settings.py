from __future__ import annotations

from typing import TYPE_CHECKING

from editor.shell.api import FieldHint

if TYPE_CHECKING:
    from framework import PluginContext

SCOPE = "editor"

__all__ = ["WindowSettings"]


class WindowSettings:
    def build(self, ctx: PluginContext) -> None:
        ctx.add_extension(FieldHint, FieldHint("window", "width", minimum=1, maximum=7680))
        ctx.add_extension(FieldHint, FieldHint("window", "height", minimum=1, maximum=4320))
        ctx.add_extension(FieldHint, FieldHint("window", "vsync", label="V-sync"))
        ctx.add_extension(
            FieldHint,
            FieldHint(
                "window", "clear_colour", colour=True, help="The colour the frame starts from."
            ),
        )
