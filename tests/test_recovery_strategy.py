import unittest

import numpy as np

from recovery_strategy import (
    SimulationConvergenceError,
    evaluate_with_recovery,
    perturb_point,
)


class PerturbPointTests(unittest.TestCase):
    def test_perturbs_only_selected_variables_without_changing_input(self):
        original = np.array([10.0, 20.0, 30.0])

        perturbed = perturb_point(original, [0, 2], factor=1.20)

        np.testing.assert_allclose(perturbed, [12.0, 20.0, 36.0])
        np.testing.assert_allclose(original, [10.0, 20.0, 30.0])

    def test_rejects_duplicate_indices(self):
        with self.assertRaises(ValueError):
            perturb_point([1.0, 2.0], [0, 0])


class EvaluateWithRecoveryTests(unittest.TestCase):
    def test_returns_immediately_when_target_converges(self):
        calls = []

        def fake_simulator(point):
            calls.append(point.copy())
            return 42.0

        result = evaluate_with_recovery(
            [1.0, 2.0],
            fake_simulator,
            variable_indices=[0],
        )

        self.assertEqual(result, 42.0)
        self.assertEqual(len(calls), 1)
        np.testing.assert_allclose(calls[0], [1.0, 2.0])

    def test_runs_auxiliary_point_then_retries_exact_target(self):
        target = np.array([10.0, 5.0, 20.0])
        calls = []
        target_attempts = 0

        def fake_simulator(point):
            nonlocal target_attempts
            calls.append(point.copy())

            if np.array_equal(point, target):
                target_attempts += 1
                if target_attempts == 1:
                    raise SimulationConvergenceError("first target attempt failed")
                return "target result"

            return "discarded recovery result"

        result = evaluate_with_recovery(
            target,
            fake_simulator,
            variable_indices=[0, 2],
            recovery_factor=1.20,
            max_attempts=2,
        )

        self.assertEqual(result, "target result")
        self.assertEqual(len(calls), 3)
        np.testing.assert_allclose(calls[0], target)
        np.testing.assert_allclose(calls[1], [12.0, 5.0, 24.0])
        np.testing.assert_allclose(calls[2], target)

    def test_unexpected_errors_are_not_hidden(self):
        def broken_adapter(_point):
            raise ValueError("adapter bug")

        with self.assertRaisesRegex(ValueError, "adapter bug"):
            evaluate_with_recovery(
                [1.0],
                broken_adapter,
                variable_indices=[0],
            )

    def test_raises_convergence_error_after_all_attempts(self):
        def never_converges(_point):
            raise SimulationConvergenceError("did not converge")

        with self.assertRaisesRegex(
            SimulationConvergenceError,
            "configured recovery attempts",
        ):
            evaluate_with_recovery(
                [1.0, 2.0],
                never_converges,
                variable_indices=[0],
                max_attempts=2,
            )


if __name__ == "__main__":
    unittest.main()
