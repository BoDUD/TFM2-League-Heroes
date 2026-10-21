r"""Pull Neeko's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_neeko.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_zyra.py: reads (never writes) Game/DATA/FINAL/Champions/Neeko.wad.client and
Neeko.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event),
decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus
64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Events (named in the base skin's bin, CommunityDragon skins/skin0.bin): NeekoBasicAttack_OnMissileLaunch / OnHit,
NeekoWPassiveAttack_OnCast / OnHit (the third attack), NeekoQ_OnCast / hit1 (the burst) / hit2 (a bloom) / hit_minion,
NeekoE_OnCast / hit_root, NeekoR_cast (the charge) / NeekoP_jump (the spring) / NeekoRStun_OnBuffActivate (the landing)
/ NeekoRShield_buffactivate_self; NeekoRStun_OnBuffActivate is not in the 16.20 bank (the bin still names it): the
landing takes NeekoQ_hit3 (the last bloom's burst), its hits NeekoE_hit_empowered; NeekoP_cast / NeekoP_buffdeactivate (the add-on's disguise on and off). Voice
(Play_vo_Neeko_): NeekoQ_cast3D, NeekoE_cast3D, NeekoR_cast3D.
Icons (Neeko.bin's): Neeko_Q = skill, Neeko_E = skill2, Neeko_R = ult, Neeko_W = W, Neeko_P = passive.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/neeko/skins/base/neeko_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/neeko/skins/base/neeko_base_vo_"  # same in every language
P = "Play_sfx_Neeko_"
V = "Play_vo_Neeko_"
C = "league_neeko_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "NeekoBasicAttack_OnMissileLaunch", P + "NeekoBasicAttack_OnCast"], None, 0.8, -16),
    C + "a_hit": ([P + "NeekoBasicAttack_OnHit"], None, 0.8, -15),
    C + "w": ([P + "NeekoWPassiveAttack_OnCast"], None, 1.0, -14),
    C + "w_hit": ([P + "NeekoWPassiveAttack_OnHit"], None, 1.0, -13),
    C + "q": ([P + "NeekoQ_OnCast", P + "NeekoQ_OnMissileLaunch"], None, 1.0, -14),
    C + "q_burst": ([P + "NeekoQ_hit1"], None, 1.4, -12),
    C + "q_bloom": ([P + "NeekoQ_hit2", P + "NeekoQ_hit3"], None, 1.4, -13),
    C + "q_hit": ([P + "NeekoQ_hit_minion"], None, 0.8, -16),
    C + "e": ([P + "NeekoE_OnCast", P + "NeekoE_OnMissileLaunch"], None, 1.2, -14),
    C + "e_hit": ([P + "NeekoE_hit_root", P + "NeekoE_hit_first"], None, 1.4, -13),
    C + "r": ([P + "NeekoR_cast", P + "NeekoR_cast_self"], None, 1.6, -13),
    C + "r_jump": ([P + "NeekoP_jump"], None, 1.2, -13),
    C + "r_sh": ([P + "NeekoRShield_buffactivate_self", P + "NeekoRShield_buffactivate"], None, 1.2, -15),
    C + "r_land": ([P + "NeekoRStun_OnBuffActivate", P + "NeekoQ_hit3"], None, 1.6, -11),
    C + "r_hit": ([P + "NeekoE_hit_empowered"], None, 1.0, -14),
    C + "p_on": ([P + "NeekoP_cast", P + "NeekoP_cast_self"], None, 1.2, -14),      # the add-on's disguise
    C + "p_off": ([P + "NeekoP_buffdeactivate"], None, 1.2, -14),
    C + "vo_q": ([V + "NeekoQ_cast3D"], None, 2.0, -6),
    C + "vo_e": ([V + "NeekoE_cast3D"], None, 2.0, -6),
    C + "vo_r": ([V + "NeekoR_cast3D"], None, 2.0, -6),
}
I = "assets/characters/neeko/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_neeko_skill": I + "neeko_q.dds",
    "league_neeko_skill2": I + "neeko_e.dds",
    "league_neeko_ult": I + "neeko_r.dds",
    "league_neeko_w": I + "neeko_w.dds",
    "league_neeko_passive": I + "neeko_p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Neeko.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Neeko.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (events, mid, max_s, peak) in CLIPS.items():
            event, variants = None, []
            # (the bins' names can carry a glued character - "OnBuffActivate2", "OnCast0": also try them without it)
            for ev in [e for ev_ in events for e in (ev_, ev_[:-1])]:
                variants = banks.event_media(ev)
                if variants:
                    event = ev
                    break
            if not variants:
                sys.exit(f"{name}: none of {events} resolves - game patch changed the bank?")
            m = variants[0] if mid is None else mid
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
