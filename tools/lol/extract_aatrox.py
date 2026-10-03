"""Pull Aatrox's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_aatrox.py --lol "D:\\WeGameApps\\lol" --list
    python tools/lol/extract_aatrox.py --lol "D:\\WeGameApps\\lol" --vgmstream "<vgmstream-cli.exe>"

Same route as extract_vi.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Aatrox.wad.client and Aatrox.<lang>.wad.client, resolves base-skin Wwise events to their
media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

This kit was written in a session without the client, so the event names are not pinned yet: --list prints every
Play_sfx_Aatrox_* / Play_vo_Aatrox_* event the champion's bins name, with its media variants, and each clip below
takes the first event matching its patterns (case-insensitive, tried in order) and that event's first variant. The
script prints what it took; once the clips sound right, write the chosen event and media id into CLIPS as plain
strings and numbers, as extract_vi.py has them, so a patch that reorders the bank cannot swap them silently.
Icons the same way: the HUD icon paths the bins name, picked by slot.
"""
import argparse
import io
import os
import re
import sys
import wave

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_garen import decode, finish, lp  # noqa: E402
from riot import SoundBanks, Wad, bnk_media, parse_wpk  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MOD = os.path.join(ROOT, "league")
CHAMP = "Aatrox"
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/aatrox/skins/base/aatrox_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/aatrox/skins/base/aatrox_base_vo_"  # same path in every language WAD
BINS = ["data/characters/aatrox/aatrox.bin", "data/characters/aatrox/skins/skin0.bin",
        "data/characters/aatrox/animations/skin0.bin"]

# clip name -> (event: an exact name, or regexes tried in order on the part after Play_<kind>_Aatrox_ and a second
#               "Aatrox" (Play_sfx_Aatrox_AatroxQ_OnCast is tried as "Q_OnCast");
#               media id among the event's random variants (None: the first), max seconds, peak dBFS)
CLIPS = {
    "league_aatrox_sfx_attack_hit": ([r"^BasicAttack\w*OnHit", r"^BasicAttack\w*hit", r"^BasicAttack"], None, 0.6, -10),
    "league_aatrox_sfx_p_hit": ([r"^Passive\w*OnHit", r"^Passive\w*hit", r"^Passive"], None, 1.0, -6),
    "league_aatrox_sfx_q1": ([r"^Q1?_OnCast$", r"^Q_?1\w*Cast", r"^Q\w*OnCast"], None, 1.2, -6),
    "league_aatrox_sfx_q2": ([r"^Q_?2\w*Cast", r"^Q\w*2\w*OnCast"], None, 1.2, -6),
    "league_aatrox_sfx_q3": ([r"^Q_?3\w*Cast", r"^Q\w*3\w*OnCast"], None, 1.4, -6),
    "league_aatrox_sfx_q_slam": ([r"^Q\w*_hit$", r"^Q\w*OnHit", r"^Q\w*hit"], None, 1.0, -5),
    "league_aatrox_sfx_q_sweet": ([r"^Q\w*(sweet|crit|edge|tip)", r"^Q\w*hit_champ", r"^Q\w*Knockup", r"^Q\w*hit"], None,
                                  1.0, -4),
    "league_aatrox_sfx_e": ([r"^E_OnCast$", r"^E\w*Cast", r"^E\w*Dash"], None, 0.8, -8),
    "league_aatrox_sfx_w_cast": ([r"^W_OnCast$", r"^W\w*Cast"], None, 1.0, -7),
    "league_aatrox_sfx_w_hit": ([r"^W\w*Missile\w*hit", r"^W\w*OnHit", r"^W\w*hit"], None, 1.0, -6),
    "league_aatrox_sfx_w_pull": ([r"^W\w*(pull|bump|snap|yank|chain)", r"^W\w*2", r"^W\w*hit"], None, 1.2, -5),
    "league_aatrox_sfx_r_cast": ([r"^R_OnCast$", r"^R\w*Cast", r"^R\w*BuffActivate"], None, 2.4, -3),
    "league_aatrox_vo_q": ([r"^Q\w*cast3D", r"^Spell1", r"^Q"], None, 1.2, -2),
    "league_aatrox_vo_w": ([r"^W\w*cast3D", r"^Spell2", r"^W"], None, 1.2, -2),
    "league_aatrox_vo_r": ([r"^R\w*cast3D", r"^Spell4", r"^R"], None, 2.5, -2),
}
ICONS = {  # TFM2 slot -> regexes on the icon file name (Deathbringer Stance and Umbral Dash ride on the others)
    "league_aatrox_skill": [r"_Q1?\.", r"Q1?\.", r"Q"],
    "league_aatrox_skill2": [r"_W\.", r"W\."],
    "league_aatrox_ult": [r"_R\.", r"R\."],
}


