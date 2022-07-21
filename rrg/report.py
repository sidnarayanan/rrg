from abc import ABC
from pathlib import Path
from shutil import rmtree
from uuid import uuid4

from dominate import document
from dominate import tags as D
from dominate.util import text, raw
from loguru import logger
from markdown2 import markdown

try:
    from matplotlib import pyplot as plt
except ImportError:

    class plt:
        class Figure:
            ...


try:
    from plotly import graph_objects as go
except ImportError:

    class go:
        class Figure:
            ...


__all__ = [
    "Report",
    "Cols1",
    "Cols2",
    "Cols3",
    "Cols",
    "SectionHeader",
    "Divider",
    "Markdown",
    "Text",
    "HTML",
    "Plotly",
    "Pyplot",
]


def _Container(*args, **kwargs):
    return D.div(*args, _class="container-fluid", **kwargs)


def _Col(*args, c, **kwargs):
    return D.div(*args, _class="col-" + c, **kwargs)


def _Col12(*args, **kwargs):
    return _Col(*args, c="xl-12", **kwargs)


def _Row(*args, **kwargs):
    return D.div(*args, _class="row", **kwargs)


class Report:
    def __init__(self, title: str = "Generated report", plotly_thumbnails: bool = True, path: str = None, toc_width: int = 2):
        self._setup_path(path)
        self.title = title
        self._plotly_thumbnails = plotly_thumbnails
        self._toc_width = toc_width

        self._elements = []
        self._toc = []

    def _setup_path(self, path: str):
        if path is None:
            return
        self._html_path = Path(path).expanduser()
        self._dir_path = self._html_path.parent
        file_name = self._html_path.stem
        self._assets_path = self._dir_path.joinpath("assets").joinpath(file_name)

    def add_element(self, element):
        if isinstance(element, SectionHeader):
            self._toc.append((element._name, element._id))

        if not isinstance(element, _NCols):
            element = Cols1([element])

        self._elements.append(element)

    def add_elements(self, *elements):
        for el in elements:
            self.add_element(el)

    def write(self, path: str = None):
        self._setup_path(path)
        if not hasattr(self, "_html_path"):
            raise RuntimeError("Trying to call Report.write() without specifying an output path.")

        doc = document(title=self.title)
        with doc.head:
            for stylesheet in [
                "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css",
                "https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/minty/bootstrap.min.css",
            ]:
                D.link(rel="stylesheet", href=stylesheet)
            for script in [
                "https://polyfill.io/v3/polyfill.min.js?features=es6",
            ]:
                D.script(rel="script", src=script)
            D.script(
                rel="script",
                src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
                id="MathJax-script",
                _async=True,
            )

        with doc.body:
            with _Container():
                with _Row():
                    with _Col12():
                        D.h1(self.title)
                        Divider(strength=7)._get_html()

        if self._assets_path.exists():
            rmtree(self._assets_path)
        self._assets_path.mkdir(exist_ok=True, parents=True)

        with doc.body:
            if self._toc:
                with _Container():
                    with _Row():
                        with _Col(c=f"md-{self._toc_width}"):
                            for name, id_ in self._toc:
                                D.p(D.a(name, href="#" + id_))
                        with _Col(c=f"lg-{12-self._toc_width}"):
                            self._write_elements()
            else:
                self._write_elements()

        with open(self._html_path, mode="w") as fhtml:
            fhtml.write(str(doc))

        logger.info(f"Wrote report to {str(self._html_path)}")

    def _write_elements(self):
        config = dict(
            assets_path=self._assets_path,
            plotly_thumbnails=self._plotly_thumbnails,
        )
        for element in self._elements:
            element._get_html(config)


class _NCols(ABC):
    n_cols: int = None
    col_cls: str = None

    def __init__(self, elements):
        if not isinstance(elements, dict):
            elements = {f"({i})": el for i, el in enumerate(elements)}
        self.elements = [_resolve_element(el, tag) for tag, el in elements.items()]

    def _get_html(self, config: dict):
        rows = []
        for i, el in enumerate(self.elements):
            try:
                el_html = el._get_html(config)
            except AttributeError:
                el_html = str(el)
            rows.append(_Col(el_html, c=self.col_cls))

        rows = _Row(rows)
        container = _Container(rows)
        return container


class Cols1(_NCols):
    n_cols = 1
    col_cls = "xl-12"


class Cols3(_NCols):
    n_cols = 3
    col_cls = "lg-4"


class Cols2(_NCols):
    n_cols = 2
    col_cls = "lg-6"


