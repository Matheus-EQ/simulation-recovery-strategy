import numpy as np


def perturb_point(point, variable_indices, factor=1.20):
    """Return a copy of point with selected variables multiplied by factor."""
    perturbed = np.array(point, dtype=float).copy()

    for idx in variable_indices:
        perturbed[idx] *= factor

    return perturbed


def evaluate_with_recovery(
    point,
    evaluate_fn,
    variable_indices,
    recovery_factor=1.20,
    max_attempts=2,
):
    """
    Try to evaluate an input point in an external simulator.

    If the simulator fails, run one auxiliary perturbed point to improve
    convergence, then retry the original point. The perturbed point is
    not stored as a valid evaluated sample.
    """
    point = np.array(point, dtype=float).copy()
    last_error = None

    for attempt in range(max_attempts):
        try:
            return evaluate_fn(point)

        except Exception as exc:
            last_error = exc

            if attempt < max_attempts - 1:
                recovery_point = perturb_point(
                    point,
                    variable_indices,
                    factor=recovery_factor,
                )

                try:
                    evaluate_fn(recovery_point)
                except Exception:
                    pass

    raise RuntimeError("Simulation failed after recovery attempts.") from last_error
