#!/usr/bin/env python3
"""Aggregate JUnit XML test statistics from one or more result files.

Direct invocation (for fixture-based testing):
    python3 junit_stats.py <results_dir>
Prints a JSON summary to stdout and exits non-zero on "no files" or
"invalid XML" so tests can assert on the failure.

CI invocation (used from the workflow):
    python3 junit_stats.py <results_dir> --github-output "$GITHUB_OUTPUT"
Always exits 0 so a stats-collection problem never fails the test job;
instead it writes ok=false to the GitHub Actions output.
"""
import glob
import json
import os
import sys
import xml.etree.ElementTree as ET


def collect_stats(results_dir):
    xml_files = sorted(glob.glob(os.path.join(results_dir, "*.xml")))
    if not xml_files:
        return {"ok": False, "error": "no_xml_files", "dir": results_dir}

    tests = failures = errors = skipped = 0
    for path in xml_files:
        try:
            tree = ET.parse(path)
        except ET.ParseError as exc:
            return {"ok": False, "error": "invalid_xml", "file": path, "detail": str(exc)}
        root = tree.getroot()
        # Recursive search over every <testcase>, regardless of nesting
        # depth, so nested <testsuite> wrappers are never double-counted.
        for testcase in root.iter("testcase"):
            tests += 1
            if testcase.find("failure") is not None:
                failures += 1
            elif testcase.find("error") is not None:
                errors += 1
            elif testcase.find("skipped") is not None:
                skipped += 1

    passed = tests - failures - errors - skipped
    return {
        "ok": True,
        "tests": tests,
        "passed": passed,
        "failed": failures + errors,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
    }


def write_github_output(stats, output_path):
    lines = [f"ok={'true' if stats.get('ok') else 'false'}"]
    if stats.get("ok"):
        lines.append(f"passed={stats['passed']}")
        lines.append(f"failed={stats['failed']}")
        lines.append(f"skipped={stats['skipped']}")
    else:
        lines.append(f"error={stats.get('error', 'unknown')}")
    with open(output_path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv):
    if len(argv) < 2:
        print(json.dumps({"ok": False, "error": "missing_dir_argument"}))
        return 2

    results_dir = argv[1]
    github_output_path = None
    if len(argv) >= 4 and argv[2] == "--github-output":
        github_output_path = argv[3]

    stats = collect_stats(results_dir)
    print(json.dumps(stats))

    if github_output_path:
        write_github_output(stats, github_output_path)
        return 0

    if not stats.get("ok"):
        return 3 if stats.get("error") == "invalid_xml" else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
