import numpy as np
import plotly.express as px
from matplotlib import pyplot as plt

import rrg
import re


def _make_plt_hist():
    fig, ax1 = plt.subplots(figsize=(12, 10))
    data = np.random.normal(size=(15,))
    ax1.hist(data)
    return fig


def _make_plt_line():
    fig, ax1 = plt.subplots(figsize=(12, 10))
    data = np.random.normal(size=(15,))
    ax1.plot(data)
    return fig


def _make_plotly_scatter():
    data = np.random.normal(size=(2, 15))
    fig = px.scatter(x=data[0], y=data[1])
    return fig


def test_report():
    r = rrg.Report("./example_reports/a.html", title="Test report")
    r.add_elements(
        rrg.SectionHeader("Markdown"),
        rrg.Markdown(
            """
### Arbitrary markdown can be used 
- List 1 
    - Sublist a
- List 2 

```
obj->run();
```
        """.strip()
        ),
        #
        #
        rrg.SectionHeader("Mathjax"),
        r"""When \(a \ne 0\), there are two solutions to \(ax^2 + bx + c = 0\) and they are
  \[x = {-b \pm \sqrt{b^2-4ac} \over 2a}.\]""",
        #
        #
        rrg.SectionHeader("Plotly"),
        rrg.Cols(
            {
                "(a): plotly subfigure": _make_plotly_scatter(),
                #
                "textbox": rrg.Markdown(
                    """
- Markdown also works inline"""
                ),
            }
        ),
        #
        #
        rrg.SectionHeader("Matplotlib"),
        rrg.Cols([_make_plt_line(), _make_plt_hist(), "Plaintext elements are supported as bare strings"]),
    )
    r.write()


if __name__ == "__main__":
    test_report()
