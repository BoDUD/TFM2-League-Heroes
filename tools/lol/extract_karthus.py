r"""Pull Karthus's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_karthus.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Volibear route (extract_volibear.py): reads (never writes) Game/DATA/FINAL/Champions/Karthus.wad.client and
Karthus.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (named in the champion's bin, prefix Play_sfx_Karthus_): KarthusBasicAttack_OnMissileLaunch /
_OnHit3, KarthusWallOfPain_OnCast / WallOfPainSoundDummy_OnBuffActivate4 (Wall of Pain), KarthusLayWasteA1_OnCast /
LayWasteSoundDummy_buffactivate9 / _hitmany4 / _hitsingle (Lay Waste), KarthusDefile_OnBuffActivate /
DefileSoundDummy_OnBuffCast (Defile), KarthusFallenOne_OnCast9 / FallenOneCastSound_OnBuffActivate /
FallenOneDamageSound_OnBuffActivate6 / FallenOneTarget_OnBuffActivate (Requiem), KarthusDeathDefiedBuff_OnBuffActivate8
(Death Defied, the add-on). Voice (Play_vo_Karthus_): Attack2DGeneral (Lay Waste), KarthusWallOfPain_cast3D,
KarthusDefileSoundDummy2_cast3D4, KarthusFallenOne_cast3D, Death3D (Death Defied).
Icons: Karthus_Q = skill (Lay Waste), Karthus_E = skill2 (Defile), Karthus_R = ult (Requiem), Karthus_W (Wall of Pain,
in the attack: league_karthus_w) and Karthus_Passive (league_karthus_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/karthus/skins/base/karthus_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/karthus/skins/base/karthus_base_vo_"  # same in every language
P = "Play_sfx_Karthus_"
V = "Play_vo_Karthus_"
C = "league_karthus_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "KarthusBasicAttack_OnMissileLaunch"], None, 0.8, -16),
    C + "a_hit": ([P + "KarthusBasicAttack_OnHit3"], None, 0.8, -16),
    C + "w_cast": ([P + "KarthusWallOfPain_OnCast"], None, 1.2, -13),
    C + "w": ([P + "KarthusWallOfPainSoundDummy_OnBuffActivate4"], None, 2.0, -12),
    C + "q": ([P + "KarthusLayWasteA1_OnCast"], None, 1.0, -14),
    C + "q_mark": ([P + "KarthusLayWasteSoundDummy_buffactivate9"], None, 1.0, -14),
    C + "q_boom": ([P + "KarthusLayWasteSoundDummy_hitmany4"], None, 1.2, -12),
    C + "q_lone": ([P + "KarthusLayWasteSoundDummy_hitsingle"], None, 1.2, -11),
    C + "e": ([P + "KarthusDefile_OnBuffActivate"], None, 1.5, -13),
    C + "e_loop": ([P + "KarthusDefileSoundDummy_OnBuffCast"], None, 2.5, -15),
    C + "r": ([P + "KarthusFallenOne_OnCast9"], None, 3.0, -11),
    C + "r_cast": ([P + "KarthusFallenOneCastSound_OnBuffActivate"], None, 3.0, -12),
    C + "r_boom": ([P + "KarthusFallenOneDamageSound_OnBuffActivate6"], None, 2.0, -10),
    C + "r_hit": ([P + "KarthusFallenOneTarget_OnBuffActivate"], None, 1.5, -12),
    C + "p": ([P + "KarthusDeathDefiedBuff_OnBuffActivate8"], None, 2.5, -12),
    C + "vo_q": ([V + "Attack2DGeneral"], None, 3.0, -6),
    C + "vo_w": ([V + "KarthusWallOfPain_cast3D"], None, 3.0, -6),
    C + "vo_e": ([V + "KarthusDefileSoundDummy2_cast3D4"], None, 3.0, -6),
    C + "vo_r": ([V + "KarthusFallenOne_cast3D"], None, 4.0, -6),
    C + "vo_p": ([V + "Death3D"], None, 4.0, -6),
}
I = "assets/characters/karthus/hud/icons2d/karthus_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_karthus_skill": I + "q.dds",
    "league_karthus_skill2": I + "e.dds",
    "league_karthus_ult": I + "r.dds",
    "league_karthus_w": I + "w.dds",
    "league_karthus_passive": I + "passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Karthus.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Karthus.{args.lang}.wad.client"))
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
