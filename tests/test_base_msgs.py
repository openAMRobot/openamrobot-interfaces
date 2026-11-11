"""Static checks for ros2/openamr_base_msgs (no ROS needed).

These check the contract rules that CONTRACT.md states: version constants, the UNKNOWN=0
convention, fault-code uniqueness and group, and that CMakeLists lists every message.
They do not replace the colcon build in tools/verify.sh.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "ros2" / "openamr_base_msgs"
MSG = PKG / "msg"

PRIMITIVES = {
    "bool", "byte", "char", "float32", "float64", "int8", "uint8", "int16", "uint16",
    "int32", "uint32", "int64", "uint64", "string",
}
EXTERNAL = {"std_msgs/Header", "builtin_interfaces/Duration"}
CONST_RE = re.compile(r"^(\w+)\s+([A-Z][A-Z0-9_]*)\s*=\s*(-?\d+)$")
FIELD_RE = re.compile(r"^([\w/]+(?:\[(?:<=)?\d*\])?)\s+([a-z][a-z0-9_]*)$")


def parse(path):
    """Return (constants, fields) from a .msg file. Raises ValueError on a bad line."""
    constants, fields = [], []
    for number, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        match = CONST_RE.match(line)
        if match:
            constants.append((match.group(1), match.group(2), int(match.group(3))))
            continue
        match = FIELD_RE.match(line)
        if match:
            fields.append((match.group(1), match.group(2)))
            continue
        raise ValueError(f"{path.name}:{number}: cannot parse {raw!r}")
    return constants, fields


def messages():
    return {p.stem: p for p in sorted(MSG.glob("*.msg"))}


class BaseMsgsTests(unittest.TestCase):
    def test_messages_exist(self):
        self.assertGreaterEqual(len(messages()), 5)

    def test_cmake_lists_every_message(self):
        listed = set(re.findall(r'"msg/(\w+)\.msg"', (PKG / "CMakeLists.txt").read_text()))
        self.assertEqual(listed, set(messages()))

    def test_every_line_parses_and_types_are_known(self):
        names = set(messages())
        for name, path in messages().items():
            constants, fields = parse(path)
            for ctype, _, _ in constants:
                self.assertIn(ctype, PRIMITIVES, f"{name}: bad constant type {ctype}")
            for ftype, fname in fields:
                base = re.sub(r"\[.*\]$", "", ftype)
                self.assertTrue(
                    base in PRIMITIVES or base in EXTERNAL or base in names,
                    f"{name}.{fname}: unknown type {ftype}",
                )

    def test_contract_version_constant_and_field(self):
        for name in ("BaseStatus", "BaseAuxStatus"):
            constants, fields = parse(messages()[name])
            versions = [v for t, n, v in constants if (t, n) == ("uint16", "CONTRACT_VERSION")]
            self.assertEqual(len(versions), 1, name)
            self.assertEqual(versions[0], 1, name)   # frozen I8 contract version starts at 1
            self.assertIn(("uint16", "contract_version"), fields, name)

    def test_status_identity_and_timing_fields(self):
        _, fields = parse(messages()["BaseStatus"])
        for expected in (
            ("std_msgs/Header", "header"),
            ("uint32", "boot_id"),
            ("uint32", "sequence"),
            ("uint64", "monotonic_us"),
            ("uint8", "powered_debug"),
            ("uint8", "reset_cause"),
        ):
            self.assertIn(expected, fields)

    def test_unknown_is_zero_in_every_message(self):
        for name, path in messages().items():
            constants, _ = parse(path)
            # enum zeros: uint8 *_UNKNOWN, or NONE. A fault code that merely contains the
            # word UNKNOWN (for example SAFETY_INPUT_UNKNOWN=18010) is a uint16 code.
            unknown = [
                v for t, n, v in constants
                if (t == "uint8" and n.endswith("UNKNOWN")) or n == "NONE"
            ]
            self.assertTrue(unknown, f"{name}: no UNKNOWN or NONE constant")
            self.assertEqual(set(unknown), {0}, f"{name}: UNKNOWN/NONE must be 0")

    def test_powered_debug_unknown_is_not_disabled(self):
        constants, _ = parse(messages()["BaseStatus"])
        values = {n: v for _, n, v in constants}
        self.assertEqual(values["POWERED_DEBUG_UNKNOWN"], 0)
        self.assertNotEqual(values["POWERED_DEBUG_DISABLED"], 0)

    def test_fault_codes_unique_and_in_group_18001(self):
        constants, _ = parse(messages()["BaseFault"])
        codes = [(n, v) for t, n, v in constants if t == "uint16" and n != "NONE"]
        self.assertTrue(codes)
        values = [v for _, v in codes]
        self.assertEqual(len(values), len(set(values)), "duplicate fault code")
        self.assertEqual(len({n for n, _ in codes}), len(codes), "duplicate fault name")
        self.assertEqual(min(values), 18001)
        self.assertTrue(all(18001 <= v <= 18999 for v in values))

    def test_codes_are_not_in_other_groups(self):
        # groups 10001 to 17001 belong to other owners (interfaces #31, Q2)
        constants, _ = parse(messages()["BaseFault"])
        for t, n, v in constants:
            if t == "uint16" and n != "NONE":
                self.assertGreaterEqual(v, 18001, n)

    def test_operating_states_match_e01_rev4(self):
        constants, fields = parse(messages()["BaseStatus"])
        names = {n for _, n, _ in constants}
        for state in ("LOCKED", "RUN", "INHIBITED", "CHARGING", "CHARGER_FAULT"):
            self.assertIn(f"OPERATING_STATE_{state}", names)
        self.assertNotIn("OPERATING_STATE_BOOT", names)  # boot lands in LOCKED (T1)
        values = {n: v for _, n, v in constants}
        self.assertEqual(values["OPERATING_STATE_UNKNOWN"], 0)
        self.assertEqual(len({v for n, v in values.items() if n.startswith("OPERATING_STATE_")}), 6)
        self.assertIn(("uint8", "operating_state"), fields)

    def test_latches_are_separate_fields(self):
        _, fields = parse(messages()["BaseStatus"])
        for expected in (
            ("uint8", "readiness"),          # reset_seen
            ("uint8", "reset_pressed"),      # input level, a different thing
            ("uint8", "ui_stop_active"),
            ("uint8", "host_stop_active"),
            ("uint8", "host_link"),          # comms health, a different thing from host stop
            ("uint16", "first_reason"),
            ("uint32", "reason_mask"),
            ("uint32", "session_epoch_counter"),
        ):
            self.assertIn(expected, fields)

    def test_reason_bits_are_distinct_single_bits(self):
        constants, _ = parse(messages()["BaseStatus"])
        bits = [v for t, n, v in constants if n.startswith("REASON_")]
        self.assertTrue(bits)
        self.assertEqual(len(bits), len(set(bits)))
        for v in bits:
            self.assertTrue(v > 0 and v & (v - 1) == 0, f"not a single bit: {v}")
        self.assertLessEqual(max(bits), 2 ** 31)

    def test_unfrozen_base_stopped_topic_is_not_in_candidate(self):
        self.assertNotIn("BaseStopped", messages())
        contract = (PKG / "CONTRACT.md").read_text()
        self.assertNotIn("| /base/stopped |", contract)
        self.assertIn("No separate /base/stopped topic", contract)

    def test_lift_measured_and_declared_positions_are_separate(self):
        _, fields = parse(messages()["BaseAuxStatus"])
        for expected in (
            ("float32", "lift_measured_position_m"),
            ("uint8", "lift_measured_position_valid"),
            ("float32", "lift_declared_position_m"),
            ("uint8", "lift_declared_position_valid"),
            ("uint8", "lift_homing_state"),
            ("uint32", "lift_raw_device_fault_code"),
            ("uint16", "lift_fault_code"),
        ):
            self.assertIn(expected, fields)
        self.assertNotIn(("float32", "lift_position_m"), fields)

    def test_fault_lifecycle_separates_condition_ack_and_recovery(self):
        constants, fields = parse(messages()["BaseFault"])
        names = {n for _, n, _ in constants}
        self.assertIn("LIFECYCLE_ACKNOWLEDGED", names)
        for expected in (("uint8", "condition_active"), ("uint8", "recovery_required")):
            self.assertIn(expected, fields)
        source = messages()["BaseFault"].read_text()
        self.assertIn("ACKNOWLEDGED may coexist with OBS_YES", source)
        contract = (PKG / "CONTRACT.md").read_text()
        self.assertIn("ACKNOWLEDGED + OBS_YES", contract)
        self.assertIn("does not prove KCHG", contract)
        self.assertIn("Package merge alone does not approve them", messages()["BaseFault"].read_text())

    def test_e01_reason_codes_exist(self):
        constants, _ = parse(messages()["BaseFault"])
        names = {n for _, n, _ in constants}
        for name in (
            "ESTOP_DIAGNOSTIC_ACTIVE", "ESTOP_DIAGNOSTIC_UNKNOWN", "RESET_INPUT_HIGH",
            "CHARGER_FAULT", "CHARGE_INTERLOCK_FAULT", "DRIVE_CONFIG_MISMATCH",
        ):
            self.assertIn(name, names)

    def test_non_fault_events_and_reset_causes_are_not_fault_codes(self):
        constants, _ = parse(messages()["BaseFault"])
        names = {n for _, n, _ in constants}
        for forbidden in ("UI_STOP_ACTIVE", "CHARGE_ENDED", "REBOOT_REQUESTED", "BOOT_POWER_ON", "BOOT_SOFTWARE", "WATCHDOG_RESET", "BROWNOUT_RESET"):
            self.assertNotIn(forbidden, names)
        status_constants, status_fields = parse(messages()["BaseStatus"])
        self.assertIn(("bool", "reboot_request_pending"), status_fields)
        self.assertIn(("uint8", "reset_cause"), status_fields)

    def test_wcm_fault_does_not_blanket_lock_run(self):
        contract = (PKG / "CONTRACT.md").read_text()
        self.assertIn("It does not by itself force `RUN` to `LOCKED`", contract)
        self.assertIn("while `CHARGING`", contract)

    def test_fault_reason_mask_excludes_events(self):
        constants, _ = parse(messages()["BaseStatus"])
        names = {n for _, n, _ in constants}
        for forbidden in ("REASON_UI_STOP", "REASON_CHARGE_ENDED", "REASON_BOOT_POWER_ON", "REASON_REBOOT_REQUESTED"):
            self.assertNotIn(forbidden, names)
        bits = [v for t, n, v in constants if n.startswith("REASON_")]
        self.assertTrue(all(v > 0 and v & (v - 1) == 0 for v in bits))

    def test_safety_ok_is_not_used_to_derive_safety_stopped(self):
        # SAFETY_OK is diagnostic feedback; it is not proof of contactor state (E-01 R6).
        for path in (MSG / "BaseStatus.msg", PKG / "CONTRACT.md"):
            text = path.read_text()
            self.assertNotIn("SAFETY_STOPPED is derived", text, path.name)
            self.assertNotIn("means the chain is OPEN", text, path.name)

    def test_no_command_or_session_messages(self):
        # #30 reports status. Commands and sessions belong to the I8 firmware/host contract.
        for name in messages():
            self.assertFalse(
                name.endswith(("Command", "Challenge", "Hello", "Result")), name
            )


if __name__ == "__main__":
    unittest.main()
