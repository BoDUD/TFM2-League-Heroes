"""league_nasus's attack, Q and E played the way League's Nasus plays them (the user, 2026-11-19: 「狗头的平A动作不像英雄联盟的
重改 包括释放其他技能时都要像英雄联盟的动作才行」), both forms (base and the R form's b_ tags), from pictures his sheet
already holds - no square is drawn or moved, a frame is a rect the sheet has.

League's clips (tools/lol/pose_ref.py --champ Nasus, renders local only). Only pictures of his stance's set are used
(the idle, GPT's attack, hit, skill[1..5], ult[3]): GPT drew his cast frames (skill[0], skill2, skill_w, the other ult
frames) in a second generation - slimmer, lava all over (tools/fix/gpt784_review/nasus_cast_colours.py only matched
their colours) - and mixed into these actions they read as the model changing (「还是有点变形」):
- nasus_attack1: the staff swung up and over his head, then down in front of him - a chop. GPT's attack was a lunge
  with the staff thrust forward like a spear. Now: the stance, the staff raised (GPT's attack[1]), over his head
  (skill[1], skill[2]), chopped down to the ground in front (skill[3], held longest: the blow), back up (skill[4]);
- Nasus_Spell1 (Q, Siphoning Strike): the staff raised high, then a slam into a low crouch, held for most of the clip.
  Now: the stance, both hands over his head (ult[3]), the slam into the crouch (skill[3], held over two frames),
  rising (skill[4]), GPT's last Q frame (skill[5], the idle reel's pick); the R form the same with its own pictures
  (b_skill[2] for the raise: the R form has no ult);
- Nasus_Base_Spell3_Full (E, Spirit Fire): the staff lifted high over his head, then aimed forward at the ground.
  Now: the stance, the staff raised (attack[1]), over his head (ult[3], held), aimed forward and down (skill[4]), back
  (skill[5]).
Each keeps its length (data_champion: attack 26 ticks = 433 ms, skill / skill2 24 = 400 ms). W (skill_w) and R (ult)
keep GPT's frames.

nasus_actions.json: per action its frames - the source picture (as GPT's tags held it before this), its ms and its
rects in the hd_, 1x and lo_ frames - and the hit's frame 0 (hit0: the braced guard tools/fix/gpt784_review/
nasus_hit.py put there, which was attack[4]). The hd strips of these actions (assets/source/ppu[/orig]/nasus_<tag>.png,
tools/fix/xinzhao_galio_1119/sheetkit.py's strip()) are written from the tags, so tools/art/ppu_hd.py makes the same
actions again. Run tools/art/hero_reels.py --hero nasus after it (the idle and BP reels are cut from these actions).

    python tools/fix/gpt784_review/nasus_actions.py [--check]
"""
import json
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
STEM = os.path.join(ROOT, "league", "champions", "league_nasus")
TABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nasus_actions.json")
PRE = {"hd_": "hd_", "1x": "", "lo_": "lo_"}


def data(r):
    return {k: float(v) for k, v in zip(("x", "y", "w", "h"), r)}


def main():
    check = "--check" in sys.argv
    raw = open(STEM + "#anim.fanim", "rb").read().decode("utf-8-sig")
    doc = json.loads(raw)
    an = doc["anims"]
    table = json.load(open(TABLE, encoding="utf-8"))
    bad = []
    for tag, frames in table["actions"].items():
        for key, pre in PRE.items():
            want = [{"duration": round(f["ms"] / 1000, 6), "data": data(f["rects"][key])} for f in frames]
            if an[pre + tag]["frames"] != want:
                bad.append(pre + tag)
                an[pre + tag]["frames"] = want
    for form, rects in table["hit0"].items():
        for key, pre in PRE.items():
            f = an[f"{pre}{form}hit"]["frames"][0]
            if f["data"] != data(rects[key]):
                bad.append(f"{pre}{form}hit[0]")
                f["data"] = data(rects[key])
    if check:
        print("nasus actions: OK" if not bad else f"nasus actions: {len(bad)} tags not as this tool leaves them: "
              + ", ".join(bad[:8]))
        sys.exit(1 if bad else 0)
    open(STEM + "#anim.fanim", "wb").write(json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    sys.path.insert(0, os.path.join(ROOT, "tools", "fix", "xinzhao_galio_1119"))
    from sheetkit import Kit
    k = Kit(ROOT, "league", "nasus")
    for tag in table["actions"]:
        k.strip(tag)
    print(f"nasus actions: {len(bad)} tags written" + (": " + ", ".join(bad) if bad else "") + "; strips of "
          + ", ".join(table["actions"]))


if __name__ == "__main__":
    main()
