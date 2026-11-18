#!/usr/bin/env python3
"""Stage 4: Rendering, Quality Control & Final Video Export.

Runs pre-render QC, renders MP4 + thumbnail + contact sheet via Remotion,
runs post-render audio/duration QC, and writes a structured qc-report.json.

Usage:
    python scripts/export_video.py --slug compound-demo [--project .] [--browser /path/to/chrome] [--retries 1]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import wave

HERE = os.path.dirname(os.path.abspath(__file__))


def pascal_case(slug: str) -> str:
    return "".join(w.capitalize() for w in slug.replace("_", "-").split("-") if w)


def check_wav(path: str) -> tuple[bool, str]:
    if not os.path.isfile(path):
        return False, f"Missing audio file: {path}"
    if os.path.getsize(path) < 44:
        return False, f"Corrupted/empty audio file: {path}"
    try:
        with wave.open(path, "rb") as wf:
            if wf.getnframes() == 0:
                return False, f"Zero-frame WAV: {path}"
        return True, "OK"
    except Exception as e:
        return False, f"Invalid WAV {path}: {e}"


def pre_render_qc(proj: str, slug: str) -> dict:
    src_dir = os.path.join(proj, "src", slug)
    pub_dir = os.path.join(proj, "public", slug)
    errors = []
    warnings = []

    tl_path = os.path.join(src_dir, "timeline.json")
    sb_path = os.path.join(src_dir, "storyboard.json")
    srt_path = os.path.join(src_dir, "voiceover.srt")

    for p in (tl_path, sb_path, srt_path):
        if not os.path.isfile(p):
            errors.append(f"Missing required project file: {p}")

    if not errors:
        with open(tl_path, encoding="utf-8") as f:
            tl = json.load(f)
        with open(sb_path, encoding="utf-8") as f:
            sb = json.load(f)
        if tl.get("durationInFrames", 0) != sb.get("durationInFrames", 0):
            warnings.append("timeline.json durationInFrames differs from storyboard.json.")
        for c in tl.get("cues", []):
            if not c.get("text", "").strip():
                errors.append(f"Empty narration in cue {c.get('id', '?')}.")

    ok, msg = check_wav(os.path.join(pub_dir, "music.wav"))
    if not ok:
        errors.append(msg)

    sfx_dir = os.path.join(pub_dir, "sfx")
    if not os.path.isdir(sfx_dir) or not os.listdir(sfx_dir):
        errors.append(f"Missing SFX directory or files: {sfx_dir}")

    return {"passed": len(errors) == 0, "errors": errors, "warnings": warnings}


def run_with_retry(cmd: list[str], cwd: str, retries: int) -> tuple[bool, str]:
    last_err = ""
    for attempt in range(retries + 1):
        print(f"$ {' '.join(cmd)} (attempt {attempt + 1}/{retries + 1})", flush=True)
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if r.returncode == 0:
            return True, r.stdout
        last_err = (r.stderr or r.stdout)[-2000:]
        if "Could not download" in last_err or "ECONNRESET" in last_err:
            break  # Network/browser binary missing is not transient
    return False, last_err


def main():
    ap = argparse.ArgumentParser(description="Render, QC, and export final Stickman video.")
    ap.add_argument("--slug", required=True, help="Video slug (e.g. compound-demo)")
    ap.add_argument("--project", default=".", help="Remotion project directory")
    ap.add_argument("--browser", default=os.environ.get("REMOTION_BROWSER_EXECUTABLE", ""), help="Path to Chrome/Chromium executable")
    ap.add_argument("--retries", type=int, default=1, help="Retries for recoverable render failures")
    args = ap.parse_args()

    proj = os.path.abspath(args.project)
    comp = pascal_case(args.slug)
    out_dir = os.path.join(proj, "out", args.slug)
    os.makedirs(out_dir, exist_ok=True)

    qc = pre_render_qc(proj, args.slug)
    report = {
        "slug": args.slug,
        "composition": comp,
        "pre_render_qc": qc,
        "render": {"mp4": False, "thumbnail": False, "contact_sheet": False, "error": None},
        "post_render_qc": None,
    }

    if not qc["passed"]:
        report_path = os.path.join(out_dir, "qc-report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        for e in qc["errors"]:
            print(f"PRE-RENDER QC ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Copy SRT deliverable
    srt_src = os.path.join(proj, "src", args.slug, "voiceover.srt")
    shutil.copyfile(srt_src, os.path.join(out_dir, f"{args.slug}.srt"))

    npx = shutil.which("npx") or shutil.which("npx.cmd")
    node = shutil.which("node")
    browser_flags = ["--browser-executable", args.browser] if args.browser else []

    mp4_path = os.path.join(out_dir, f"{args.slug}.mp4")
    thumb_path = os.path.join(out_dir, "thumbnail.png")
    sheet_path = os.path.join(out_dir, "contact-sheet.png")

    ok_mp4, err_mp4 = run_with_retry(
        [npx, "remotion", "render", comp, mp4_path, "--codec", "h264", "--audio-codec", "aac", *browser_flags],
        cwd=proj,
        retries=args.retries,
    )
    report["render"]["mp4"] = ok_mp4
    if not ok_mp4:
        report["render"]["error"] = err_mp4
        report_path = os.path.join(out_dir, "qc-report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"RENDER FAILED:\n{err_mp4}", file=sys.stderr)
        sys.exit(2)

    ok_thumb, _ = run_with_retry(
        [npx, "remotion", "still", comp, thumb_path, "--frame=15", *browser_flags],
        cwd=proj,
        retries=args.retries,
    )
    report["render"]["thumbnail"] = ok_thumb

    ok_sheet, _ = run_with_retry(
        [node, "stickman-sheet.mjs", comp, sheet_path, "0-120:30"],
        cwd=proj,
        retries=0,
    )
    report["render"]["contact_sheet"] = ok_sheet

    # Post-render QC
    tl_path = os.path.join(proj, "src", args.slug, "timeline.json")
    r_qc = subprocess.run(
        [sys.executable, os.path.join(HERE, "check_render.py"), mp4_path, "--timeline", tl_path],
        capture_output=True,
        text=True,
    )
    report["post_render_qc"] = {"passed": r_qc.returncode == 0, "output": r_qc.stdout.strip()}

    report_path = os.path.join(out_dir, "qc-report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Export complete: {out_dir}")


if __name__ == "__main__":
    main()
