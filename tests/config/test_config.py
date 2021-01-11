import unittest
from typing import Dict

from my_project_name.config import Config
from my_project_name.errors import ConfigError


class FakeConfigClass:
    def __init__(self, my_test_config_dict: Dict):
        self.config_dict = my_test_config_dict


class ConfigTestCase(unittest.TestCase):
    def test_get_cfg(self):
        """Test that Config._get_cfg works correctly"""

        # Here's our test dictionary. Pretend that this was parsed from a YAML config file.
        test_config_dict = {"a_key": 5, "some_key": {"some_other_key": "some_value"}}

        # We create a fake config class. This class is needed as _get_cfg pulls config options
        # from 'self.config_dict'. So, we make a class that has a self.config_dict, and fill it
        # with our test config options.
        fake_cfg = FakeConfigClass(my_test_config_dict=test_config_dict)

        # Now let's make some calls to Config._get_cfg. We provide 'fake_cfg' as the first argument
        # as a substitute for 'self'. _get_cfg will then be pulling values from fake_cfg.config_dict.

        # Test that we can get the value of a top-level key
        self.assertEqual(
            Config._get_cfg(fake_cfg, ["a_key"]),
            5,
        )

        # Test that we can get the value of a nested key
        self.assertEqual(
            Config._get_cfg(fake_cfg, ["some_key", "some_other_key"]),
            "some_value",
        )

        # Test that the value provided by the default option is used when a key does not exist
        self.assertEqual(
            Config._get_cfg(
                fake_cfg,
                ["a_made_up_key", "this_does_not_exist"],
                default="The default",
            ),
            "The default",
        )

        # Test that the value provided by the default option is *not* used when a key *does* exist
        self.assertEqual(
            Config._get_cfg(fake_cfg, ["a_key"], default="The default"),
            5,
        )

        # Test that keys that do not exist raise a ConfigError when the required argument is True
        with self.assertRaises(ConfigError):
            Config._get_cfg(
                fake_cfg, ["a_made_up_key", "this_does_not_exist"], required=True
            )

        # Test that a ConfigError is not returned when a non-existent key is provided and required is False
        self.assertIsNone(
            Config._get_cfg(
                fake_cfg, ["a_made_up_key", "this_does_not_exist"], required=False
            )
        )

        # Test that default is used for non-existent keys, even if required is True
        # (Typically one shouldn't use a default with required=True anyways...)
        self.assertEqual(
            Config._get_cfg(
                fake_cfg,
                ["a_made_up_key", "this_does_not_exist"],
                default="something",
                required=True,
            ),
            "something",
        )

    # TODO: Test creating a test yaml file, passing the path to Config and _parse_config_values is called correctly


if __name__ == "__main__":
    unittest.main()
