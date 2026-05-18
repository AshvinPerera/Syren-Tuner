import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from syren_tuner import Parameter, ParameterError, ParameterSpace


class ParameterTests(unittest.TestCase):
    def test_linear_sampling_and_clamp(self):
        parameter = Parameter("rate", bounds=(0.0, 10.0), initial=5.0)
        self.assertEqual(parameter.sample(0.0), 0.0)
        self.assertEqual(parameter.sample(0.5), 5.0)
        self.assertEqual(parameter.normalize(12.0), 10.0)

    def test_log_sampling(self):
        parameter = Parameter("scale", bounds=(1.0, 100.0), initial=10.0, scale="log")
        self.assertAlmostEqual(parameter.sample(0.0), 1.0)
        self.assertAlmostEqual(parameter.sample(1.0), 100.0)
        self.assertAlmostEqual(parameter.sample(0.5), 10.0)

    def test_integer_domain_snaps_values(self):
        parameter = Parameter("count", bounds=(0.0, 10.0), initial=2.2, domain="integer")
        self.assertEqual(parameter.initial, 2.0)
        self.assertEqual(parameter.sample(0.26), 3.0)

    def test_integer_domain_rounds_half_away_from_zero_like_rust(self):
        positive = Parameter("pos", bounds=(0.0, 10.0), initial=2.5, domain="integer")
        negative = Parameter("neg", bounds=(-10.0, 0.0), initial=-2.5, domain="integer")
        self.assertEqual(positive.initial, 3.0)
        self.assertEqual(negative.initial, -3.0)

    def test_space_rejects_duplicate_ids(self):
        with self.assertRaises(ParameterError):
            ParameterSpace(
                [
                    Parameter("x", bounds=(0.0, 1.0)),
                    Parameter("x", bounds=(0.0, 1.0)),
                ]
            )

    def test_from_dicts_accepts_studio_domain_shape(self):
        space = ParameterSpace.from_dicts(
            [
                {
                    "id": "count",
                    "bounds": {"min": 0, "max": 4},
                    "initial": 1.7,
                    "domain": {"kind": "integer"},
                }
            ]
        )
        self.assertEqual(space.initial()["count"], 2.0)


if __name__ == "__main__":
    unittest.main()
