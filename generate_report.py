#!/usr/bin/env python3
"""Generates an HTML report from the latest Maestro run's commands JSON."""

import json
import os
import glob
import sys
from datetime import datetime


def get_label(cmd):
    if "launchAppCommand" in cmd:
        return "Launch app"
    if "waitForAnimationToEndCommand" in cmd:
        t = cmd["waitForAnimationToEndCommand"].get("timeout", "")
        return f"Wait for animation to end ({t} ms)"
    if "assertConditionCommand" in cmd:
        cond = cmd["assertConditionCommand"].get("condition", {})
        if "visible" in cond:
            text = cond["visible"].get("textRegex", cond["visible"].get("id", ""))
            return f'Assert visible: "{text[:70]}{"…" if len(text) > 70 else ""}"'
        if "notVisible" in cond:
            text = cond["notVisible"].get("textRegex", "")
            return f'Assert not visible: "{text[:70]}"'
        return "Assert condition"
    if "tapOnElement" in cmd:
        sel = cmd["tapOnElement"].get("selector", {})
        text = sel.get("textRegex") or sel.get("id") or str(sel.get("point", ""))
        return f'Tap on "{text[:70]}"'
    if "inputTextCommand" in cmd:
        text = cmd["inputTextCommand"].get("text", "")
        return f'Input text: "{text[:50]}"'
    if "pressKeyCommand" in cmd:
        return f'Press key: {cmd["pressKeyCommand"].get("code", "")}'
    if "scrollUntilVisibleCommand" in cmd:
        sel = cmd["scrollUntilVisibleCommand"].get("selector", {})
        text = sel.get("textRegex", "")
        return f'Scroll until visible: "{text[:60]}"'
    if "swipeCommand" in cmd:
        return f'Swipe {cmd["swipeCommand"].get("direction", "")}'
    if "takeScreenshotCommand" in cmd:
        return f'Take screenshot: {cmd["takeScreenshotCommand"].get("path", "")}'
    if "runFlowCommand" in cmd:
        cond = cmd["runFlowCommand"].get("condition", {})
        if "visible" in cond:
            text = cond["visible"].get("textRegex", "")
            return f'Run flow when visible: "{text[:60]}"'
        if "notVisible" in cond:
            text = cond["notVisible"].get("textRegex", "")
            return f'Run flow when not visible: "{text[:60]}"'
        return "Run sub-flow"
    if "hideKeyboardCommand" in cmd:
        return "Hide keyboard"
    if "extendedWaitUntilCommand" in cmd:
        cond = cmd["extendedWaitUntilCommand"].get("condition", {})
        if "visible" in cond:
            text = cond["visible"].get("textRegex", "")
            return f'Wait until visible: "{text[:60]}"'
        return "Extended wait"
    if "backPressCommand" in cmd:
        return "Press Back"
    return list(cmd.keys())[0] if cmd else "Unknown"


