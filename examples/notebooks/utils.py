"""Utils for notebooks."""

import tempfile
from pathlib import Path

from graphviz import Digraph
from IPython.core.display import HTML, SVG, display
from mdp_dp_rl.processes.mdp import MDP

from stochastic_service_composition.rendering import service_to_graphviz, target_to_graphviz, mdp_to_graphviz
from stochastic_service_composition.services import Service
from stochastic_service_composition.target import Target

_default_svg_style = (
    "display: block; margin-left: auto; margin-right: auto; width: 50%;"
)


def display_svgs(*filenames, style=_default_svg_style):
    svgs = [SVG(filename=f).data for f in filenames]
    joined_svgs = "".join(svgs)
    no_wrap_div = f'<div style="{style}white-space: nowrap">{joined_svgs}</div>'
    display(HTML(no_wrap_div))


def render_service(service: Service, style: str = _default_svg_style):
    digraph = service_to_graphviz(service)
    render_digraph(digraph, style)


def render_target(target: Target, style: str = _default_svg_style):
    digraph = target_to_graphviz(target)
    render_digraph(digraph, style)


def render_composition_mdp(mdp: MDP, style: str = _default_svg_style):
    digraph = mdp_to_graphviz(mdp)
    render_digraph(digraph, style)


def render_digraph(digraph: Digraph, style: str):
    tmp_dir = tempfile.mkdtemp()
    tmp_filepath = str(Path(tmp_dir, "output"))
    digraph.render(tmp_filepath)
    display_svgs(tmp_filepath + ".svg", style=style)
