import dataclasses
import os.path
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

__all__ = [
    "get_prompt_template",
    "apply_prompt_template",
]

_env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_prompt_template(prompt_name: str):
    try:
        template = _env.get_template(f"{prompt_name}.md")
        return template
    except FileNotFoundError:
        raise ValueError(f"Template {prompt_name} not found")
    except Exception as e:
        raise ValueError(f"Error loading template {prompt_name}: {e}")


def apply_prompt_template(
    prompt_name: str,
    state: Dict[str, Any],
    configurable: Optional[Dict[str, Any]] = None,
    add_history: bool = True,
    date: bool = True,
) -> list:
    # Convert state to dict for template rendering
    state_vars = deepcopy(state)
    if date:
        state_vars["CURRENT_TIME"] = datetime.now()

    # Add configurable variables
    if configurable:
        state_vars.update(dataclasses.asdict(configurable))

    try:
        template = _env.get_template(f"{prompt_name}.md")
        system_prompt = template.render(**state_vars)
        return (
            [{"role": "system", "content": system_prompt}] + state["messages"]
            if add_history
            else []
        )
    except Exception as e:
        raise ValueError(f"Error applying template {prompt_name}: {type(e)}, {e}")
