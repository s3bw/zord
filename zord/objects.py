from dataclasses import dataclass

from PIL import ImageDraw, ImageFont

from .core import Colour, scene_object


def interpolate_color(start_color: str, end_color: str, progress: float) -> str:
    """Helper function to interpolate between two colors"""
    # Handle transparency
    if start_color is None:
        start_color = "#00000000"
    if end_color is None:
        end_color = "#00000000"

    # Convert 6-digit hex to 8-digit (with alpha)
    if len(start_color) == 7:
        start_color = start_color + "FF"
    if len(end_color) == 7:
        end_color = end_color + "FF"

    # Extract RGBA values
    start = tuple(int(start_color[i : i + 2], 16) for i in (1, 3, 5, 7))
    end = tuple(int(end_color[i : i + 2], 16) for i in (1, 3, 5, 7))
    current = tuple(int(start[i] + (end[i] - start[i]) * progress) for i in range(4))
    return f"#{current[0]:02x}{current[1]:02x}{current[2]:02x}{current[3]:02x}"


def interpolate_position(start: float, end: float, progress: float) -> float:
    """Helper function to interpolate between two positions"""
    return start + (end - start) * progress


@scene_object
@dataclass
class Square:
    size: int = 50
    label: str = ""
    background: str = Colour.WHITE
    outline: str = Colour.BLACK
    x: float = 0
    y: float = 0

    def get_state(self) -> dict:
        return {"x": self.x, "y": self.y, "background": self.background}

    def interpolate(self, last_state: dict, progress: float) -> "Square":
        return Square(
            size=self.size,
            label=self.label,
            background=interpolate_color(
                last_state["background"], self.background, progress
            ),
            x=interpolate_position(last_state["x"], self.x, progress),
            y=interpolate_position(last_state["y"], self.y, progress),
            _temporary=True,
        )

    def render(self, draw: ImageDraw.Draw) -> None:
        draw.rectangle(
            [(self.x, self.y), (self.x + self.size, self.y + self.size)],
            fill=self.background,
            outline=self.outline,
        )
        if self.label:
            font = ImageFont.load_default()
            bbox = font.getbbox(self.label)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text(
                (self.x + (self.size - w) / 2, self.y + (self.size - h) / 2),
                self.label,
                fill=Colour.BLACK,
                font=font,
            )


@scene_object
@dataclass
class Indicator:
    size: int = 20
    x: float = 0
    y: float = 0
    target_x: float = 0
    target_y: float = 0

    def get_state(self) -> dict:
        return {"x": self.target_x, "y": self.target_y}

    def interpolate(self, last_state: dict, progress: float) -> "Indicator":
        interpolated = Indicator(size=self.size, _temporary=True)
        interpolated.x = interpolate_position(last_state["x"], self.target_x, progress)
        interpolated.y = interpolate_position(last_state["y"], self.target_y, progress)
        return interpolated

    def point_at(self, target) -> None:
        if hasattr(target, "x") and hasattr(target, "y"):
            self.target_x = target.x + target.size / 2
            self.target_y = target.y - self.size - 5

    def render(self, draw: ImageDraw.Draw) -> None:
        points = [
            (self.x, self.y),
            (self.x - self.size / 2, self.y - self.size),
            (self.x + self.size / 2, self.y - self.size),
        ]
        draw.polygon(points, fill=Colour.BLACK)
