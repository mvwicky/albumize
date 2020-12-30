from pathlib import Path
from typing import Optional, Tuple

import click

from .const import DEFAULT_EXTS
from .core import env, find_images

dir_only = click.Path(dir_okay=True, exists=True, resolve_path=True, file_okay=False)


@click.command(name="albumize", context_settings={"max_content_width": 100})
@click.option(
    "--recursive/--not-recursive",
    "-r/ ",
    default=False,
    help="Search subdirectories for images.",
    show_default=True,
)
@click.option("--output-dir", "-o", type=click.Path(resolve_path=True), default=".")
@click.option("--output-name", "-n", default=None)
@click.option("--min-images", type=click.IntRange(1), default=1)
@click.argument("src", type=dir_only)
@click.argument("exts", nargs=-1)
def albumize(
    src: str,
    exts: Tuple[str],
    recursive: bool,
    output_dir: str,
    output_name: Optional[str],
    min_images: int,
) -> None:
    exts = exts or DEFAULT_EXTS
    src, output_dir = Path(src), Path(output_dir)
    if output_name is None:
        output_name = ".".join([src.name, "html"])
    output_file = output_dir / output_name
    image_files = find_images(src, exts, recursive)
    if len(image_files) < min_images:
        raise click.ClickException(
            "Directory did not contain enough images. "
            f"(found: {len(image_files)}, needed at least {min_images})"
        )
    click.secho(f"Found {len(image_files)} images", fg="green")

    template = env.get_template("base.jinja")
    context = {"title": f"Album of {src}", "images": image_files}
    print(template.name, src, exts)
    print(repr(output_file))
    template.stream(context).dump(str(output_file))


def cli():
    albumize(auto_envvar_prefix="ALBUMIZE")
