r"""Pull Bel'Veth's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_belveth.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Zac route (extract_zac.py): reads (never writes) Game/DATA/FINAL/Champions/Belveth.wad.client and
Belveth.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Belveth_Belveth, the names her skin bin lists): the wing-blade's swing and hit; Void
Surge's cast and hit; Above and Below's cast, the slam (W_knockup) and its hit; Endless Banquet's cast, the coral burst
(RSteroid_cast) and its hit; Royal Maelstrom's cast and its slice hit; the coral eaten (R_buffactivate_self). Voice
(Play_vo_Belveth_): BelvethW_cast3D and BelvethE_cast3D; the banks have no line for Void Surge or Endless Banquet, so Q
takes Attack2DGeneral and R her taunt (Taunt3DGeneral).
Icons: BelvethQ (the Void Surge strip BV_Q_1) = skill, BelvethW = skill2, BelvethR = ult, BelvethE = Royal Maelstrom
(league_belveth_e), Belveth_Passive = Death in Lavender (league_belveth_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/belveth/skins/base/belveth_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/belveth/skins/base/belveth_base_vo_"  # same in every language
P = "Play_sfx_Belveth_Belveth"
V = "Play_vo_Belveth_"
C = "league_belveth_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS); the sfx at the level Zac's got, the voice as the others', the storm's slices quiet (they
# play every e_p ticks)
CLIPS = {
    C + "a": ([P + "BasicAttack_cast_slow", P + "BasicAttack_cast_fast"], None, 0.6, -9),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.7, -8),
    C + "q": ([P + "Q_cast"], None, 0.9, -6),
    C + "q_hit": ([P + "Q_hit"], None, 0.8, -7),
    C + "w": ([P + "W_OnCast", P + "W_missilelaunch"], None, 1.0, -6),
    C + "w_slam": ([P + "W_knockup"], None, 1.2, -5),
    C + "w_hit": ([P + "W_hit"], None, 0.9, -7),
    C + "e": ([P + "E_OnCast", P + "E_cast"], None, 1.5, -6),
    C + "e_hit": ([P + "E_hit", P + "E_slice_cast"], None, 0.5, -14),
    C + "r": ([P + "R_OnCast", P + "R_transform0"], None, 2.0, -5),
    C + "r_burst": ([P + "RSteroid_cast", P + "R_buffactivate_self"], None, 2.0, -5),
    C + "r_hit": ([P + "R_hit"], None, 0.9, -7),
    C + "c_eat": ([P + "R_buffactivate_self", P + "RCorpse_OnBuffDeactivate", P + "RPassive_hit"], None, 1.2, -7),
    C + "vo_q": ([V + "Attack2DGeneral"], None, 2.5, -6),
    C + "vo_w": ([V + "BelvethW_cast3D"], None, 2.5, -6),
    C + "vo_e": ([V + "BelvethE_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "Taunt3DGeneral", V + "Laugh3DGeneral"], None, 3.0, -6),
}
I = "assets/characters/belveth/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon (file names searched in the WAD when these are not there)
    "league_belveth_skill": "bv_q_1",
    "league_belveth_skill2": "belvethw",
    "league_belveth_ult": "belvethr",
    "league_belveth_e": "belvethe",
    "league_belveth_passive": "belveth_passive",
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
    main_wad = Wad(os.path.join(champs, "Belveth.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Belveth.{args.lang}.wad.client"))
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
