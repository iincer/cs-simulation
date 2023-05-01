from pacti.terms.polyhedra import *
from pacti.iocontract import Var
from typing import Dict, Optional
import pacti.terms.polyhedra.plots as plh_plots
import matplotlib.pyplot as plt
from matplotlib.figure import Figure as MplFigure
from matplotlib.patches import Polygon as MplPatchPolygon
import numpy as np

def get_bounds(ptl: PolyhedralTermList, var: str) -> tuple[float, float]:
    min = ptl.optimize(objective={Var(var): 1}, maximize=False)
    max = ptl.optimize(objective={Var(var): 1}, maximize=True)
    return min, max

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

def scenario_sequence(
    c1: PolyhedralContract,
    c2: PolyhedralContract,
    variables: list[str],
    c1index: int,
    c2index: Optional[int] = None,
    file_name: Optional[str] = None,
) -> PolyhedralContract:
    """
    Composes c1 with a c2 modified to rename its entry variables according to c1's exit variables

    Args:
        c1: preceding step in the scenario sequence
        c2: next step in the scenario sequence
        variables: list of entry/exit variable names for renaming
        c1index: the step number for c1's variable names
        c2index: the step number for c2's variable names; defaults ti c1index+1 if unspecified

    Returns:
        c1 composed with a c2 modified to rename its c2index-entry variables
        to c1index-exit variables according to the variable name correspondences
        with a post-composition renaming of c1's exit variables to fresh outputs
        according to the variable names.
    """
    if not c2index:
        c2index = c1index + 1
    c2_inputs_to_c1_outputs = [(f"{v}{c2index}_entry", f"{v}{c1index}_exit") for v in variables]
    keep_c1_outputs = [f"{v}{c1index}_exit" for v in variables]
    renamed_c1_outputs = [(f"{v}{c1index}_exit", f"output_{v}{c1index}") for v in variables]

    c2_with_inputs_renamed = c2.rename_variables(c2_inputs_to_c1_outputs)
    c12_with_outputs_kept = c1.compose(c2_with_inputs_renamed, vars_to_keep=keep_c1_outputs)
    c12 = c12_with_outputs_kept.rename_variables(renamed_c1_outputs)

    if file_name:
        write_contracts_to_file(
            contracts=[c1, c2_with_inputs_renamed, c12_with_outputs_kept],
            names=["c1", "c2_with_inputs_renamed", "c12_with_outputs_kept"],
            file_name=file_name,
        )

    return c12