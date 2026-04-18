from dataclasses import dataclass
from typing import Optional

from PIL import ImageDraw, ImageFont

from .core import Colour, Scene, scene_object


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
class Rect:
    h: int = 50
    w: int = 50
    label: str = ""
    background: str = Colour.WHITE
    outline: str = Colour.BASE
    x: float = 0
    y: float = 0
    radius: int = 3

    def get_state(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "background": self.background,
            "h": self.h,
            "w": self.w,
        }

    def interpolate(self, last_state: dict, progress: float) -> "Rect":
        return Rect(
            w=int(interpolate_position(last_state["w"], self.w, progress)),
            h=int(interpolate_position(last_state["h"], self.h, progress)),
            label=self.label,
            background=interpolate_color(
                last_state["background"], self.background, progress
            ),
            x=interpolate_position(last_state["x"], self.x, progress),
            y=interpolate_position(last_state["y"], self.y, progress),
            _temporary=True,
        )

    def render(self, draw: ImageDraw.Draw) -> None:
        draw.rounded_rectangle(
            [(self.x, self.y), (self.x + self.w, self.y + self.h)],
            radius=self.radius,
            fill=self.background,
            outline=self.outline,
        )
        if self.label:
            font = ImageFont.truetype("Courier", 16)
            bbox = font.getbbox(self.label)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text(
                (self.x + (self.w - w) / 2, self.y + (self.h - h) / 2),
                self.label,
                fill=Colour.BASE,
                font=font,
            )


@scene_object
@dataclass
class Indicator:
    size: int = 20
    x: float = 0
    y: float = 0
    label: str = ""
    target_x: float = 0
    target_y: float = 0
    fill: str = Colour.BASE
    # Add font size
    _temporary: bool = True  # Start as temporary

    def get_state(self) -> dict:
        return {"x": self.target_x, "y": self.target_y}

    def interpolate(self, last_state: dict, progress: float) -> "Indicator":
        interpolated = Indicator(size=self.size, label=self.label, _temporary=True)
        interpolated.x = interpolate_position(last_state["x"], self.target_x, progress)
        interpolated.y = interpolate_position(last_state["y"], self.target_y, progress)
        return interpolated

    def start_at(self, target) -> None:
        if hasattr(target, "x") and hasattr(target, "y"):
            self.x = target.x + target.h / 2
            self.y = target.y - self.size - 5
            self.target_x = self.x
            self.target_y = self.y
            self._temporary = False  # Make permanent after positioning
            if Scene.current_scene is not None:
                Scene.current_scene._register_object(self)

    def point_at(self, target) -> None:
        if hasattr(target, "x") and hasattr(target, "y"):
            self.target_x = target.x + target.h / 2
            self.target_y = target.y - self.size - 5

    def render(self, draw: ImageDraw.Draw) -> None:
        points = [
            (self.x, self.y),
            (self.x - self.size / 2, self.y - self.size),
            (self.x + self.size / 2, self.y - self.size),
        ]
        draw.polygon(points, fill=Colour.BASE, outline=Colour.WHITE)
        if self.label:
            font = ImageFont.truetype("Courier", 28)
            bbox = font.getbbox(self.label)
            h = bbox[3] - bbox[1]
            x = self.x - (len(self.label) / 2) - 8
            y = self.y + (self.size - h - 90) / 2
            outline_width = 2

            # Draw outline by rendering the text multiple times with offsets
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:  # Skip the center position
                        draw.text(
                            (x + dx, y + dy),
                            self.label,
                            fill=Colour.WHITE,
                            font=font,
                        )

            draw.text(
                (x, y),
                self.label,
                fill=Colour.BASE,
                font=font,
            )


