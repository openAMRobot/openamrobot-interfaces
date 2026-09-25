"""Validate interface sources, package metadata and declared JSON/YAML contracts."""

import argparse
import json
from pathlib import Path
import subprocess

from jsonschema import Draft202012Validator
import yaml

DRAFT = "https://json-schema.org/draft/2020-12/schema"
REGISTRY_SCHEMA = {
    "$schema": DRAFT, "type": "object", "additionalProperties": False,
    "required": ["format_version", "entries"],
    "properties": {
        "format_version": {"const": 1},
        "entries": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["schema", "valid", "invalid"],
            "properties": {
                "schema": {"type": "string"},
                "valid": {"type": "array", "minItems": 1, "uniqueItems": True,
                          "items": {"type": "string"}},
                "invalid": {"type": "array", "minItems": 1, "uniqueItems": True,
                            "items": {"type": "string"}},
            },
        }},
    },
}


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate mapping key: {key}")
        result[key] = value
    return result


class UniqueLoader(yaml.SafeLoader):
    pass


def yaml_mapping(loader, node):
    return unique_pairs(loader.construct_pairs(node))


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, yaml_mapping)


def load_data(path):
    def reject_constant(value):
        raise ValueError(f"Non-finite JSON number: {value}")

    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        value = json.loads(text, object_pairs_hook=unique_pairs,
                           parse_constant=reject_constant)
    elif path.suffix in (".yaml", ".yml"):
        value = yaml.load(text, Loader=UniqueLoader)
    else:
        raise ValueError(f"Unsupported schema/data extension: {path}")
    # YAML timestamps, non-string keys and non-finite numbers are not JSON data.
    def check(item):
        if isinstance(item, dict):
            if any(not isinstance(k, str) for k in item):
                raise ValueError("Schema data requires string keys")
            for child in item.values():
                check(child)
        elif isinstance(item, list):
            for child in item:
                check(child)
    check(value)
    json.dumps(value, allow_nan=False)
    return value


def local_refs(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ("$ref", "$dynamicRef") and not str(child).startswith("#"):
                raise ValueError("Only in-document schema references are supported; no network retrieval")
            local_refs(child)
    elif isinstance(value, list):
        for child in value:
            local_refs(child)


def validate_schemas(root):
    registry = load_data(root / "schemas/validation.json")
    Draft202012Validator(REGISTRY_SCHEMA).validate(registry)
    discovered = {p.resolve() for folder in ("json", "yaml")
                  for p in (root / "schemas" / folder).rglob("*")
                  if p.is_file() and p.name != ".gitkeep" and p.suffix != ".md"}
    covered = set()

    def asset(relative):
        path = (root / relative).resolve()
        path.relative_to((root / "schemas").resolve())
        if path not in discovered:
            raise ValueError(f"Missing or out-of-scope schema asset: {relative}")
        covered.add(path)
        return path

    registered = set()
    for entry in registry["entries"]:
        schema_path = asset(entry["schema"])
        if schema_path in registered:
            raise ValueError(f"Schema registered twice: {entry['schema']}")
        registered.add(schema_path)
        schema = load_data(schema_path)
        if not isinstance(schema, dict) or schema.get("$schema") != DRAFT:
            raise ValueError(f"Schema must declare Draft 2020-12: {schema_path}")
        local_refs(schema)
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        if set(entry["valid"]) & set(entry["invalid"]):
            raise ValueError("A fixture cannot be both valid and invalid")
        for relative in entry["valid"]:
            validator.validate(load_data(asset(relative)))
        for relative in entry["invalid"]:
            # Malformed JSON/YAML or unresolved references are not expected failures.
            if not list(validator.iter_errors(load_data(asset(relative)))):
                raise ValueError(f"Invalid fixture unexpectedly accepted: {relative}")
    if discovered != covered:
        raise ValueError(f"Unregistered JSON/YAML assets: {sorted(str(p) for p in discovered - covered)}")
    return {"status": "PASS" if registered else "NOT_APPLICABLE",
            "schemas": len(registered), "assets": len(covered),
            "reason": "Validated declared contracts" if registered else "No domain JSON/YAML contracts exist"}


def validate_interfaces(root):
    from catkin_pkg.package import parse_package
    from rosidl_adapter.parser import parse_action_string, parse_message_string, parse_service_string
    parsers = {"msg": parse_message_string, "srv": parse_service_string,
               "action": parse_action_string}
    count = 0
    packages = []
    for manifest in sorted((root / "ros2").rglob("package.xml")):
        warnings = []
        package = parse_package(str(manifest), warnings=warnings)
        if warnings:
            raise ValueError(f"{manifest}: {warnings}")
        if package.name in packages:
            raise ValueError(f"Duplicate package name: {package.name}")
        packages.append(package.name)
        subprocess.run(["ament_lint_cmake", str(manifest.parent / "CMakeLists.txt")], check=True)
        package_count = 0
        for kind, parse in parsers.items():
            for path in sorted((manifest.parent / kind).glob(f"*.{kind}")):
                text = path.read_text(encoding="utf-8")
                for number, line in enumerate(text.splitlines(), 1):
                    if "\t" in line or line.rstrip() != line:
                        raise ValueError(f"{path}:{number}: tabs or trailing whitespace")
                parse(package.name, path.stem, text)
                package_count += 1
        if package_count == 0:
            raise ValueError(f"No interfaces in {package.name}")
        count += package_count
    if count == 0:
        raise ValueError("No ROS interfaces found")
    return {"status": "PASS", "packages": packages, "interfaces": count}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = {}
    try:
        report["interfaces"] = validate_interfaces(args.root)
        report["schemas"] = validate_schemas(args.root)
        report["status"] = "PASS"
    except Exception as error:
        report.update(status="FAIL", error=str(error))
        raise
    finally:
        args.report.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