def bin_strings(wad, pattern):
    found = set()
    for path in BINS:
        try:
            blob = wad.read_path(path)
        except KeyError:
            continue
        found.update(m.decode("latin1") for m in re.findall(pattern, blob, re.I))
    return sorted(found)


def choose(spec, names, kind):
    """The event a clip takes: an exact name, or the first name whose spell part matches one of the regexes."""
    if isinstance(spec, str):
        return spec if spec in names else None
    prefix = f"Play_{kind}_{CHAMP}_".lower()

    def part(e):
        rest = e[len(prefix):]
        return rest[len(CHAMP):] if rest.lower().startswith(CHAMP.lower()) else rest
    mine = [e for e in names if e.lower().startswith(prefix)]
    for rx in spec:
        hits = [e for e in mine if re.search(rx, part(e), re.I)]
        if hits:
            return min(hits, key=len)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    ap.add_argument("--list", action="store_true", help="print the events and icons the bins name, write nothing")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, f"{CHAMP}.wad.client"))
    events = bin_strings(main_wad, rb"Play_(?:sfx|vo)_" + CHAMP.encode() + rb"_[A-Za-z0-9_]+")
    icons = bin_strings(main_wad, rb"ASSETS/Characters/" + CHAMP.encode() + rb"/HUD/Icons2D/[A-Za-z0-9_\.]+\.(?:dds|tex)")

    banks = media = None
    if args.vgmstream or args.list:
        vo_wad = Wad(os.path.join(champs, f"{CHAMP}.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)

    if args.list:
        print(f"{len(events)} events named in the bins:")
        for e in events:
            print(f"  {e:60s} variants {banks.event_media(e)}")
        print(f"{len(icons)} icons:")
        for i in icons:
            print(f"  {i}")
        return

    if args.vgmstream:
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        playable = [e for e in events if banks.event_media(e)]
        for name, (spec, mid, max_s, peak) in CLIPS.items():
            kind = "vo" if "_vo_" in name else "sfx"
            event = choose(spec, playable, kind)
            if not event:
                print(f"{name:34s} NO EVENT matched {spec} - see --list")
                continue
            variants = banks.event_media(event)
            if mid is None:
                mid = variants[0]
            elif mid not in variants:
                sys.exit(f"{event}: media {mid} not found (variants: {variants}) - game patch changed the bank?")
            sr, x = decode(media[mid], args.vgmstream)
            pcm = finish(x, sr, max_s, peak)
            with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(pcm.tobytes())
            print(f"{name:34s} {len(pcm) / sr:4.2f}s  <- {event} media {mid} (of {variants})")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, rxs in ICONS.items():
        path = next((min(hits, key=len) for rx in rxs
                     for hits in [[i for i in icons if re.search(rx, os.path.basename(i), re.I)]] if hits), None)
        if not path:
            print(f"{name:34s} NO ICON matched {rxs} - see --list")
            continue
        data = main_wad.read_path(path)
        if data[:4] == b"TEX\0":      # newer clients ship the icons as Riot .tex
            from pose_ref import read_tex
            img = read_tex(data)
        else:
            img = Image.open(io.BytesIO(data)).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:34s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