@scene_object
@dataclass
class Wire:
    start_object: Optional[object] = None
    end_object: Optional[object] = None
    start_arrow: bool = False
    end_arrow: bool = False
    color: str = Colour.BASE
    _temporary: bool = True

    def get_state(self) -> dict:
        size_x = self.start_object.w
        size_y = self.start_object.h
        end_x = self.end_object.w
        end_y = self.end_object.h
        return {
            "start_x": (self.start_object.x + size_x / 2 if self.start_object else 0),
            "start_y": (self.start_object.y + size_y / 2 if self.start_object else 0),
            "end_x": (self.end_object.x + end_x / 2 if self.end_object else 0),
            "end_y": (self.end_object.y + end_y / 2 if self.end_object else 0),
        }

    def interpolate(self, last_state: dict, progress: float) -> "Wire":
        interpolated = Wire(
            start_object=self.start_object,
            end_object=self.end_object,
            start_arrow=self.start_arrow,
            end_arrow=self.end_arrow,
            color=self.color,
            _temporary=True,
        )
        return interpolated

    def connect(self, start_obj, end_obj) -> None:
        self.start_object = start_obj
        self.end_object = end_obj
        self._temporary = False
        if Scene.current_scene is not None:
            Scene.current_scene._register_object(self)

    def _get_edge_points(self, obj, is_start: bool) -> tuple[float, float]:
        """Calculate the point where the wire should connect to the object's edge"""
        center_x = obj.x + obj.w / 2
        center_y = obj.y + obj.h / 2

        # Get the center point of the other object
        other = self.end_object if is_start else self.start_object
        other_center_x = other.x + other.w / 2
        other_center_y = other.y + other.h / 2

        # Calculate the midpoint for the vertical segment
        mid_x = (center_x + other_center_x) / 2

        # Determine which edge to connect to based on the relative positions
        if is_start:
            # For start object
            if mid_x > center_x:
                # Connect to right edge
                return obj.x + obj.w + 2, center_y
            else:
                # Connect to left edge
                return obj.x, center_y
        else:
            # For end object
            if mid_x > center_x:
                # Connect to left edge
                return obj.x, center_y
            else:
                # Connect to right edge
                return obj.x - 2, center_y

    def render(self, draw: ImageDraw.Draw) -> None:
        if not self.start_object or not self.end_object:
            return

        # Get edge connection points
        start_x, start_y = self._get_edge_points(self.start_object, True)
        end_x, end_y = self._get_edge_points(self.end_object, False)

        # Calculate the center point
        center_x = (start_x + end_x) / 2

        # Draw the three segments
        # First horizontal segment
        draw.line([(start_x, start_y), (center_x, start_y)], fill=self.color)
        # Vertical segment
        draw.line([(center_x, start_y), (center_x, end_y)], fill=self.color)
        # Second horizontal segment
        draw.line([(center_x, end_y), (end_x, end_y)], fill=self.color)

        # Draw arrows if needed
        arrow_size = 6
        if self.start_arrow:
            points = [
                (start_x, start_y),
                (start_x + arrow_size, start_y - arrow_size),
                (start_x + arrow_size, start_y + arrow_size),
            ]
            draw.polygon(points, fill=self.color)

        if self.end_arrow:
            points = [
                (end_x, end_y),
                (end_x - arrow_size, end_y - arrow_size),
                (end_x - arrow_size, end_y + arrow_size),
            ]
            draw.polygon(points, fill=self.color)


