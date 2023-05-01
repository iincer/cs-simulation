from pacti.terms.polyhedra import *


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
            # The soc_var ranges from the entry value up to entry value plus the max generation rate times the duration.
            f"0 <= {soc_entry} <= {soc_var} <= {soc_entry} + {generation[1]}*{duration} <= 100",
            # The duration is equal to the time between entry/exit.
            f"{duration} = {t_exit} - {t_entry}",
            # The lower/upper difference between exit/entry soc is the min/max generation rate times the duration.
            f"{generation[0]}*{duration} <= {soc_exit} - {soc_entry} <= {generation[1]}*{duration}",
            # The difference between the current soc and the entry soc is bounded by the min/max generation rate
            # times the difference between the current time and the time at entry.
            f"{generation[0]}*({t_var}-{t_entry}) <= {soc_var} - {soc_entry} <= {generation[1]}*({t_var}-{t_entry})",
            # The current time has lower/upper bounds as the entry/exit times.
            f"{t_entry} <= {t_var} <= {t_exit}",
            # The current state of charge has lower/upper bounds as the entry/exit state of charge.
            f"{soc_entry} <= {soc_var} <= {soc_exit}",
        ]
    )



