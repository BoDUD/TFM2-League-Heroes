r"""Pull Jarvan IV's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_jarvaniv.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

Same route as extract_nasus.py: reads (never writes) Game/DATA/FINAL/Champions/JarvanIV.wad.client and
JarvanIV.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a media id is given), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_JarvanIV_JarvanIV, named in the wad's bins): BasicAttack_OnCast / _OnHit,
MartialCadenceAttack_hit, DemacianStandard_OnCast / _fall / _hit, DragonStrike_OnCast / _hit, DragonStrikePH_hit (the
drag to the standard), GoldenAegis_OnCast, Cataclysm_OnCast / _hit / _missilelaunch. Voice (Play_vo_JarvanIV_):
Spell3DQCast, Spell3DECast, Spell3DBasic (W), Spell3DRCast (the spoken lines; the bins' cast3D names do not resolve).
Icons: JarvanIVE = skill (E -> Q), JarvanIVQ = skill2, JarvanIVR = ult; JarvanIVW and JarvanIVP too
(league_jarvaniv_w, _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/jarvaniv/skins/base/jarvaniv_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/jarvaniv/skins/base/jarvaniv_base_vo_"  # same in every language
P = "Play_sfx_JarvanIV_JarvanIV"
V = "Play_vo_JarvanIV_"
C = "league_jarvaniv_sfx_"

# clip name -> (event, media id among the event's variants or None for the first, max seconds, peak dBFS)
CLIPS = {
    C + "a_swing": (P + "BasicAttack_OnCast", None, 0.6, -16),
    C + "a_hit": (P + "BasicAttack_OnHit", None, 0.6, -14),
    C + "p_hit": (P + "MartialCadenceAttack_hit", None, 0.9, -12),
    C + "e": (P + "DemacianStandard_OnCast", None, 0.8, -13),
    C + "e_flag": (P + "DemacianStandard_fall", None, 1.2, -12),
    C + "e_hit": (P + "DemacianStandard_hit", None, 1.0, -12),
    C + "q": (P + "DragonStrike_OnCast", None, 1.0, -12),
    C + "q_hit": (P + "DragonStrike_hit", None, 1.0, -12),
    C + "q_dash": (P + "DragonStrikePH_hit", None, 1.2, -12),
    C + "q_land": (P + "DemacianStandard_hit", None, 1.0, -12),
    C + "w": (P + "GoldenAegis_OnCast", None, 1.5, -11),
    C + "r": (P + "Cataclysm_OnCast", None, 1.5, -11),
    C + "r_land": (P + "Cataclysm_missilelaunch", None, 2.0, -10),
    C + "r_hit": (P + "Cataclysm_hit", None, 1.2, -12),
    C + "vo_q": (V + "Spell3DQCast", None, 2.0, -6),
    C + "vo_e": (V + "Spell3DECast", None, 2.0, -6),
    C + "vo_w": (V + "Spell3DBasic", None, 2.0, -6),
    C + "vo_r": (V + "Spell3DRCast", None, 2.5, -6),
}
I = "assets/characters/jarvaniv/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_jarvaniv_skill": I + "jarvanive.dds",
    "league_jarvaniv_skill2": I + "jarvanivq.dds",
    "league_jarvaniv_ult": I + "jarvanivr.dds",
    "league_jarvaniv_w": I + "jarvanivw.dds",
    "league_jarvaniv_passive": I + "jarvanivp.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "JarvanIV.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"JarvanIV.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (event, mid, max_s, peak) in CLIPS.items():
            variants = banks.event_media(event)
            if mid is None and variants:
                mid = variants[0]
            if mid not in variants:
                sys.exit(f"{event}: media {mid} not found (variants: {variants}) - game patch changed the bank?")
            sr, x = decode(media[mid], args.vgmstream)
            pcm = finish(x, sr, max_s, peak)
            with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(pcm.tobytes())
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
