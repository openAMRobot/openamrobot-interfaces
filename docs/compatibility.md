# Interface compatibility and version gate

`bash tools/verify.sh` checks every installed interface's generated ROS Jazzy
RIHS01 type hash against `compatibility/jazzy.json`. Constants are recorded
separately because they are not part of the wire type hash. Nested type changes
affect generated hashes; navigation and UI message/action definitions are covered.

The generated snapshot must exactly match the checked-in snapshot. The checker
then compares it with the snapshot at `VERIFY_BASE_REF` (default `HEAD^`). CI
sets this to the PR target commit or the previous main-branch push commit and
fetches full history. Locally, for a multi-commit branch, run:

```bash
VERIFY_BASE_REF=$(git merge-base HEAD origin/main) bash tools/verify.sh
```

Use `upstream/main` instead if that is your authoritative main remote. Invalid
refs fail. When first introducing this gate, a missing baseline at the comparison
commit is accepted only if `git diff <base> -- ros2` is empty: bootstrap cannot
accompany interface changes. Empty or missing current snapshots do not pass.

## Rules

- Navigation type additions/removals/hash changes and changes to existing enum
  constants require an increase of `NavigationStatus.CONTRACT_VERSION`.
- New enum/reason constants alone do not require a bump, per CONTRACT.md.
- Existing navigation reason codes are append-only: removal, renumbering or
  reuse fails even with a contract bump.
- The complete candidate reason registry must have unique numeric values,
  including newly added reasons. Two new reasons sharing a code fail even when
  the contract version increases or the baseline is being introduced.
- Other packages require an increased `package.xml` version for type changes
  or changes to existing constants. This checks an increase, not a universal
  major/minor SemVer policy.
- Package and contract versions cannot regress. Package removal requires a
  separately reviewed migration policy and fails this gate.

These are structural checks, not proof of old/new runtime interoperability.
Changes in prose or the meaning of a value still require human review and the
documented version decision. No release readiness is implied.

## Updating a snapshot

After building and sourcing the candidate install, explicitly regenerate it:

```bash
python3 tools/check_compatibility.py --source ros2 --output compatibility/jazzy.json
```

Commit it alongside the reviewed interface/version change. Normal verification
never rewrites this file. Updating the snapshot does not bypass version checks:
they compare with the baseline from Git, not the modified working file. Review
the snapshot diff and any dependency-caused hash changes before accepting it.

Evidence: `interface-snapshot.json` records generated hashes/constants/versions,
`compatibility.json` records the comparison commit, changes and verdict, and
`compatibility.log` records checker and regression-test output. Early failures
appear in the log and overall `result.txt`; missing reports are not passes.
