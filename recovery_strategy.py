"""Simple recovery strategy for external simulations."""


def run_with_recovery(
    point,
    run_simulation,
    variables_to_perturb,
    perturbation=0.20,
):
    """Retry a failed point after running a temporary perturbed point."""
    original_point = point.copy()

    try:
        result = run_simulation(original_point.copy())
    except Exception:
        result = None

    if result is not None:
        return result

    print("The original point did not converge. Applying the recovery strategy...")

    recovery_point = original_point.copy()
    for variable in variables_to_perturb:
        recovery_point[variable] *= 1 + perturbation

    # The auxiliary result is intentionally discarded.
    try:
        run_simulation(recovery_point)
    except Exception:
        print("The auxiliary point did not converge. Retrying the original point anyway...")

    print("Restoring and retrying the exact original point...")
    try:
        result = run_simulation(original_point.copy())
    except Exception:
        result = None

    if result is None:
        print("The original point did not converge after the recovery attempt.")

    return result
