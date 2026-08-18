# Aspen HYSYS Simulation Recovery Strategy

A small, generic Python implementation of a convergence-recovery pattern developed for an automated **Python-Aspen HYSYS** workflow.

The original application evaluated operating points generated with **Latin Hypercube Sampling (LHS)** to create data for surrogate modeling and support Bayesian optimization studies. Some points did not converge on the first attempt, especially after large changes between consecutive samples.

This repository isolates the recovery logic from the proprietary simulation model. It contains no plant data, Aspen HYSYS case, COM automation code, or project-specific variable names.

## Problem context

LHS is a space-filling sampling method, so consecutive samples are not necessarily close in the decision-variable space. In the original workflow, Python updated HYSYS feed-stream variables and requested a new steady-state solution for each sample.

During the sampled runs, the convergence failures were consistently associated with changes in two influential feed-stream inputs. A failed LHS point could often be recovered through the following sequence:

1. Attempt the exact LHS point.
2. If it does not converge, create an auxiliary recovery point by perturbing only the selected variables.
3. Evaluate the auxiliary point so that the simulator can reach a different solved state.
4. Restore the exact values of the original LHS point.
5. Retry the original point.
6. Store only the result of the original LHS point. The auxiliary point is never treated as a valid sample.

The recovery perturbation is configurable. A factor of `1.20` represents a temporary increase of 20% in each selected variable, while a generic factor can be supplied for other cases.

## Why this can help

AspenTech training material describes steady-state flowsheet calculations as sequential and highlights the importance of initial guesses for iterative elements such as tear streams and recycle convergence. In the observed workflow, the currently solved simulator state influenced whether the next sampled condition converged.

The auxiliary evaluation is therefore used as a **numerical continuation heuristic**: it changes the simulator state before the original target is attempted again. It does not modify the target sample or guarantee convergence.

This explanation is an engineering interpretation of the observed behavior, not a claim about every internal Aspen HYSYS solver mechanism. The underlying cause can depend on the flowsheet, solver mode, recycle structure, column specifications, thermodynamics, and automation sequence.

Official background:

- [AspenTech - Aspen HYSYS](https://www.aspentech.com/en/products/engineering/aspen-hysys)
- [AspenTech training - recycle convergence and the importance of initial guesses](https://esupport.aspentech.com/T_course?id=a3p4P000000Vin3QAC)

## Installation

```bash
python -m pip install -r requirements.txt
```

## Example

```python
from recovery_strategy import run_with_recovery

point = {
    "x1": 1.0,
    "x2": 2.0,
    "x3": 3.0,
    "x4": 4.0,
    "x5": 5.0,
    "x6": 6.0,
    "x7": 7.0,
    "x8": 8.0,
    "x9": 9.0,
}

result = run_with_recovery(
    point=point,
    run_simulation=simulate_hysys,
    variables_to_perturb=["x2", "x7"],
    perturbation=0.20,
)
```

Here, `perturbation=0.20` temporarily increases `x2` and `x7` by 20%. The auxiliary result is discarded. The function then restores and evaluates the exact original point again.
