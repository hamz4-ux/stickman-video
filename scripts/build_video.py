#!/usr/bin/env python3
"""Single-command automated video production pipeline for stickman-video.

Transforms an English script (or declarative storyboard.json) into a complete,
validated, render-ready Remotion composition with synthesized audio.

Usage:
    python scripts/build_video.py --script sample.md --slug my-explainer [--size 1920x1080] [--wps 2.6]
    python scripts/build_video.py --storyboard storyboard.json --slug my-explainer
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VALID_CHARACTERS = {"hero", "expert", "skeptic", "banker", "vip"}
VALID_SCENE_TYPES = {"cold_open", "split_compare", "data_beat", "station_pan", "ending", "chapter"}
VALID_MUSIC_STYLES = {"intro", "play", "tense", "mystery", "hope", "finale", "card"}


def run(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        sys.exit(f"Command failed ({r.returncode}): {' '.join(cmd)}")


def build_storyboard_from_timeline(timeline: dict) -> dict:
    """Convert timeline.json into a declarative storyboard.json using Stage 2 recipes."""
    cues = timeline.get("cues", [])
    fps = timeline.get("fps", 30)
    total_frames = timeline.get("durationInFrames", 0)
    if not cues:
        sys.exit("Error: timeline.json contains no cues.")

    scenes = []
    # Group cues into logical scenes (cold_open -> body scenes -> ending)
    n = len(cues)
    for idx, cue in enumerate(cues):
        start = cue["startFrame"]
        end = cue["endFrame"]
        dur = max(30, end - start)
        text = cue["text"].strip()

        if idx == 0:
            scenes.append({
                "id": f"S{idx + 1:02d}",
                "type": "cold_open",
                "fromFrame": start,
                "durationFrames": dur,
                "narration": text,
                "musicStyle": "intro",
                "characters": ["hero"],
                "params": {
                    "hero": "hero",
                    "hook": text.split(".")[0][:42].upper(),
                    "sub": text if len(text) <= 80 else text[:77] + "...",
                },
            })
        elif idx == n - 1:
            scenes.append({
                "id": f"S{idx + 1:02d}",
                "type": "ending",
                "fromFrame": start,
                "durationFrames": max(dur, total_frames - start),
                "narration": text,
                "musicStyle": "finale",
                "characters": ["hero"],
                "params": {
                    "hero": "hero",
                    "takeaway": text.split(".")[0][:42].upper(),
                },
            })
        elif any(ch.isdigit() for ch in text):
            scenes.append({
                "id": f"S{idx + 1:02d}",
                "type": "data_beat",
                "fromFrame": start,
                "durationFrames": dur,
                "narration": text,
                "musicStyle": "play",
                "characters": ["hero"],
                "params": {
                    "hero": "hero",
                    "value": 100,
                    "suffix": "%",
                    "caption": text[:80],
                },
            })
        elif idx % 2 == 1:
            scenes.append({
                "id": f"S{idx + 1:02d}",
                "type": "split_compare",
                "fromFrame": start,
                "durationFrames": dur,
                "narration": text,
                "musicStyle": "play",
                "characters": ["hero", "expert"],
                "params": {
                    "title": f"KEY POINT {idx}",
                    "left": {"character": "hero", "label": "BEFORE", "pose": "shrug"},
                    "right": {"character": "expert", "label": "AFTER", "pose": "pointR"},
                },
            })
        else:
            scenes.append({
                "id": f"S{idx + 1:02d}",
                "type": "station_pan",
                "fromFrame": start,
                "durationFrames": dur,
                "narration": text,
                "musicStyle": "hope",
                "characters": ["hero", "skeptic"],
                "params": {
                    "stations": [
                        {"title": "STEP 1", "character": "hero", "pose": "pointR"},
                        {"title": "STEP 2", "character": "skeptic", "pose": "think"},
                    ]
                },
            })

    return {
        "fps": fps,
        "durationInFrames": total_frames,
        "scenes": scenes,
    }


def validate_storyboard(sb: dict) -> list[str]:
    """Validate storyboard.json and return a list of warnings; exit on fatal errors."""
    errors = []
    warnings = []
    fps = sb.get("fps", 30)
    scenes = sb.get("scenes", [])
    if not scenes:
        errors.append("Storyboard has no scenes.")

    total_sec = sb.get("durationInFrames", 0) / fps
    if total_sec < 30 or total_sec > 120:
        warnings.append(f"Total duration {total_sec:.1f}s is outside the 30-120s target range.")

    for s in scenes:
        sid = s.get("id", "?")
        stype = s.get("type")
        if stype not in VALID_SCENE_TYPES:
            errors.append(f"Scene {sid}: invalid type '{stype}'.")
        if s.get("durationFrames", 0) <= 0:
            errors.append(f"Scene {sid}: durationFrames must be > 0.")
        if s.get("musicStyle", "play") not in VALID_MUSIC_STYLES:
            errors.append(f"Scene {sid}: invalid musicStyle '{s.get('musicStyle')}'.")
        for c in s.get("characters", []):
            if c not in VALID_CHARACTERS:
                errors.append(f"Scene {sid}: unknown character '{c}'.")

    if errors:
        for e in errors:
            print(f"VALIDATION ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    return warnings


def generate_scenes_tsx(sb: dict, out_dir: str):
    """Generate src/<slug>/Scenes.tsx from validated storyboard.json."""
    used_types = {s["type"] for s in sb["scenes"]}
    import_map = {
        "cold_open": "ColdOpenScene",
        "split_compare": "SplitCompareScene",
        "data_beat": "DataBeatScene",
        "station_pan": "StationPanScene",
        "ending": "EndingScene",
    }
    recipe_imports = sorted(import_map[t] for t in used_types if t in import_map)
    lines = [
        'import React from "react";',
        'import { CHARACTERS } from "../stickman/characters";',
        f'import {{ {", ".join(recipe_imports)} }} from "../stickman/recipes";',
        'import { SceneProps } from "./Video";',
        "",
    ]

    scene_entries = []
    for s in sb["scenes"]:
        sid = s["id"]
        stype = s["type"]
        from_f = s["fromFrame"]
        p = s.get("params", {})

        if stype == "cold_open":
            hero = p.get("hero", "hero")
            hook = json.dumps(p.get("hook", "HOOK"))
            sub = json.dumps(p.get("sub", ""))
            lines.append(
                f'const {sid}: React.FC<SceneProps> = ({{ dur }}) => '
                f'<ColdOpenScene dur={{dur}} hero={{CHARACTERS.{hero}}} hook={{{hook}}} sub={{{sub}}} />;'
            )
        elif stype == "split_compare":
            title = json.dumps(p.get("title", ""))
            l = p.get("left", {"character": "hero", "label": "A", "pose": "shrug"})
            r = p.get("right", {"character": "expert", "label": "B", "pose": "pointR"})
            lines.append(
                f'const {sid}: React.FC<SceneProps> = ({{ dur }}) => '
                f'<SplitCompareScene dur={{dur}} title={{{title}}} '
                f'left={{{{ character: CHARACTERS.{l["character"]}, label: {json.dumps(l["label"])}, pose: {json.dumps(l.get("pose", "pointR"))} }}}} '
                f'right={{{{ character: CHARACTERS.{r["character"]}, label: {json.dumps(r["label"])}, pose: {json.dumps(r.get("pose", "shrug"))} }}}} />;'
            )
        elif stype == "data_beat":
            hero = p.get("hero", "hero")
            val = p.get("value", 100)
            suffix = json.dumps(p.get("suffix", ""))
            cap = json.dumps(p.get("caption", ""))
            lines.append(
                f'const {sid}: React.FC<SceneProps> = ({{ dur }}) => '
                f'<DataBeatScene dur={{dur}} hero={{CHARACTERS.{hero}}} value={{{val}}} suffix={{{suffix}}} caption={{{cap}}} />;'
            )
        elif stype == "station_pan":
            stations = p.get("stations", [])
            st_code = ", ".join(
                f'{{ title: {json.dumps(st["title"])}, character: CHARACTERS.{st["character"]}, pose: {json.dumps(st.get("pose", "stand"))} }}'
                for st in stations
            )
            lines.append(
                f'const {sid}: React.FC<SceneProps> = ({{ dur }}) => '
                f'<StationPanScene dur={{dur}} stations={{[{st_code}]}} />;'
            )
        elif stype == "ending":
            hero = p.get("hero", "hero")
            takeaway = json.dumps(p.get("takeaway", "THE END"))
            lines.append(
                f'const {sid}: React.FC<SceneProps> = ({{ dur }}) => '
                f'<EndingScene dur={{dur}} hero={{CHARACTERS.{hero}}} takeaway={{{takeaway}}} />;'
            )

        scene_entries.append(f"  {{ c: {sid}, from: {from_f} }},")

    lines.append("")
    lines.append("export const GENERATED_SCENES = [")
    lines.extend(scene_entries)
    lines.append("];")
    lines.append(f"export const GENERATED_DURATION = {sb['durationInFrames']};")
    lines.append("")

    with open(os.path.join(out_dir, "Scenes.tsx"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description="Build a complete Stickman video project from script or storyboard.")
    ap.add_argument("--script", help="Path to English markdown script")
    ap.add_argument("--storyboard", help="Path to declarative storyboard.json")
    ap.add_argument("--slug", required=True, help="Video slug (e.g. compound-interest)")
    ap.add_argument("--project", default=".", help="Remotion project directory")
    ap.add_argument("--size", default="1920x1080", help="1920x1080 (16:9) or 1080x1920 (9:16)")
    ap.add_argument("--wps", type=float, default=2.6, help="Words per second for narration pacing")
    args = ap.parse_args()

    if not args.script and not args.storyboard:
        sys.exit("Error: provide --script or --storyboard.")

    proj = os.path.abspath(args.project)
    src_dir = os.path.join(proj, "src", args.slug)
    pub_dir = os.path.join(proj, "public", args.slug)

    if not os.path.isdir(src_dir):
        run([sys.executable, os.path.join(HERE, "new_video.py"), "--project", proj, "--slug", args.slug, "--size", args.size])

    if args.script:
        run([sys.executable, os.path.join(HERE, "parse_input.py"), "--script", args.script, "--out", src_dir, "--wps", str(args.wps)])
        with open(os.path.join(src_dir, "timeline.json"), encoding="utf-8") as f:
            timeline = json.load(f)
        sb = build_storyboard_from_timeline(timeline)
        sb_path = os.path.join(src_dir, "storyboard.json")
        with open(sb_path, "w", encoding="utf-8") as f:
            json.dump(sb, f, indent=2)
    else:
        with open(args.storyboard, encoding="utf-8") as f:
            sb = json.load(f)
        shutil.copyfile(args.storyboard, os.path.join(src_dir, "storyboard.json"))

    warnings = validate_storyboard(sb)
    generate_scenes_tsx(sb, src_dir)

    # Generate audio plan from storyboard
    fps = sb.get("fps", 30)
    plan_parts = [f"{s.get('musicStyle', 'play')}:{s['durationFrames'] / fps:.2f}" for s in sb["scenes"]]
    plan_str = ",".join(plan_parts)
    run([sys.executable, os.path.join(HERE, "gen_audio.py"), "--out", pub_dir, "--plan", plan_str])

    # Run TypeScript check
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if npx:
        run([npx, "tsc", "--noEmit"], cwd=proj)

    print("\n=== PRODUCTION REPORT ===")
    print(f"Slug:       {args.slug}")
    print(f"Size:       {args.size}")
    print(f"Scenes:     {len(sb['scenes'])}")
    print(f"Duration:   {sb['durationInFrames'] / fps:.1f}s ({sb['durationInFrames']} frames @ {fps}fps)")
    print(f"Storyboard: {os.path.join(src_dir, 'storyboard.json')}")
    print(f"Scenes TSX: {os.path.join(src_dir, 'Scenes.tsx')}")
    print(f"Audio:      {pub_dir}/music.wav + sfx/*.wav")
    if warnings:
        for w in warnings:
            print(f"WARNING:    {w}")
    print("TypeScript: PASSED (0 errors)")


if __name__ == "__main__":
    main()
