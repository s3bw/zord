import os
import time

import click
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .core import load_scene


class SceneHandler(FileSystemEventHandler):
    def __init__(self, scene_file):
        self.scene_file = scene_file
        self.last_modified = 0

    def on_modified(self, event):
        if event.src_path == self.scene_file:
            # Debounce multiple events
            current_time = time.time()
            if current_time - self.last_modified > 1:
                self.last_modified = current_time
                click.echo(f"Changes detected in {self.scene_file}, re-rendering...")
                render_scene(self.scene_file)


def render_scene(scene_file: str) -> bool:
    if not os.path.exists(scene_file):
        click.echo(f"Error: File {scene_file} does not exist")
        return False

    scene = load_scene(scene_file)
    if not scene:
        click.echo(f"Error: Could not load scene from {scene_file}")
        return False

    output_file = os.path.splitext(scene_file)[0] + ".gif"
    scene.save(output_file)
    click.echo(f"Rendered scene to {output_file}")
    return True


@click.group()
def cli():
    """Zord animation renderer"""
    pass


@cli.command()
@click.argument("scene_file")
def render(scene_file):
    """Render a scene to GIF"""
    render_scene(scene_file)


@cli.command()
@click.argument("scene_file")
def watch(scene_file):
    """Watch a scene file and re-render on changes"""
    if not os.path.exists(scene_file):
        click.echo(f"Error: File {scene_file} does not exist")
        return

    # Initial render
    render_scene(scene_file)

    # Set up file watcher
    event_handler = SceneHandler(os.path.abspath(scene_file))
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(os.path.abspath(scene_file)))
    observer.start()

    click.echo(f"Watching {scene_file} for changes... Press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    cli()
