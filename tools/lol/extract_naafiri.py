r"""Pull Naafiri's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_naafiri.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Volibear route (extract_volibear.py): reads (never writes) Game/DATA/FINAL/Champions/Naafiri.wad.client and
Naafiri.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Naafiri_): the sound events follow the keys since 14.x's swap, the spells keep
their old names - NaafiriR_* is Hounds' Pursuit (cast, oml, hit, kill_reset: her R key, DD id NaafiriW) and
NaafiriW_* The Call of the Pack (the roar, its 6.6 s loop: her W key, DD id NaafiriR); NaafiriPackmateR_* the
packmates in the pursuit, PackmateBasicAttack_* / PackmatePounce_* the pack's bites and leaps. Voice (Play_vo_Naafiri_):
NaafiriQ_cast3D, NaafiriE_cast3D, NaafiriW_cast3D (the roar that opens the ult), NaafiriR_cast3D.
Icons: Icons_Naafiri_Q = skill (Darkin Daggers), _E = skill2 (Eviscerate), _W = ult (Hounds' Pursuit: Data Dragon's
NaafiriW.png), _R = the roar (league_naafiri_roar, The Call of the Pack), _P = the passive (league_naafiri_passive).
"""
import argparse
import io
import os
import sys
import wave

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_garen import decode, finish, lp  # noqa: E402
from riot import SoundBanks, Wad, bnk_media, parse_wpk  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MOD = os.path.join(ROOT, "league")
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/naafiri/skins/base/naafiri_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/naafiri/skins/base/naafiri_base_vo_"  # same in every language
P = "Play_sfx_Naafiri_"
V = "Play_vo_Naafiri_"
C = "league_naafiri_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "NaafiriBasicAttack_OnCast"], None, 0.6, -14),
    C + "a_hit": ([P + "NaafiriBasicAttack_OnHit"], None, 0.8, -15),
    C + "pk_bite": ([P + "PackmateBasicAttack_OnHit"], None, 0.6, -17),
    C + "pk_leap": ([P + "PackmatePounce_Qhit_cast"], None, 0.9, -15),
    C + "q": ([P + "NaafiriQ_OnMissileLaunch", P + "NaafiriQ_OnCast"], None, 1.0, -13),
    C + "q_hit": ([P + "NaafiriQ_OnHit"], None, 1.0, -13),
    C + "q2": ([P + "NaafiriQRecast_OnMissileLaunch", P + "NaafiriQRecast_OnCast"], None, 1.0, -13),
    C + "q2_hit": ([P + "NaafiriQRecast_OnHit"], None, 1.0, -12),
    C + "e": ([P + "NaafiriE_OnCast"], None, 1.0, -13),
    C + "e_hit": ([P + "NaafiriE_hit"], None, 0.6, -14),
    C + "e_end": ([P + "NaafiriE_obd"], None, 1.0, -14),
    C + "r_roar": ([P + "NaafiriW_cast"], None, 2.0, -12),
    C + "r_dash": ([P + "NaafiriR_cast", P + "NaafiriR_oml"], None, 1.2, -12),
    C + "r_hit": ([P + "NaafiriR_hit"], None, 0.8, -12),
    C + "r_pack": ([P + "NaafiriPackmateR_hit"], None, 0.5, -15),
    C + "r_reset": ([P + "NaafiriR_kill_reset"], None, 2.0, -12),
    C + "vo_q": ([V + "NaafiriQ_cast3D"], None, 2.5, -6),
    C + "vo_e": ([V + "NaafiriE_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "NaafiriW_cast3D", V + "NaafiriR_cast3D"], None, 3.0, -6),
}
I = "assets/characters/naafiri/hud/icons2d/icons_naafiri_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_naafiri_skill": I + "q.dds",
    "league_naafiri_skill2": I + "e.dds",
    "league_naafiri_ult": I + "w.dds",
    "league_naafiri_roar": I + "r.dds",
    "league_naafiri_passive": I + "p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Naafiri.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Naafiri.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (events, mid, max_s, peak) in CLIPS.items():
            event, variants = None, []
            for ev in events:
                variants = banks.event_media(ev)
                if variants:
                    event = ev
                    break
            if not variants:
                sys.exit(f"{name}: none of {events} resolves - game patch changed the bank?")
            m = variants[0] if mid is None else variants[min(mid, len(variants) - 1)]
            sr, x = decode(media[m], args.vgmstream)
            pcm = finish(x, sr, max_s, peak)
            with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(pcm.tobytes())
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event} ({len(variants)} variants)")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
