"""Utils for notebooks."""

import tempfile
from pathlib import Path

from graphviz import Digraph
from IPython.core.display import HTML, SVG, display

from stochastic_service_composition.rendering import service_to_graphviz
from stochastic_service_composition.services import Service

_default_svg_style = (
    "display: block; margin-left: auto; margin-right: auto; width: 50%;"
)


def display_svgs(*filenames, style=_default_svg_style):
    svgs = [SVG(filename=f).data for f in filenames]
    joined_svgs = "".join(svgs)
    no_wrap_div = f'<div style="{style}white-space: nowrap">{joined_svgs}</div>'
    display(HTML(no_wrap_div))


def render_service(service: Service, **kwargs):
    digraph = service_to_graphviz(service, **kwargs)
    render_digraph(digraph)


def render_digraph(digraph: Digraph):
    tmp_dir = tempfile.mkdtemp()
    tmp_filepath = str(Path(tmp_dir, "output"))
    digraph.render(tmp_filepath)
    display_svgs(tmp_filepath + ".svg")
