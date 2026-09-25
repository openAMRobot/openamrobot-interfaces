import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from lint_schemas import DRAFT, load_data, validate_interfaces, validate_schemas


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "schemas/json").mkdir(parents=True)
        (self.root / "schemas/yaml").mkdir()
        self.write("schemas/validation.json", {"format_version": 1, "entries": [{
            "schema": "schemas/json/test.schema.json",
            "valid": ["schemas/yaml/valid.yaml"],
            "invalid": ["schemas/json/invalid.json"],
        }]})
        self.write("schemas/json/test.schema.json", {
            "$schema": DRAFT, "type": "object", "required": ["version"],
            "properties": {"version": {"type": "integer", "minimum": 1}},
            "additionalProperties": False,
        })
        (self.root / "schemas/yaml/valid.yaml").write_text("version: 1\n")
        self.write("schemas/json/invalid.json", {"version": 0})

    def write(self, relative, value):
        (self.root / relative).write_text(json.dumps(value))

    def test_valid_and_invalid_examples(self):
        self.assertEqual(validate_schemas(self.root)["status"], "PASS")

    def test_wrong_valid_example_fails(self):
        (self.root / "schemas/yaml/valid.yaml").write_text("version: nope\n")
        with self.assertRaises(Exception):
            validate_schemas(self.root)

    def test_invalid_example_must_be_rejected(self):
        self.write("schemas/json/invalid.json", {"version": 2})
        with self.assertRaises(ValueError):
            validate_schemas(self.root)

    def test_unregistered_file_fails(self):
        self.write("schemas/json/unregistered.json", {})
        with self.assertRaises(ValueError):
            validate_schemas(self.root)

    def test_malformed_invalid_example_is_not_success(self):
        (self.root / "schemas/json/invalid.json").write_text("{")
        with self.assertRaises(ValueError):
            validate_schemas(self.root)

    def test_duplicate_yaml_key_rejected(self):
        path = self.root / "schemas/yaml/valid.yaml"
        path.write_text("version: 1\nversion: 2\n")
        with self.assertRaises(ValueError):
            load_data(path)

    def test_external_reference_rejected(self):
        self.write("schemas/json/test.schema.json", {
            "$schema": DRAFT, "$ref": "https://example.invalid/schema.json",
        })
        with self.assertRaises(ValueError):
            validate_schemas(self.root)

    def test_malformed_schema_fails(self):
        self.write("schemas/json/test.schema.json", {"$schema": DRAFT, "type": 3})
        with self.assertRaises(Exception):
            validate_schemas(self.root)

    def test_empty_registry_does_not_hide_files(self):
        self.write("schemas/validation.json", {"format_version": 1, "entries": []})
        with self.assertRaises(ValueError):
            validate_schemas(self.root)

    def test_duplicate_json_key_rejected(self):
        path = self.root / "schemas/json/invalid.json"
        path.write_text('{"version": 0, "version": 1}')
        with self.assertRaises(ValueError):
            load_data(path)


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "ros2/sample_msgs"
        (self.package / "msg").mkdir(parents=True)
        (self.package / "package.xml").write_text('''<package format="3">
<name>sample_msgs</name><version>0.0.1</version><description>Test</description>
<maintainer email="test@example.com">Test</maintainer><license>MIT</license>
</package>''')
        (self.package / "msg/Sample.msg").write_text("string value\n")
        # Unit tests isolate source/metadata validation from the separately run CMake linter.
        mocked = patch("lint_schemas.subprocess.run")
        mocked.start()
        self.addCleanup(mocked.stop)

    def test_valid_source(self):
        self.assertEqual(validate_interfaces(self.root)["interfaces"], 1)

    def test_invalid_field_name(self):
        (self.package / "msg/Sample.msg").write_text("string InvalidField\n")
        with self.assertRaises(Exception):
            validate_interfaces(self.root)

    def test_bad_package_metadata(self):
        (self.package / "package.xml").write_text('<package format="3"><name>sample_msgs</name></package>')
        with self.assertRaises(Exception):
            validate_interfaces(self.root)

    def test_trailing_whitespace(self):
        (self.package / "msg/Sample.msg").write_text("string value \n")
        with self.assertRaises(ValueError):
            validate_interfaces(self.root)

    def test_empty_interfaces_rejected(self):
        (self.package / "msg/Sample.msg").unlink()
        with self.assertRaises(ValueError):
            validate_interfaces(self.root)


if __name__ == "__main__":
    unittest.main()
