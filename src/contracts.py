from pacti.terms.polyhedra import *
from pacti.iocontract import Var
from typing import Dict
import pacti.terms.polyhedra.plots as plh_plots
import matplotlib.pyplot as plt
from matplotlib.figure import Figure as MplFigure
from matplotlib.patches import Polygon as MplPatchPolygon
import numpy as np


def calculate_output_bounds_for_input_value(ptl: PolyhedralTermList, inputs: Dict[Var, float], output: Var) -> tuple[float,float]:
    return get_bounds(ptl.evaluate(inputs).simplify(), output.name)

# Add a callback function for the mouse click event
def on_hover(ptl: PolyhedralTermList, x_var: Var, y_var: Var, fig, ax, event):
    if event.inaxes == ax:
        x_coord, y_coord = event.xdata, event.ydata
        y_min, y_max = calculate_output_bounds_for_input_value(ptl, {x_var: x_coord}, y_var)
        ax.set_title(f"@ {x_var.name}={x_coord:.2f}\n{y_min:.2f} <= {y_var.name} <= {y_max:.2f}")
        fig.canvas.draw_idle()

def plot_input_output_polyhedral_term_list(ptl: PolyhedralTermList, x_var: Var, y_var: Var) -> MplFigure:
    x_lims=get_bounds(ptl, x_var.name)
    y_lims=get_bounds(ptl, y_var.name)
    res_tuple = PolyhedralTermList.termlist_to_polytope(ptl, PolyhedralTermList([]))
    variables = res_tuple[0]
    a_mat = res_tuple[1]
    b = res_tuple[2]

    x, y = plh_plots._get_bounding_vertices(a_mat, b)

    # generate figure
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, aspect="equal")
    ax.set_xlim(x_lims)
    ax.set_ylim(y_lims)
    ax.set_xlabel(x_var.name)
    ax.set_ylabel(y_var.name)
    ax.set_aspect((x_lims[1] - x_lims[0]) / (y_lims[1] - y_lims[0]))


    poly = MplPatchPolygon(
        np.column_stack([x, y]), animated=False, closed=True, facecolor="deepskyblue", edgecolor="deepskyblue"
    )
    ax.add_patch(poly)

    # Connect the event to the callback function
    fig.canvas.mpl_connect('button_press_event', lambda event: on_hover(ptl, x_var, y_var, fig, ax, event))
    
    return fig

def charging(s: int, generation: tuple[float, float]) -> PolyhedralContract:
    t_entry=f"t{s}_entry"
    t_var=f"t{s}_var"
    t_exit=f"t{s}_exit"

    soc_entry=f"soc{s}_entry"
    soc_var=f"soc{s}_var"
    soc_exit=f"soc{s}_exit"

    duration=f"duration{s}"
    return PolyhedralContract.from_string(
        input_vars=[
            t_entry,
            t_var,

            duration,

            soc_entry
        ],
        output_vars=[
            t_exit,
            soc_var,
            soc_exit,
        ],
        assumptions=[
            f"0 <= {duration}",
            f"0 <= {t_entry} <= {t_var}",
        ],
        guarantees=[
            f"0 <= {soc_entry} <= {soc_var} <= {soc_entry} + {generation[1]}*{duration} <= 100",
            f"{duration} = {t_exit} - {t_entry}",
            f"{generation[0]}*{duration} <= {soc_exit} - {soc_entry} <= {generation[1]}*{duration}",
            f"{generation[0]}*({t_var}-{t_entry}) <= {soc_var} - {soc_entry} <= {generation[1]}*({t_var}-{t_entry})",
            f"{t_entry} <= {t_var} <= {t_exit}",
            f"{soc_entry} <= {soc_var} <= {soc_exit}",
        ]
    )


def get_bounds(ptl: PolyhedralTermList, var: str) -> tuple[float, float]:
    min = ptl.optimize(objective={Var(var): 1}, maximize=False)
    max = ptl.optimize(objective={Var(var): 1}, maximize=True)
    return min, max
