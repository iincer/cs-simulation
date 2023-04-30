from pacti.terms.polyhedra import *
from pacti.iocontract import Var

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
