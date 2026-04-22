import importlib.util
import sys
import uuid
from functools import wraps
from typing import Dict, List, Optional, Protocol

from PIL import Image, ImageDraw


class Colour:
    PRIMARY = "#FF5858"
    ACCENT = "#6CFFDD"
    SHINY = "#ff8000"
    BASE = "#2A2A2A"
    WHITE = "#FFFFFF"
    BLACK = "#000000"


class SceneObject(Protocol):
    """Protocol defining what a scene object must implement"""

    _id: str
    _temporary: bool

    def get_state(self) -> dict:
        """Return the current state of the object for interpolation"""
        ...

    def interpolate(self, last_state: dict, progress: float) -> "SceneObject":
        """Create an interpolated version of this object"""
        ...

    def render(self, draw: ImageDraw.Draw) -> None:
        """Render the object to the given ImageDraw context"""
        ...


def scene_object(cls):
    """Class decorator to handle scene object registration"""
    original_init = cls.__init__

    @wraps(original_init)
    def init_wrapper(self, *args, **kwargs):
        self._id = str(uuid.uuid4())
        _temporary = kwargs.pop("_temporary", False)
        original_init(self, *args, **kwargs)
        # Set _temporary AFTER original_init so dataclass defaults don't overwrite
        self._temporary = _temporary
        if Scene.current_scene is not None and not self._temporary:
            Scene.current_scene._register_object(self)

    cls.__init__ = init_wrapper
    return cls


class Scene:
    current_scene = None
    background: Colour = None
    width = 854
    height = 480

    def __init__(self):
        self.frames: List[Image.Image] = []
        self.current_frame = None
        self._objects: Dict[str, SceneObject] = {}
        self.transition_frames = 10
        Scene.current_scene = self
        self._init_frame()
        self.last_frame_state = {}

    def vertical_center(self, size) -> float:
        return self.height // 2 - size // 2  # Center vertically

    def horizontal_center(self, size) -> float:
        return self.width // 2 - size // 2

    def construct(self):
        """Override this method to create your scene"""
        pass

    def _register_object(self, obj: SceneObject) -> None:
        if obj._id not in self._objects:
            self._objects[obj._id] = obj
            self.last_frame_state[obj._id] = obj.get_state()

    def _init_frame(self) -> None:
        # Create frame with background
        self.current_frame = Image.new(
            "RGBA",
            (self.width, self.height),
            (0, 0, 0, 0) if self.background is None else self.background,
        )
        self.draw = ImageDraw.Draw(self.current_frame)

    def _render_objects(self, objects: List[SceneObject]) -> None:
        """Render a list of objects to the current frame"""
        for obj in objects:
            obj.render(self.draw)

    def play(self) -> None:
        # Store current state
        current_state = {}
        for obj in self._objects.values():
            current_state[obj._id] = obj.get_state()

        # Generate transition frames
        for t in range(self.transition_frames):
            progress = t / (self.transition_frames - 1)
            self._init_frame()

            # Interpolate and render objects
            interpolated_objects = []
            for obj in self._objects.values():
                last_state = self.last_frame_state.get(obj._id, obj.get_state())
                interpolated = obj.interpolate(last_state, progress)
                interpolated_objects.append(interpolated)

            # Render only the interpolated objects
            self._render_objects(interpolated_objects)
            self.frames.append(self.current_frame.copy())

        # Update last frame state
        self.last_frame_state = current_state

    def wait(self, seconds: float) -> None:
        frames_to_add = int(seconds * 30)  # Assuming 30 fps
        for _ in range(frames_to_add):
            self.frames.append(self.current_frame.copy())

    def save(self, filename: str) -> None:
        if not self.frames:
            return

        self.frames[0].save(
            filename,
            save_all=True,
            append_images=self.frames[1:],
            duration=33,
            loop=0,
            transparency=0,
            disposal=2,
        )


def load_scene(file_path: str) -> Optional[Scene]:
    """Dynamically load a scene from a Python file"""
    try:
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location("scene_module", file_path)
        if not spec or not spec.loader:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules["scene_module"] = module
        spec.loader.exec_module(module)

        # Find the Scene subclass
        scene_class = None
        for item in dir(module):
            obj = getattr(module, item)
            if isinstance(obj, type) and issubclass(obj, Scene) and obj != Scene:
                scene_class = obj
                break

        if not scene_class:
            return None

        # Create and return the scene instance
        scene = scene_class()
        scene.construct()
        return scene

    except Exception as e:
        print(f"Error loading scene: {e}")
        raise
