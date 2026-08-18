"""Generic recovery logic for stateful external process simulations."""

from collections.abc import Callable, Sequence
from typing import TypeVar

import numpy as np
from numpy.typing import NDArray


ResultT = TypeVar("ResultT")


class SimulationConvergenceError(RuntimeError):
    """Signal that an external simulator did not converge for an input point."""


def perturb_point(
    point: Sequence[float],
    variable_indices: Sequence[int],
    factor: float = 1.20,
) -> NDArray[np.float64]:
    """Return a copy with selected decision variables multiplied by ``factor``."""
    if not np.isfinite(factor) or factor <= 0:
        raise ValueError("factor must be a finite number greater than zero")

    perturbed = np.asarray(point, dtype=float).copy()
    if perturbed.ndim != 1:
        raise ValueError("point must be a one-dimensional sequence")

    indices = tuple(variable_indices)
    if len(set(indices)) != len(indices):
        raise ValueError("variable_indices must not contain duplicates")

    for index in indices:
        if not isinstance(index, (int, np.integer)):
            raise TypeError("variable_indices must contain integers")
        if index < 0 or index >= perturbed.size:
            raise IndexError(f"variable index out of range: {index}")
        perturbed[index] *= factor

    return perturbed


def evaluate_with_recovery(
    point: Sequence[float],
    evaluate_fn: Callable[[NDArray[np.float64]], ResultT],
    variable_indices: Sequence[int],
    recovery_factor: float = 1.20,
    max_attempts: int = 2,
) -> ResultT:
    """Evaluate a target point, using auxiliary perturbed runs after failures.

    Only :class:`SimulationConvergenceError` triggers the recovery sequence.
    The auxiliary recovery result is discarded; a successful return always belongs
    to the exact target point supplied by the caller.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    target_point = np.asarray(point, dtype=float).copy()
    recovery_point = perturb_point(
        target_point,
        variable_indices,
        factor=recovery_factor,
    )
    last_error: SimulationConvergenceError | None = None

    for attempt in range(max_attempts):
        try:
            return evaluate_fn(target_point.copy())
        except SimulationConvergenceError as exc:
            last_error = exc

        if attempt < max_attempts - 1:
            try:
                evaluate_fn(recovery_point.copy())
            except SimulationConvergenceError:
                # The target is still retried because the auxiliary evaluation may
                # have changed the external simulator's internal numerical state.
                continue

    raise SimulationConvergenceError(
        "Target point failed after the configured recovery attempts."
    ) from last_error
