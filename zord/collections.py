from dataclasses import dataclass
from typing import List
import copy

from PIL import ImageDraw

from .core import SceneObject, Scene


@dataclass
class Group:
    """A group of scene objects that can be transformed together"""
    objects: List[SceneObject] = None
    x: float = 0
    y: float = 0
    scale_factor: float = 1.0

    def __post_init__(self):
        if self.objects is None:
            self.objects = []

    def append(self, obj: SceneObject) -> None:
        """Add an object to the group"""
        self.objects.append(obj)

    def move(self, x: float, y: float) -> None:
        """Move the group by the specified amount"""
        self.x += x
        self.y += y
        for obj in self.objects:
            obj.x += x
            obj.y += y

    def scale(self, factor: float) -> None:
        """Scale the group by the specified factor"""
        # Calculate the center point of the group
        if not self.objects:
            return
            
        # Find the center point
        min_x = min(obj.x for obj in self.objects)
        max_x = max(obj.x + getattr(obj, 'size', 0) for obj in self.objects)
        min_y = min(obj.y for obj in self.objects)
        max_y = max(obj.y + getattr(obj, 'size', 0) for obj in self.objects)
        
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        # Apply scaling from center
        for obj in self.objects:
            # Calculate offset from center
            offset_x = obj.x - center_x
            offset_y = obj.y - center_y
            
            # Scale the offset and size
            if hasattr(obj, 'size'):
                obj.size = int(obj.size * factor)
            
            # Update position
            obj.x = center_x + offset_x * factor
            obj.y = center_y + offset_y * factor
        
        self.scale_factor *= factor

    def copy(self) -> "Group":
        """Create a deep copy of the group and its objects"""
        # Create a new group with the same properties
        new_group = Group(x=self.x, y=self.y, scale_factor=self.scale_factor)
        
        # Create a deep copy of each object
        for obj in self.objects:
            # Create a new instance of the same type with copied properties
            new_obj = type(obj)()
            for key, value in obj.__dict__.items():
                if key != '_temporary':  # Skip temporary flag
                    setattr(new_obj, key, copy.deepcopy(value))
            
            # Register the new object with the scene
            if Scene.current_scene is not None:
                Scene.current_scene._register_object(new_obj)
            
            new_group.append(new_obj)
        
        return new_group 