@scene_object
@dataclass
class Circle:
    wire: Optional[Wire] = None
    size: int = 10
    color: str = Colour.BASE
    progress: float = 0.0  # 0.0 to 1.0
    speed: float = 0.02  # How much to increment progress per frame
    start_progress: float = 0.0  # Where to start on the wire (0.0 to 1.0)
    _temporary: bool = True

    def get_state(self) -> dict:
        return {"progress": self.progress}

    def interpolate(self, last_state: dict, progress: float) -> "Circle":
        # Calculate the target progress, ensuring it's always forward
        target_progress = self.progress
        last_progress = last_state["progress"]

        # Handle the case where we're near the loop point
        if target_progress < last_progress:
            # If we've looped around, add 1.0 to the target
            target_progress += 1.0
        elif last_progress > 0.9 and target_progress < 0.1:
            # If we're about to loop, adjust last_progress
            last_progress -= 1.0

        # Interpolate between last progress and target progress
        interpolated_progress = interpolate_position(
            last_progress, target_progress, progress
        )

        # Normalize back to 0-1 range
        if interpolated_progress >= 1.0:
            interpolated_progress -= 1.0
        elif interpolated_progress < 0.0:
            interpolated_progress += 1.0

        return Circle(
            wire=self.wire,
            size=self.size,
            color=self.color,
            progress=interpolated_progress,
            speed=self.speed,
            start_progress=self.start_progress,
            _temporary=True,
        )

    def get_frames_to_complete(self) -> int:
        """Calculate how many frames it will take to complete one full path"""
        if self.speed <= 0:
            return 0
        return int(1.0 / self.speed + 0.5)

    def attach_to_wire(self, wire: Wire) -> None:
        """Attach this circle to a wire for animation"""
        self.wire = wire
        self.progress = self.start_progress  # Set initial progress to start_progress
        self._temporary = False
        if Scene.current_scene is not None:
            Scene.current_scene._register_object(self)

    def _calculate_position(self) -> tuple[float, float]:
        """Calculate the circle's position along the wire path"""
        if not self.wire:
            return (0, 0)

        # Get wire's path points
        start_x, start_y = self.wire._get_edge_points(self.wire.start_object, True)
        end_x, end_y = self.wire._get_edge_points(self.wire.end_object, False)
        center_x = (start_x + end_x) / 2

        # Check if the wire is straight (no vertical bend)
        if abs(start_y - end_y) < 1:  # Small threshold for straightness
            # For straight wires, just interpolate directly from start to end
            x = start_x + (end_x - start_x) * self.progress
            y = start_y
        else:
            # For bent wires, use the three-segment path
            if self.progress <= 0.33:  # First horizontal segment
                segment_progress = self.progress * 3
                x = start_x + (center_x - start_x) * segment_progress
                y = start_y
            elif self.progress <= 0.66:  # Vertical segment
                segment_progress = (self.progress - 0.33) * 3
                x = center_x
                y = start_y + (end_y - start_y) * segment_progress
            else:  # Second horizontal segment
                segment_progress = (self.progress - 0.66) * 3
                x = center_x + (end_x - center_x) * segment_progress
                y = end_y

        return (x, y)

    def update(self) -> None:
        """Update the circle's position for animation"""
        if not self.wire:
            return

        # Update progress based on absolute time rather than relative position
        self.progress = (self.progress + self.speed) % 1.0

    def render(self, draw: ImageDraw.Draw) -> None:
        if not self.wire:
            return

        # Calculate current position
        x, y = self._calculate_position()

        # Draw circle
        radius = self.size // 2
        draw.ellipse(
            [(x - radius, y - radius), (x + radius, y + radius)], fill=self.color
        )


@scene_object
@dataclass
class Text:
    text: str = ""
    x: float = 0
    y: float = 0
    size: int = 24
    color: str = Colour.BASE
    outline_color: str = Colour.WHITE
    outline_width: int = 2
    _temporary: bool = True

    def get_state(self) -> dict:
        return {"text": self.text, "x": self.x, "y": self.y}

    def interpolate(self, last_state: dict, progress: float) -> "Text":
        return Text(
            text=self.text,
            x=interpolate_position(last_state["x"], self.x, progress),
            y=interpolate_position(last_state["y"], self.y, progress),
            size=self.size,
            color=self.color,
            outline_color=self.outline_color,
            outline_width=self.outline_width,
            _temporary=False,
        )

    def render(self, draw: ImageDraw.Draw) -> None:
        font = ImageFont.truetype("Courier", self.size)

        # Draw outline by rendering the text multiple times with offsets
        for dx in range(-self.outline_width, self.outline_width + 1):
            for dy in range(-self.outline_width, self.outline_width + 1):
                if dx != 0 or dy != 0:  # Skip the center position
                    draw.text(
                        (self.x + dx, self.y + dy),
                        self.text,
                        fill=self.outline_color,
                        font=font,
                    )

        # Draw the main text on top
        draw.text((self.x, self.y), self.text, fill=self.color, font=font)
