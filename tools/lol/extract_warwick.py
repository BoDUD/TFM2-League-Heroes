r"""Pull Warwick's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_warwick.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Volibear route (extract_volibear.py): reads (never writes) Game/DATA/FINAL/Champions/Warwick.wad.client and
Warwick.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (named in the champion's bins, prefix Play_sfx_Warwick_Warwick): BasicAttack_OnCast / _OnHit,
BasicAttackPassive1_OnHit2 (Eternal Hunger's heal bite), Q_OnCast / Q_Leap_land / Q_OnHit (Jaws of the Beast),
W_Hunt_start or WActiveHit_OnCast (Blood Hunt), E_OnCast / E2_OnBuffActivate (Primal Howl's guard and howl), R_OnCast /
Rsound_UltimateEfforts (Infinite Duress). Voice (Play_vo_Warwick_): Spell3DQCast, Spell3DE2Cast, Spell3DRHit,
Spell3DWCast.
Icons: WarwickQ = skill (Jaws of the Beast), WarwickE = skill2 (Primal Howl), WarwickR = ult (Infinite Duress), WarwickW
(Blood Hunt, in the attack: league_warwick_w) and WarwickP (league_warwick_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/warwick/skins/base/warwick_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/warwick/skins/base/warwick_base_vo_"  # same in every language
P = "Play_sfx_Warwick_Warwick"
V = "Play_vo_Warwick_"
C = "league_warwick_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.8, -14),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -15),
    C + "p_bite": ([P + "BasicAttackPassive1_OnHit2"], None, 0.9, -15),
    C + "q": ([P + "Q_OnCast"], None, 1.0, -13),
    C + "q_land": ([P + "Q_Leap_land"], None, 0.8, -14),
    C + "q_hit": ([P + "Q_OnHit"], None, 1.0, -12),
    C + "w": ([P + "W_Hunt_start", P + "WActiveHit_OnCast", P + "W_bloodhunt_50"], None, 2.0, -14),
    C + "e": ([P + "E_OnCast"], None, 1.2, -13),
    C + "e_howl": ([P + "E2_OnBuffActivate"], None, 2.0, -11),
    C + "r": ([P + "R_OnCast"], None, 1.5, -12),
    C + "r_hit": ([P + "Rsound_UltimateEfforts"], None, 2.0, -11),
    C + "vo_q": ([V + "Spell3DQCast"], None, 3.0, -6),
    C + "vo_w": ([V + "Spell3DWCast"], None, 3.0, -6),
    C + "vo_e": ([V + "Spell3DE2Cast", V + "Spell3DE1Cast"], None, 3.0, -6),
    C + "vo_r": ([V + "Spell3DRHit", V + "WarwickR_cast3D"], None, 4.0, -6),
}
I = "assets/characters/warwick/hud/icons2d/warwick"
ICONS = {  # TFM2 slot -> Riot icon
    "league_warwick_skill": I + "q.dds",
    "league_warwick_skill2": I + "e.dds",
    "league_warwick_ult": I + "r.dds",
    "league_warwick_w": I + "w.dds",
    "league_warwick_passive": I + "p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Warwick.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Warwick.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (events, mid, max_s, peak) in CLIPS.items():
            event, variants = None, []
            # (the bins' names can carry a glued character - "OnBuffActivate2", "Q_hit2": also try them without it)
            for ev in [e for ev_ in events for e in (ev_, ev_[:-1])]:
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
