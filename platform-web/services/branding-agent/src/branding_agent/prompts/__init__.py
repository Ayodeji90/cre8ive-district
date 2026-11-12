from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_prompt(template_name: str, **variables: object) -> str:
    template = _env.get_template(f"{template_name}.j2")
    return template.render(**variables)
