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

            soc_entry,
            soc_var
        ],
        output_vars=[
            t_exit,
            soc_exit,
        ],
        assumptions=[
            f"0 <= {duration}",
            f"0 <= {t_entry} <= {t_var}",
            f"0 <= {soc_entry} <= {soc_var} <= {soc_entry} + {generation[1]}*{duration} <= 100",
        ],
        guarantees=[
            f"{duration} = {t_exit} - {t_entry}",
            f"{generation[0]}*{duration} <= {soc_exit} - {soc_entry} <= {generation[1]}*{duration}",
            f"{generation[0]}*({t_var}-{t_entry}) <= {soc_var} - {soc_entry} <= {generation[1]}*({t_var}-{t_entry})",
            f"{t_entry} <= {t_var} <= {t_exit}",
            f"{soc_entry} <= {soc_var} <= {soc_exit}",
        ]
    )

c1: PolyhedralContract = charging(s=1, generation=[0.5, 0.8])

print(f"c1:\n{c1}")

constraints: PolyhedralTermList = c1.a | c1.g

print(f"constraints:\n{constraints}")

ce: PolyhedralTermList = constraints.evaluate(
    {Var("duration1"): 10.0,
     Var("t1_entry"): 0,
     Var("soc1_entry"): 50.0}
)

print(f"ce:\n{ce}")

t_var_min = ce.optimize(objective={Var("t1_var"): 1,}, maximize=False)
t_var_max = ce.optimize(objective={Var("t1_var"): 1,}, maximize=True)
print(f"t1_var:[{t_var_min},{t_var_max}]")

soc1_var_min = ce.optimize(objective={Var("soc1_var"): 1,}, maximize=False)
soc1_var_max = ce.optimize(objective={Var("soc1_var"): 1,}, maximize=True)
print(f"soc1_var (ce) :[{soc1_var_min},{soc1_var_max}]")

ce1: PolyhedralTermList = ce.evaluate({Var("t1_var"): 2.0})
print(f"ce1:\n{ce1}")

soc1_var_min = ce1.optimize(objective={Var("soc1_var"): 1,}, maximize=False)
soc1_var_max = ce1.optimize(objective={Var("soc1_var"): 1,}, maximize=True)
print(f"soc1_var (ce1):[{soc1_var_min},{soc1_var_max}]")
