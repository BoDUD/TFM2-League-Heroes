"""Stage the locally delivered Poseidon MP3s after checking their digests."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("delivery", type=Path, help="Root of the unpacked Poseidon asset bundle")
    args = parser.parse_args()
    asset_root = Path(__file__).resolve().parents[1]
    repo = asset_root.parents[2]
    manifest = json.loads((asset_root / "audio/manifest.json").read_text(encoding="utf-8"))
    clips = []
    for clip in [*manifest["sfx"], *manifest["voice"]]:
        path = args.delivery / clip["mp3"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != clip["mp3_sha256"]:
            parser.error(f"Missing clip or SHA-256 mismatch: {path}")
        clips.append(path)
    destination = repo / "ragnarok/sound/sfx"
    destination.mkdir(parents=True, exist_ok=True)
    for clip in clips:
        shutil.copyfile(clip, destination / clip.name)
    print(f"{len(clips)} clips -> {destination}")


if __name__ == "__main__":
    main()
