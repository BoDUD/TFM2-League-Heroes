"""tft_scuttlecrab's idle_base at the size GPT shrank the crab to (PR #784, 29929a743 「缩小迅捷蟹」).

GPT's commit drew the crab's hd_ and 1x frames at about 85 % and wrote its idle reel (idle / hd_idle: frame 0 held +
snippets) from the smaller idle frame, but left idle_base / hd_idle_base - hero_reels.py's frame 0, which every later run
starts from, and the first frame illaoi_souls.py takes the crab's spirit from - pointing at the old, bigger idle frame.
So a hero_reels.py run put the bigger crab back into his idle and ban/pick card (frame 0 is 122 x 82 hd px, the
frames around it 104 x 70) and hero_reels.py --check failed. This points idle_base / hd_idle_base at the idle's frame 0
as GPT drew it (the same rect, no pixel moved); hero_reels.py --hero scuttlecrab then writes the reels GPT's commit
holds, frame for frame. lo_ (the UI's frames) GPT left at the old size; so does this.

    python tools/fix/gpt784_review/scuttlecrab_idle_base.py            # write
    python tools/fix/gpt784_review/scuttlecrab_idle_base.py --check    # exit 1 when not done
"""
import json
import os
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
FANIM = os.path.join(REPO, "tft", "champions", "tft_scuttlecrab#anim.fanim")


def main():
    check = "--check" in sys.argv[1:]
    raw = open(FANIM, "rb").read()
    doc = json.loads(raw.decode("utf-8-sig"))
    an = doc["anims"]
    todo = []
    for pre in ("", "hd_"):
        base, idle = an[pre + "idle_base"]["frames"], an[pre + "idle"]["frames"]
        want = idle[0]["data"]
        if len(base) != 1:
            sys.exit(f"{pre}idle_base: {len(base)} frames, this tool knows the crab's single one")
        if base[0]["data"] != want:
            todo.append(pre + "idle_base")
            base[0]["data"] = dict(want)
    if check:
        print("tft_scuttlecrab idle_base: " + ("ok" if not todo else "not at GPT's idle frame 0: " + ", ".join(todo)))
        sys.exit(1 if todo else 0)
    if todo:
        open(FANIM, "wb").write(json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    print("tft_scuttlecrab idle_base: " + ("pointed at GPT's idle frame 0: " + ", ".join(todo) if todo else "already done"))


if __name__ == "__main__":
    main()