def main():
    reports_dir = "reports"
    dirs = sorted(
        glob.glob(os.path.join(reports_dir, "????-??-??_??????")), reverse=True
    )
    if not dirs:
        print("No report directories found.")
        sys.exit(1)

    latest_dir = dirs[0]
    json_files = glob.glob(os.path.join(latest_dir, "commands-*.json"))
    if not json_files:
        print(f"No JSON file in {latest_dir}")
        sys.exit(1)

    json_file = json_files[0]
    flow_name = (
        os.path.basename(json_file)
        .replace("commands-", "")
        .replace(".json", "")
        .strip("()")
    )

    with open(json_file) as f:
        commands = json.load(f)

    commands.sort(key=lambda x: x.get("metadata", {}).get("sequenceNumber", 0))

    total   = len(commands)
    passed  = sum(1 for c in commands if c.get("metadata", {}).get("status") == "COMPLETED")
    failed  = sum(1 for c in commands if c.get("metadata", {}).get("status") == "FAILED")
    skipped = sum(1 for c in commands if c.get("metadata", {}).get("status") == "SKIPPED")
    errors  = total - passed - failed - skipped
    pass_rate = round(passed / total * 100) if total > 0 else 0

    ts = os.path.basename(latest_dir)
    try:
        dt = datetime.strptime(ts, "%Y-%m-%d_%H%M%S")
        generated = dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        generated = ts

    rows = ""
    for c in commands:
        label    = get_label(c.get("command", {}))
        status   = c.get("metadata", {}).get("status", "UNKNOWN")
        duration = c.get("metadata", {}).get("duration", 0)
        error    = c.get("metadata", {}).get("error", "")

        if status == "COMPLETED":
            badge     = '<span class="badge pass">PASS</span>'
            row_class = ""
        elif status == "FAILED":
            badge     = '<span class="badge fail">FAIL</span>'
            row_class = 'class="fail-row"'
        elif status == "SKIPPED":
            badge     = '<span class="badge skip">SKIP</span>'
            row_class = ""
        else:
            badge     = f'<span class="badge">{status}</span>'
            row_class = ""

        err_html = f'<div class="err">{error}</div>' if error else ""
        rows += f"""
        <tr {row_class}>
          <td>{label}{err_html}</td>
          <td>{badge}</td>
          <td>{duration / 1000:.2f}s</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Maestro Test Report</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f5f7fa;color:#1e293b}}
  header{{background:#0f172a;color:#fff;padding:18px 36px;display:flex;justify-content:space-between;align-items:center}}
  header h1{{font-size:20px;letter-spacing:.3px}}
  header .gen{{font-size:12px;color:#94a3b8}}
  .summary{{display:flex;gap:14px;padding:22px 36px;flex-wrap:wrap}}
  .card{{background:#fff;border-radius:10px;padding:18px 24px;flex:1;min-width:100px;box-shadow:0 1px 3px rgba(0,0,0,.07)}}
  .num{{font-size:34px;font-weight:700;line-height:1}}
  .lbl{{font-size:12px;color:#94a3b8;margin-top:5px}}
  .green{{color:#22c55e}} .red{{color:#ef4444}} .orange{{color:#f97316}} .blue{{color:#3b82f6}} .gray{{color:#94a3b8}}
  .bar-wrap{{margin:0 36px 20px;background:#e2e8f0;border-radius:99px;height:7px;overflow:hidden}}
  .bar{{height:100%;background:#22c55e;border-radius:99px;width:{pass_rate}%}}
  .content{{padding:0 36px 40px}}
  .meta{{font-size:13px;color:#64748b;margin-bottom:12px}}
  .meta span{{font-weight:600;color:#1e293b}}
  table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.07)}}
  thead{{background:#f8fafc}}
  th{{padding:11px 14px;text-align:left;font-size:11px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid #e2e8f0}}
  td{{padding:10px 14px;font-size:13px;border-bottom:1px solid #f1f5f9;vertical-align:top}}
  tr:last-child td{{border-bottom:none}}
  tr.fail-row{{background:#fff5f5}}
  .badge{{display:inline-block;padding:2px 9px;border-radius:99px;font-size:10.5px;font-weight:700}}
  .pass{{background:#dcfce7;color:#15803d}}
  .fail{{background:#fee2e2;color:#b91c1c}}
  .skip{{background:#f1f5f9;color:#94a3b8}}
  .err{{font-size:11.5px;color:#dc2626;margin-top:3px}}
  td:nth-child(2){{width:80px;text-align:center}}
  td:nth-child(3){{width:80px;text-align:right;color:#94a3b8}}
</style>
</head>
<body>
<header>
  <h1>✏️ Maestro Test Report</h1>
  <span class="gen">Generated {generated}</span>
</header>
<div class="summary">
  <div class="card"><div class="num">{total}</div><div class="lbl">Total Steps</div></div>
  <div class="card"><div class="num green">{passed}</div><div class="lbl">Passed</div></div>
  <div class="card"><div class="num red">{failed}</div><div class="lbl">Failed</div></div>
  <div class="card"><div class="num orange">{errors}</div><div class="lbl">Errors</div></div>
  <div class="card"><div class="num gray">{skipped}</div><div class="lbl">Skipped</div></div>
  <div class="card"><div class="num blue">{pass_rate}%</div><div class="lbl">Pass Rate</div></div>
</div>
<div class="bar-wrap"><div class="bar"></div></div>
<div class="content">
  <div class="meta">Flow: <span>{flow_name}</span> &nbsp;|&nbsp; Run: <span>{generated}</span></div>
  <table>
    <thead><tr><th>Step</th><th>Status</th><th>Duration</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>
</body>
</html>"""

    out = os.path.join(reports_dir, "report.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"✅  Report → {out}")


if __name__ == "__main__":
    main()
