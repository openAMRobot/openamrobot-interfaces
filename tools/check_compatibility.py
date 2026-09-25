"""Snapshot generated Jazzy type hashes and enforce reviewed version rules."""

import argparse
import json
from pathlib import Path
import re
import subprocess


def snapshot(source):
    from ament_index_python.packages import get_package_share_directory
    from catkin_pkg.package import parse_package
    from rosidl_adapter.parser import (
        parse_action_string, parse_message_string, parse_service_string,
    )

    packages = {}
    parsers = {"msg": parse_message_string, "srv": parse_service_string,
               "action": parse_action_string}
    for manifest in sorted(source.rglob("package.xml")):
        package = parse_package(str(manifest))
        installed = Path(get_package_share_directory(package.name))
        interfaces = {}
        for kind, parse in parsers.items():
            for path in sorted((manifest.parent / kind).glob(f"*.{kind}")):
                spec = parse(package.name, path.stem, path.read_text())
                parts = {"msg": (spec,)} if kind == "msg" else {}
                if kind == "srv":
                    parts = {"request": (spec.request,), "response": (spec.response,)}
                if kind == "action":
                    parts = {"goal": (spec.goal,), "result": (spec.result,),
                             "feedback": (spec.feedback,)}
                constants = {}
                for part, specs in parts.items():
                    for item in specs[0].constants:
                        constants[f"{part}/{item.name}"] = {
                            "type": str(item.type), "value": item.value,
                        }
                description = json.loads((installed / kind / f"{path.stem}.json").read_text())
                name = f"{package.name}/{kind}/{path.stem}"
                hashes = {entry["type_name"]: entry["hash_string"]
                          for entry in description["type_hashes"]}
                if name not in hashes or not re.fullmatch(r"RIHS01_[0-9a-f]{64}", hashes[name]):
                    raise ValueError(f"Missing valid generated type hash: {name}")
                interfaces[f"{kind}/{path.stem}"] = {
                    "type_hash": hashes[name], "constants": constants,
                }
        if not interfaces:
            raise ValueError(f"No interfaces found in {package.name}")
        packages[package.name] = {"package_version": package.version, "interfaces": interfaces}
    if not packages:
        raise ValueError("No interface packages found")
    return {"format_version": 1, "ros_distro": "jazzy", "packages": packages}


def package_version(value):
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError(f"Invalid package version: {value}")
    return tuple(map(int, value.split(".")))


def contract_version(package):
    constant = package["interfaces"]["msg/NavigationStatus"]["constants"]["msg/CONTRACT_VERSION"]
    value = constant["value"]
    if constant["type"] != "uint16" or type(value) is not int or not 1 <= value <= 65535:
        raise ValueError("CONTRACT_VERSION must be a positive uint16 constant")
    return value


def compare(before, after):
    errors, changes = [], []
    if before.get("format_version") != 1 or after.get("format_version") != 1:
        raise ValueError("Unsupported snapshot format")
    if before.get("ros_distro") != "jazzy" or after.get("ros_distro") != "jazzy":
        raise ValueError("Expected Jazzy snapshots")
    if not before["packages"] or not after["packages"]:
        raise ValueError("Empty package snapshot")
    candidate_nav = after["packages"].get("openamr_nav_msgs")
    if candidate_nav is not None:
        reasons = {}
        for name, constant in candidate_nav["interfaces"]["msg/NavigationStatus"]["constants"].items():
            # NavigationStatus's uint16 constants are reason codes, except its version.
            if constant["type"] != "uint16" or name == "msg/CONTRACT_VERSION":
                continue
            code = constant["value"]
            if code in reasons:
                errors.append(f"{name}: duplicate reason code {code} (also {reasons[code]})")
            else:
                reasons[code] = name
    for name, old in before["packages"].items():
        if name not in after["packages"]:
            errors.append(f"{name}: removing a package requires a migration policy")
            continue
        new = after["packages"][name]
        old_version = package_version(old["package_version"])
        new_version = package_version(new["package_version"])
        if new_version < old_version:
            errors.append(f"{name}: package version regressed")
        changed = set(old["interfaces"]) != set(new["interfaces"])
        for interface, previous in old["interfaces"].items():
            current = new["interfaces"].get(interface)
            if current is None:
                continue
            if previous["type_hash"] != current["type_hash"]:
                changed = True
                changes.append(f"{name}/{interface}: generated type hash changed")
            for constant, value in previous["constants"].items():
                if constant == "msg/CONTRACT_VERSION" and name == "openamr_nav_msgs":
                    continue
                if current["constants"].get(constant) != value:
                    changed = True
                    changes.append(f"{name}/{interface}: existing constant changed: {constant}")
                    if name == "openamr_nav_msgs" and interface == "msg/NavigationStatus" and (
                        value["type"] == "uint16" and (value["value"] >= 1000 or constant == "msg/NONE")
                    ):
                        errors.append(f"{constant}: reason codes are append-only")
            if name == "openamr_nav_msgs" and interface == "msg/NavigationStatus":
                reserved = {v["value"] for k, v in previous["constants"].items()
                            if v["type"] == "uint16" and (v["value"] >= 1000 or k == "msg/NONE")}
                for key, value in current["constants"].items():
                    if key not in previous["constants"] and value["type"] == "uint16" and value["value"] in reserved:
                        errors.append(f"{key}: reuses a reserved reason code")
        if name == "openamr_nav_msgs":
            old_contract, new_contract = contract_version(old), contract_version(new)
            if not isinstance(new_contract, int) or new_contract < old_contract:
                errors.append(f"{name}: CONTRACT_VERSION regressed or is invalid")
            if changed and new_contract <= old_contract:
                errors.append(f"{name}: interface change requires CONTRACT_VERSION increase")
        elif changed and new_version <= old_version:
            errors.append(f"{name}: interface change requires package version increase")
    for name in after["packages"].keys() - before["packages"].keys():
        changes.append(f"{name}: new package")
    return {"status": "FAIL" if errors else "PASS", "changes": changes, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--base-ref", default="HEAD^")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    current = snapshot(args.source)
    args.output.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
    if args.baseline is None:
        print(f"Snapshot written: {args.output}; no compatibility result claimed")
        return
    recorded = json.loads(args.baseline.read_text())
    if recorded != current:
        raise SystemExit("FAIL: checked-in snapshot differs from generated interfaces; regenerate it for review")
    root = args.source.resolve().parent
    # The clean HOME intentionally excludes checkout's global safe.directory.
    # Trust only the explicitly supplied repository, for these read-only calls.
    git = ["git", "-c", f"safe.directory={root}"]
    ref = subprocess.check_output(
        git + ["rev-parse", "--verify", f"{args.base_ref}^{{commit}}"], cwd=root, text=True
    ).strip()
    relative = args.baseline.resolve().relative_to(root).as_posix()
    exists = subprocess.run(git + ["cat-file", "-e", f"{ref}:{relative}"], cwd=root,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if exists.returncode:
        # Bootstrap is allowed only while introducing this gate, with no ROS changes.
        subprocess.run(git + ["diff", "--exit-code", ref, "--", "ros2"], cwd=root, check=True)
        previous = recorded
        print("Initial baseline: interface sources unchanged from comparison commit")
    else:
        previous = json.loads(subprocess.check_output(
            git + ["show", f"{ref}:{relative}"], cwd=root, text=True
        ))
    result = compare(previous, current)
    result["base_commit"] = ref
    if args.report:
        args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
