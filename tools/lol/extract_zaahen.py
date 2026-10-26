r"""Pull Zaahen's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_zaahen.py --lol "D:\WeGameApps\lol" --vgmstream C:\t\ks_tools\vgm\vgmstream-cli.exe

extract_skarner.py's route: reads (never writes) Game/DATA/FINAL/Champions/Zaahen.wad.client and
Zaahen.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice:
zh_CN. Events (the names his bins carry, Play_sfx_Zaahen_Zaahen*): the glaive's swing and hit; The Darkin Glaive's
cast, its empowered strikes, the recast and its uppercut's hit; Dreaded Return's cast and its hit on a champion;
Aureate Rush's cast and its outer edge; Grim Deliverance's cast, its shockwave and its hit on a champion; Cultivation of
War full, the revive. Voice (Play_vo_Zaahen_*): The Darkin Glaive's, Dreaded Return's, Aureate Rush's and Grim
Deliverance's casts, Determination at full and the revive.
Icons (the champion bin's hud/icons2d): ZaahenQ = skill, ZaahenW = skill2, ZaahenR = ult, ZaahenP = Cultivation of War
(league_zaahen_passive), ZaahenE = Aureate Rush (league_zaahen_e), ZaahenQ2 = the glaive's recast (league_zaahen_q2).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/zaahen/skins/base/zaahen_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/zaahen/skins/base/zaahen_base_vo_"  # same in every language
P = "Play_sfx_Zaahen_Zaahen"
V = "Play_vo_Zaahen_"
C = "league_zaahen_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.7, -9),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.7, -8),
    C + "q": ([P + "Q_OnCast", P + "Q1_buffactivate"], None, 1.2, -7),
    C + "q_hit": ([P + "QAttack_OnHit"], None, 1.0, -6),
    C + "q2": ([P + "Q2_OnCast", P + "Q2_buffactivate"], None, 1.2, -7),
    C + "q_up": ([P + "Q2Attack_OnHit"], None, 1.2, -5),
    C + "w": ([P + "W_OnCast", P + "W_OnMissileLaunch"], None, 1.5, -6),
    C + "w_hit": ([P + "W_hit_champion", P + "W_pull_champion"], None, 1.2, -6),
    C + "e": ([P + "E_OnCast"], None, 1.2, -6),
    C + "e_hit": ([P + "EAttack_hit_outer", P + "EAttack_AoE_buffactivate"], None, 1.2, -6),
    C + "r": ([P + "R_OnCast"], None, 1.8, -6),
    C + "r_slam": ([P + "R_AoE_buffactivate", P + "R_dash"], None, 2.0, -5),
    C + "r_hit": ([P + "R_AoE_hit_champion"], None, 1.5, -5),
    C + "p_full": ([P + "P_castAF", P + "P_loop_stacks_max"], None, 1.5, -7),
    C + "rv": ([P + "P_revive_buffactivate"], None, 3.0, -6),
    C + "vo_q": ([V + "ZaahenQAttack_cast3D"], None, 2.5, -6),
    C + "vo_w": ([V + "ZaahenW_cast3D", V + "ZaahenW_cast3DK"], None, 2.5, -6),
    C + "vo_e": ([V + "ZaahenE_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "ZaahenR_cast3D"], None, 3.0, -6),
    C + "vo_p": ([V + "Spell3DPMax"], None, 3.0, -6),
    C + "vo_rv": ([V + "Spell3DPRevive"], None, 3.5, -6),
}
I = "assets/characters/zaahen/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon (file names searched in the WAD when these are not there)
    "league_zaahen_skill": "zaahenq",
    "league_zaahen_skill2": "zaahenw",
    "league_zaahen_ult": "zaahenr",
    "league_zaahen_e": "zaahene",
    "league_zaahen_q2": "zaahenq2",
    "league_zaahen_passive": "zaahenp",
}


def icon_path(wad, stem):
    """The WAD path of an icon: hud/icons2d/<stem>.dds or .tex (None when neither is there)."""
    for ext in (".dds", ".tex", ".png"):
        p = I + stem + ext
        try:
            wad.read_path(p)
            return p
        except Exception:
            pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    ap.add_argument("--icon", nargs="*", default=[], help="slot=wad/path overrides")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Zaahen.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Zaahen.{args.lang}.wad.client"))
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

    over = dict(kv.split("=", 1) for kv in args.icon)
    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, stem in ICONS.items():
        path = over.get(name) or icon_path(main_wad, stem)
        if path is None:
            sys.exit(f"{name}: no {I}{stem}.dds - pass --icon {name}=<wad path> (see the WAD's hud/icons2d entries)")
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
