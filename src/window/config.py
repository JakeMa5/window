from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from framework import ConfigError, ConfigSection
from gfx import DEFAULT_CLEAR_COLOUR

if TYPE_CHECKING:
    from framework import PluginContext

SCOPE = "shared"

__all__ = ["WindowConfig", "WindowSection"]

_COLOUR_COMPONENTS: Final = 4


@dataclass(frozen=True, slots=True)
class WindowSection(ConfigSection):
    title: str = "Snowdon"
    width: int = 1280
    height: int = 720
    vsync: bool = True
    clear_colour: tuple[float, ...] = DEFAULT_CLEAR_COLOUR

    def validate(self, path: str = "") -> None:
        if self.width <= 0 or self.height <= 0:
            raise ConfigError(f"{path}: width and height must be positive.")
        if len(self.clear_colour) != _COLOUR_COMPONENTS:
            raise ConfigError(f"{path}.clear_colour must have four components.")
        if not all(0.0 <= component <= 1.0 for component in self.clear_colour):
            raise ConfigError(f"{path}.clear_colour components must be within 0.0 and 1.0.")


class WindowConfig:
    def build(self, ctx: PluginContext) -> None:
        ctx.add_config_section("window", WindowSection)
