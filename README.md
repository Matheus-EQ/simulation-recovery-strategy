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

## Usage

The HYSYS-specific automation should be wrapped by an `evaluate_fn`. That adapter is responsible for writing the decision variables, running the solver, checking convergence, reading the requested outputs, and raising `SimulationConvergenceError` when the model does not converge.

```python
from recovery_strategy import (
    SimulationConvergenceError,
    evaluate_with_recovery,
)


def evaluate_hysys(point):
    # 1. Write the decision variables through the HYSYS automation interface.
    # 2. Run/check the steady-state calculation.
    # 3. Raise SimulationConvergenceError if the case does not converge.
    # 4. Return only the outputs required by the data-generation workflow.
    raise NotImplementedError


result = evaluate_with_recovery(
    point=[1.0, 2.0, 3.0],
    evaluate_fn=evaluate_hysys,
    variable_indices=[0, 2],
    recovery_factor=1.20,
    max_attempts=2,
)
```

With `max_attempts=2`, the call sequence is:

```text
original point -> recovery point -> original point
```

If the first original attempt succeeds, no recovery point is evaluated.

## Run the tests

The tests use Python's standard-library test runner and a fake simulator, so Aspen HYSYS is not required.

```bash
python -m unittest discover -s tests -v
```

## Limitations

- This is a targeted recovery heuristic, not a universal convergence algorithm.
- The influential variables and perturbation factor must be justified for each flowsheet.
- Perturbations must remain inside physically meaningful and permitted operating bounds.
- Unexpected automation or programming errors are not treated as convergence failures.
- Production workflows should log every failed attempt and define a separate policy for unrecoverable samples.
- Aspen HYSYS is a commercial product of Aspen Technology, Inc. This repository is an independent example and is not affiliated with or endorsed by AspenTech.
