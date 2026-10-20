#!/usr/bin/env python3
"""Send a per-status Telegram notification about a CI run.

All inputs come from environment variables only (never argv), so the
bot token and chat id never appear in process listings, shell tracing,
or logged command lines.

Exit codes:
  0 - message sent, or secrets missing (warning only, not a failure)
  1 - secrets present but sending failed (bad STATUS, HTTP error,
      ok=false, timeout) - the caller is expected to mark this step
      continue-on-error so it never affects the overall run status.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

STATUS_LABELS = {
    "success": "✅ Success",
    "tests-failed": "❌ Tests failed",
    "build-failed": "\U0001F6D1 Build failed before tests",
    "cancelled": "⚠️ Cancelled",
}

# Telegram legacy Markdown only treats these four characters as special.
_MD_SPECIAL = re.compile(r"([_*`\[])")

TIMEOUT_SECONDS = 10


def env(name, default=""):
    return os.environ.get(name, default)


def esc(value):
    return _MD_SPECIAL.sub(r"\\\1", value)


def build_message():
    status = env("STATUS")
    if status not in STATUS_LABELS:
        raise ValueError(f"unknown STATUS: {status!r}")

    lines = [
        f"*{STATUS_LABELS[status]}*",
        "",
        f"*Project:* {esc(env('PROJECT'))}",
        "*CI:* GitHub Actions",
        f"*Branch:* {esc(env('BRANCH'))}",
        f"*Commit:* {esc(env('COMMIT'))}",
        "",
    ]

    if status in ("success", "tests-failed"):
        if env("STATS_OK") == "true":
            lines.append("*Tests:*")
            lines.append(f"✅ Passed: `{esc(env('PASSED', '0'))}`")
            lines.append(f"❌ Failed: `{esc(env('FAILED', '0'))}`")
            lines.append(f"⏭ Skipped: `{esc(env('SKIPPED', '0'))}`")
        else:
            lines.append("Tests: stats unavailable (JUnit XML missing or invalid)")
    elif status == "build-failed":
        lines.append("Tests did not run (build/compile failed)")
    elif status == "cancelled":
        lines.append("Run was cancelled before completion")

    lines.append("")
    lines.append(f"Run: {esc(env('RUN_URL'))}")
    report_url = env("REPORT_URL")
    if report_url:
        lines.append(f"Report: {esc(report_url)}")

    return "\n".join(lines)


def send(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status_code = response.status
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"::error::Telegram API returned HTTP {exc.code}: {body}")
        return False
    except urllib.error.URLError as exc:
        print(f"::error::Telegram API request failed: {exc.reason}")
        return False
    except OSError as exc:
        print(f"::error::Telegram API request failed: {exc}")
        return False

    if status_code != 200:
        print(f"::error::Telegram API returned unexpected HTTP status {status_code}: {body}")
        return False

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print("::error::Telegram API returned a non-JSON response")
        return False

    if not data.get("ok"):
        print(f"::error::Telegram API reported ok=false: {data.get('description', 'no description')}")
        return False

    print("Telegram notification sent")
    return True


def main():
    try:
        text = build_message()
    except ValueError as exc:
        print(f"::error::{exc}")
        return 1

    token = env("TELEGRAM_BOT_TOKEN")
    chat_id = env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print(
            "::warning::TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set; "
            "skipping Telegram notification"
        )
        return 0

    return 0 if send(token, chat_id, text) else 1


if __name__ == "__main__":
    raise SystemExit(main())