class Cols(_NCols):
    def __init__(self, elements):
        N = self.n_cols = len(elements)

        if N == 1:
            c = "xl-12"
        elif N == 2:
            c = "lg-6"
        elif N == 3:
            c = "lg-4"
        elif N == 4:
            c = "md-3"
        elif N < 7:
            c = "sm-2"
        else:
            c = "sm-1"
        self.col_cls = c

        super().__init__(elements)


class Divider:
    def __init__(self, strength: int = 5):
        self.style = f"height:{strength}px;border:none;color:#000;background-color:#000;"

    def _get_html(self, config: dict = None):
        return D.hr(style=self.style)


class SectionHeader:
    def __init__(self, name: str):
        self.divider = Divider()
        self.text = HTMLElement(D.h2(name))
        self._id = name.replace(" ", "_")
        self._name = name

    def _get_html(self, config: dict):
        return D.div([self.divider._get_html(config), self.text._get_html(config)], id=self._id)


def _resolve_element(el, tag):
    if isinstance(el, D.html_tag):
        return HTMLElement(el)

    elif isinstance(el, str):
        return TextElement(el)

    elif isinstance(el, plt.Figure):
        return MatplotlibElement(el, tag)

    elif isinstance(el, go.Figure):
        return PlotlyElement(el, tag)

    elif isinstance(el, BaseElement) and hasattr(el, "tag"):
        el.tag = tag
        return el

    else:
        return el


class BaseElement:
    ...


class TextElement(BaseElement):
    def __init__(self, el):
        self.content = el

    def _get_html(self, assets_path: Path):
        return D.p(
            self.content,
        )


class HTMLElement(BaseElement):
    def __init__(self, el):
        self.content = str(el)

    def _get_html(self, assets_path: Path):
        return raw(self.content)


class MarkdownElement(HTMLElement):
    def __init__(self, el):
        self.content = markdown(el)


class MatplotlibElement(BaseElement):
    def __init__(self, el: plt.Figure, tag: str = None, height=None, width="100%"):
        self.content = el
        self.tag = tag
        self.height = height
        self.width = width

    def _get_html(self, config: dict):
        tag = uuid4().hex + ".png"
        target_path = config["assets_path"].joinpath(tag)
        rel_path = Path(str(target_path).replace(str(target_path.parents[2]), "."))
        self.content.savefig(target_path)

        kwarg = {}
        if self.height is not None:
            kwarg["height"] = self.height

        img = D.a(
            D.img(src=rel_path, width=self.width, _class="text-center"),
            href=rel_path,
            target="_blank",
            **kwarg,
        )
        tag = D.p(
            [self.tag, D.a(D.i(_class="fa-solid fa-up-right-from-square text-center"), href=rel_path, target="_blank")],
            _class="text-center",
        )
        return D.div(
            [
                img,
                tag,
            ]
        )


class PlotlyElement(BaseElement):
    def __init__(self, el: go.Figure, tag: str = None, height=None, width="100%"):
        self.content = el
        self.tag = tag
        self.height = height
        self.width = width

    def _get_html(self, config: dict):
        tag = uuid4().hex + ".html"
        html_target_path = config["assets_path"].joinpath(tag)
        html_rel_path = Path("./" + str(html_target_path).replace(str(html_target_path.parents[2]), "."))
        self.content.write_html(html_target_path)

        if config["plotly_thumbnails"]:
            png_target_path = Path(str(html_target_path).replace(".html", ".png"))
            png_rel_path = Path("./" + str(png_target_path).replace(str(png_target_path.parents[2]), "."))
            self.content.write_image(png_target_path)

            kwarg = {}
            if self.height is not None:
                kwarg["height"] = self.height

            img = D.a(
                D.img(src=png_rel_path, width=self.width, _class="text-center", **kwarg),
                href=html_rel_path,
                target="_blank",
            )

        else:
            kwarg = {}
            if self.height is None:
                height = self.content.layout.height
                if height is not None:
                    kwarg["height"] = f"{height}px"
            else:
                kwarg["height"] = self.height
            img = D.iframe(src=html_rel_path, width=self.width, _class="text-center", **kwarg)

        tag = D.p(
            [self.tag, D.a(D.i(_class="fa-solid fa-up-right-from-square text-center"), href=html_rel_path, target="_blank")],
            _class="text-center",
        )

        return D.div([img, tag])


Text = TextElement
HTML = HTMLElement
Markdown = MarkdownElement
Plotly = PlotlyElement
Pyplot = MatplotlibElement
