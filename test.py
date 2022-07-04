import numpy as np
import plotly.express as px
from matplotlib import pyplot as plt

import rrg.report as rrg


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
    r = rrg.Report("~/test_reports/a.html", title="Test report")
    r.add_elements(
        rrg.SectionHeader("Section 1"),
        #
        rrg.Cols3([_make_plt_hist(), "3 columns", _make_plotly_scatter()]),
        #
        rrg.SectionHeader("Section 2"),
        #
        rrg.Cols2([_make_plt_line(), "2 columns"]),
        #
        r"""When \(a \ne 0\), there are two solutions to \(ax^2 + bx + c = 0\) and they are
  \[x = {-b \pm \sqrt{b^2-4ac} \over 2a}.\]""",
    )
    r.write()


if __name__ == "__main__":
    test_report()
