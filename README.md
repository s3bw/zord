# Zord Animation Library

A Python library for creating animated GIFs from scene descriptions.

## Installation

```bash
pip install -e .
```

## Usage

Create a scene file (e.g., `example.py`):

```python
from zord import Scene, Square, Indicator, Animate, Colour

class BinarySearch(Scene):
    start = Animate.FADE_IN
    end = Animate.FADE_OUT

    def construct(self):
        s = Square(label="a")
        row = [s] * 15
        arrow = Indicator()

        row[7].background = Colour.BLUE
        arrow.point_at(row[7])
        self.play()
        self.wait(1)

        row[7].background = Colour.RED
        arrow.point_at(row[9])
        row[9].background = Colour.RED
        self.play()
```

### Commands

1. Render a scene:
```bash
zord render example.py
```

2. Watch for changes and auto-render:
```bash
zord watch example.py
```

## Features

- Create animated GIFs from Python scene descriptions
- Live reload support with the watch command
- Simple API for creating animations
- Support for basic shapes, colors, and animations 