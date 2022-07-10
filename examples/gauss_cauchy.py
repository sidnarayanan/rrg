import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import rrg


def shear(samples: np.ndarray) -> np.ndarray:
    scale = np.array(
        [
            [1, 0.1, 0.2],
            [0.1, 0.8, 0.5],
            [0.2, 0.5, 1.2],
        ]
    )
    return np.matmul(samples, scale)


def plotly_2d(g: np.ndarray, c: np.ndarray, x: int, y: int) -> go.Figure:
    fig = go.Figure()
    data = {"Gauss": g, "Cauchy": c}
    for k, arr in data.items():
        arr = arr.T
        trace = go.Scattergl(x=arr[x], y=arr[y], marker=dict(opacity=0.5), name=k, mode="markers")
        fig.add_trace(trace)

    fig.update_layout(height=400)
    return fig


def plotly_3d(g: np.ndarray, c: np.ndarray) -> go.Figure:
    fig = go.Figure()
    data = {
        "Gauss": g,
        "Cauchy": c,
    }
    for k, arr in data.items():
        arr = arr.T
        trace = go.Scatter3d(x=arr[0], y=arr[1], z=arr[2], marker=dict(opacity=0.5), name=k, mode="markers")
        fig.add_trace(trace)

    fig.update_layout(height=600)
    return fig


def plt_1d(g: np.ndarray, c: np.ndarray, dim: int) -> plt.Figure:
    fig = plt.figure(figsize=(12, 10))
    ax = plt.gca()
    data = {
        "Gauss": g,
        "Cauchy": c,
    }
    for k, arr in data.items():
        x = arr[:, dim]
        ax.hist(x, histtype="step", label=k, linewidth=4)

    ax.legend()
    return fig


def main():
    rng = np.random.default_rng()
    gauss = shear(rng.normal(size=(10, 3)))
    cauchy = shear(rng.standard_cauchy(size=(10, 3)))

    report = rrg.Report(path="./example_reports/gauss_vs_cauchy.html", title="Gauss vs. Cauchy", plotly_thumbnails=False)

    fig_3d = plotly_3d(gauss, cauchy)
    report.add_element(rrg.SectionHeader("Cauchy distributions have many outliers..."))
    report.add_element(
        rrg.Cols(
            {
                "(a)": fig_3d,
                "textbox": rrg.Text(
                    r"""Figure (a) shows the difference between 3D Gaussian and Cauchy distributions. 
Note that the Cauchy distribution is generated in its standard form, then rescaled 
by applying the Gaussian's covariance matrix.. 
\[\]
It is easy to show the Cauchy distribution does not have a well-defined variance (or indeed any moments):

\[\int_{-\infty}^\infty dx~x^2p(x) =\int_{-\infty}^\infty dx~\frac{x^2}{1+x^2} \]

Note the integrand tends to \(1\) as \(x\rightarrow \infty\), ensuring the integral diverges.
"""
                ),
            }
        )
    )

    figs_2d = {f"x={x}, y={y}": plotly_2d(gauss, cauchy, x, y) for (x, y) in [(0, 1), (1, 2), (0, 2)]}
    report.add_element(rrg.SectionHeader("...so sometimes 2D views are helpful..."))
    report.add_element(rrg.Cols(figs_2d))

    figs_1d = {}
    figs_1d["textbox"] = rrg.Markdown(
        """And for fun, let's:

- write a markdown caption here
- and insert it to the left"""
    )
    figs_1d.update({f"x={x}": plt_1d(gauss, cauchy, x) for x in range(3)})
    report.add_element(rrg.SectionHeader("...or 1D histograms..."))
    report.add_element(rrg.Cols(figs_1d))

    report.write()


if __name__ == "__main__":
    main()
