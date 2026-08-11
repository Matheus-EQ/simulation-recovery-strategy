# Simulation Recovery Strategy

A generic Python example of a recovery strategy for external simulations.

When an external simulator fails to converge for a given input point, this approach evaluates an auxiliary perturbed point before retrying the original point. The auxiliary point is not stored as a valid sample; it is only used to help the simulator reach a better internal state.

## Example

```python
from recovery_strategy import evaluate_with_recovery


result = evaluate_with_recovery(
    point=[1.0, 2.0, 3.0],
    evaluate_fn=my_simulator_function,
    variable_indices=[0, 2],
    recovery_factor=1.20,
    max_attempts=2,
)

## Notes

This pattern can be useful when evaluating random or sequentially generated points in external simulators that reuse previous internal states or initial guesses.
