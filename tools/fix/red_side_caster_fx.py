#!/usr/bin/env python3
"""The red-side pass over every hero's caster pictures (2026-10-06): baked into his frames, or made symmetric.

    python tools/fix/red_side_caster_fx.py [--hero aatrox ...]

The client never mirrors a data effect picture (champion-data.md section 6), so every caster picture lint_mod.py flags
(mirrored, more than half its opaque pixels land on empty ones) was dealt with here, hero by hero:
1. tools/fix/bake_caster_fx.py draws what rides on one of his actions into his frames (CUT: dash trails and flashes
   whose tail ran past the animation, cut there);
2. tools/art/import_native.py redraws his sheet with assets/source/native/<hero>_bake.json;
3. tools/fix/mirror_union_fx.py makes the rest left-right symmetric (SYM, the ones step 1 left: auras, shields and
   bursts that play while he walks or when a projectile lands - checked by eye: rings, sparks and flames that read
   the same mirrored).
4. HIT: pictures on a target or point that show where the blow came from (a streak or a chevron pointing on along
   the shot: league_ezreal R, league_riven's Wind Slash, league_yasuo Q and E, league_vayne's bolts) are made symmetric
   too; a slash or crescent across the target reads the same either way and stays.
KEEP is what neither fits: league_ekko's R hologram, a figure of him left where he cast it for 4 s while he walks on
(not one action, and his side-on idle had a front): tools/art/import_ekko.py makes it from Codex's front view now
(assets/source/red_side/ekko_front.png), so it is symmetric and nothing is left.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

HEROES = ["aatrox", "ahri", "akali", "alistar", "amumu", "briar", "caitlyn", "diana", "ekko", "evelynn", "ezreal",
          "fiddlesticks", "fiora", "fizz", "garen", "jax", "jhin", "jinx", "kaisa", "kayle", "kayn", "kennen", "leblanc",
          "lissandra", "masteryi", "missfortune", "nocturne", "rakan", "riven", "ryze", "sett", "sivir", "soraka", "teemo",
          "tristana", "tryndamere", "twistedfate", "varus", "veigar", "vi", "xerath", "xinzhao", "yasuo", "yone", "zilean"]
CUT = {"aatrox": ["q3_slash", "q3_slash_r"], "kaisa": ["r_trail"], "vi": ["q_go", "r_trail"], "tristana": ["q_cast"]}
SYM = {
    "ahri": ["w_orbit"], "alistar": ["e_ready", "w_butt"], "fiddlesticks": ["r_storm"], "fiora": ["v_ms_fx"],
    "jax": ["r_slam"], "jhin": ["a_reload"], "jinx": ["excited"], "kaisa": ["e_aura", "e_invis"], "kayle": ["w_heal"],
    "kennen": ["w_burst"], "masteryi": ["q_vanish", "wuju"], "missfortune": ["strut"], "rakan": ["r_start"],
    "sivir": ["e_block", "r_renew"], "soraka": ["rejuv"], "teemo": ["stealth", "w_cast"], "tristana": ["q_rapid"],
    "tryndamere": ["w_shout"], "vi": ["e_arm"], "varus": ["p_rage_on"], "yasuo": ["shield"],
    "yone": ["e_leave", "e_return", "shield"], "xinzhao": ["p_heal"],
}
KEEP = {"ekko": ["r_ghost"]}
HIT = {"ezreal": ["r_hit"], "riven": ["r_hit"], "yasuo": ["q_hit", "e_hit"], "vayne": ["hit"], "janna": ["w_hit"],
       "sivir": ["w_bounce"]}


def run(*cmd):
    r = subprocess.run([sys.executable, *cmd], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"{' '.join(cmd)} failed:\n{r.stdout}{r.stderr}")
    return r.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hero", action="append")
    args = ap.parse_args()
    for hero in args.hero or sorted(set(HEROES) | set(HIT)):
        if hero not in HEROES:
            run("tools/fix/mirror_union_fx.py", "--hero", hero,
                *[x for n in HIT[hero] for x in ("--name", f"league_{hero}_{n}")])
            print(f"league_{hero}: symmetric: {', '.join(HIT[hero])}")
            continue
        cut = [x for n in CUT.get(hero, []) for x in ("--cut", f"league_{hero}_{n}")]
        out = run("tools/fix/bake_caster_fx.py", "--hero", hero, *cut)
        left = sorted({line.split()[1] for line in out.splitlines() if line.strip().startswith("LEFT")})
        expect = sorted(f"league_{hero}_{n}" for n in SYM.get(hero, []) + KEEP.get(hero, []))
        extra = [n for n in left if n not in expect]
        if extra:
            sys.exit(f"league_{hero}: left but neither SYM nor KEEP: {', '.join(extra)}")
        run("tools/art/import_native.py", "--hero", hero)
        sym = [n for n in SYM.get(hero, []) if f"league_{hero}_{n}" in left]     # what the frames could not carry
        sym += HIT.get(hero, [])
        if sym:
            run("tools/fix/mirror_union_fx.py", "--hero", hero,
                *[x for n in sym for x in ("--name", f"league_{hero}_{n}")])
        print(out.strip().splitlines()[-1] + (f"; symmetric: {', '.join(sym)}" if sym else ""))


if __name__ == "__main__":
    main()
