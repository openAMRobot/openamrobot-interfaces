import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_compatibility import compare


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.before = json.loads((ROOT / "compatibility/jazzy.json").read_text())
        self.after = copy.deepcopy(self.before)

    def nav(self):
        return self.after["packages"]["openamr_nav_msgs"]["interfaces"]

    def bump(self):
        self.nav()["msg/NavigationStatus"]["constants"]["msg/CONTRACT_VERSION"]["value"] += 1

    def errors(self):
        return compare(self.before, self.after)["errors"]

    def test_unchanged(self):
        self.assertEqual(self.errors(), [])

    def test_nested_type_change_requires_contract_bump(self):
        self.nav()["msg/SensorStatus"]["type_hash"] = "RIHS01_" + "f" * 64
        self.assertTrue(self.errors())
        self.bump()
        self.assertEqual(self.errors(), [])

    def test_removed_type_requires_contract_bump(self):
        del self.nav()["msg/ParkingStatus"]
        self.assertTrue(self.errors())

    def test_enum_addition_allowed_without_bump(self):
        self.nav()["msg/SensorStatus"]["constants"]["msg/KIND_TEST"] = {"type": "uint8", "value": 7}
        self.assertEqual(self.errors(), [])

    def test_changed_enum_requires_bump(self):
        self.nav()["msg/SensorStatus"]["constants"]["msg/KIND_LIDAR"]["value"] = 9
        self.assertTrue(self.errors())
        self.bump()
        self.assertEqual(self.errors(), [])

    def test_reason_renumber_rejected_even_with_bump(self):
        self.nav()["msg/NavigationStatus"]["constants"]["msg/BASE_LINK_LOST"]["value"] = 9999
        self.bump()
        self.assertTrue(self.errors())

    def test_reason_reuse_rejected(self):
        self.nav()["msg/NavigationStatus"]["constants"]["msg/OTHER_REASON"] = {"type": "uint16", "value": 9001}
        self.assertTrue(self.errors())

    def test_duplicate_new_reason_codes_rejected(self):
        constants = self.nav()["msg/NavigationStatus"]["constants"]
        constants["msg/NEW_REASON_A"] = {"type": "uint16", "value": 9005}
        constants["msg/NEW_REASON_B"] = {"type": "uint16", "value": 9005}
        for mode in ("unchanged_version", "bumped_version", "bootstrap"):
            with self.subTest(mode=mode):
                if mode == "bumped_version":
                    self.bump()
                before = self.after if mode == "bootstrap" else self.before
                result = compare(before, self.after)
                self.assertEqual(result["status"], "FAIL")
                self.assertTrue(any("duplicate reason code 9005" in e for e in result["errors"]))

    def test_distinct_new_reason_codes_allowed_without_bump(self):
        constants = self.nav()["msg/NavigationStatus"]["constants"]
        constants["msg/NEW_REASON_A"] = {"type": "uint16", "value": 9005}
        constants["msg/NEW_REASON_B"] = {"type": "uint16", "value": 9006}
        self.assertEqual(self.errors(), [])

    def test_contract_regression_rejected(self):
        self.nav()["msg/NavigationStatus"]["constants"]["msg/CONTRACT_VERSION"]["value"] = 0
        with self.assertRaises(ValueError):
            self.errors()

    def test_contract_counter_type_cannot_change(self):
        self.nav()["msg/NavigationStatus"]["constants"]["msg/CONTRACT_VERSION"] = {"type": "bool", "value": True}
        with self.assertRaises(ValueError):
            self.errors()

    def test_ui_change_requires_package_bump(self):
        ui = self.after["packages"]["openamr_ui_msgs"]
        ui["interfaces"]["action/MoveBase"]["type_hash"] = "RIHS01_" + "f" * 64
        self.assertTrue(self.errors())
        version = list(map(int, ui["package_version"].split(".")))
        version[2] += 1
        ui["package_version"] = ".".join(map(str, version))
        self.assertEqual(self.errors(), [])

    def test_missing_package_is_not_pass(self):
        del self.after["packages"]["openamr_nav_msgs"]
        self.assertTrue(self.errors())

    def test_empty_snapshot_is_not_pass(self):
        self.after["packages"] = {}
        with self.assertRaises(ValueError):
            self.errors()


if __name__ == "__main__":
    unittest.main()
