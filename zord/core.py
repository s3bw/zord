from PIL import Image, ImageDraw
from typing import List, Dict, Any, Protocol, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
from functools import wraps
import importlib.util
import sys


class Colour:
    RED = "#FF0000"
    BLUE = "#0000FF"
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    GRAY = "#E0E0E0"

class SceneObject(Protocol):
    """Protocol defining what a scene object must implement"""
    _id: str
    _temporary: bool
    
    def get_state(self) -> dict:
        """Return the current state of the object for interpolation"""
        ...
    
    def interpolate(self, last_state: dict, progress: float) -> 'SceneObject':
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
        self._temporary = kwargs.pop('_temporary', False)
        original_init(self, *args, **kwargs)
        if Scene.current_scene is not None and not self._temporary:
            Scene.current_scene._register_object(self)
    
    cls.__init__ = init_wrapper
    return cls

class Scene:
    current_scene = None
    background = Colour.GRAY
    
    def __init__(self):
        self.width = 854
        self.height = 480
        self.frames: List[Image.Image] = []
        self.current_frame = None
        self._objects: Dict[str, SceneObject] = {}
        self.transition_frames = 15
        Scene.current_scene = self
        self._init_frame()
    
    def _register_object(self, obj: SceneObject) -> None:
        self._objects[obj._id] = obj
    
    def _init_frame(self) -> None:
        self.current_frame = Image.new('RGBA', (self.width, self.height), 
                                     (0, 0, 0, 0) if self.background is None else self.background)
        self.draw = ImageDraw.Draw(self.current_frame)
        
        if self.background is not None:
            for i in range(0, self.width, 60):
                self.draw.line([(i, 0), (i, self.height)], fill="#D0D0D0", width=1)
            for i in range(0, self.height, 60):
                self.draw.line([(0, i), (self.width, i)], fill="#D0D0D0", width=1)
    
    def play(self) -> None:
        if not hasattr(self, 'last_frame_state'):
            self.last_frame_state = {}
        
        # Store current state
        current_state = {}
        for obj in self._objects.values():
            current_state[obj._id] = obj.get_state()
        
        # Generate transition frames
        for t in range(self.transition_frames):
            progress = t / (self.transition_frames - 1)
            self._init_frame()
            
            # Interpolate and render objects
            for obj in self._objects.values():
                last_state = self.last_frame_state.get(obj._id, obj.get_state())
                interpolated = obj.interpolate(last_state, progress)
                interpolated.render(self.draw)
            
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
        return None 