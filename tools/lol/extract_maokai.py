r"""Pull Maokai's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_maokai.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_jarvaniv.py: reads (never writes) Game/DATA/FINAL/Champions/Maokai.wad.client and
Maokai.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a media id is given), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Maokai_Maokai, named in the wad's bins; several named there do not resolve in the
bank - PassiveAttack_OnCast1, TrunkLineMissile_hit, Sapling2_missilelaunch*, rsoundmis_OnMissileLaunch2 - so their
nearest resolving neighbours stand in): BasicAttack_OnCast / _OnHit, BasicAttack2_OnHit (Sap Magic's blow),
PassiveReady_OnBuffActivate (the heal), Q_OnCast, Qmissile_OnMissileLaunch / _OnHit, W_OnCast, Wroot_OnBuffCast,
CritAttack_OnHit (W's blow), E_OnCast, EMissile_Landing_Dirt, R_OnCast, rsoundmis_OnMissileLaunchEnd (the wall),
rmis_OnHit; E_AggroSound_buffcast (the pounce) and E_Explosion (prefix Play_sfx_Maokai_). Voice
(Play_vo_Maokai_): MaokaiQ_cast3D, Attack2DGeneral (no W line), MaokaiE_cast3D, MaokaiRMis_cast3D.
Icons: maokai_q = skill, maokai_w = skill2, maokai_r = ult; maokai_e and maokai_passive too (league_maokai_e,
_passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/maokai/skins/base/maokai_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/maokai/skins/base/maokai_base_vo_"  # same in every language
P = "Play_sfx_Maokai_Maokai"
S = "Play_sfx_Maokai_"
V = "Play_vo_Maokai_"
C = "league_maokai_sfx_"

# clip name -> (events tried in order, media id among the event's variants or None for the first, max seconds, peak)
CLIPS = {
    C + "a_swing": ([P + "BasicAttack_OnCast"], None, 0.6, -16),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.6, -14),
    C + "p_hit": ([P + "BasicAttack2_OnHit"], None, 0.9, -12),
    C + "p_heal": ([P + "PassiveReady_OnBuffActivate"], None, 1.2, -13),
    C + "q": ([P + "Q_OnCast"], None, 1.0, -12),
    C + "q_land": ([P + "Qmissile_OnMissileLaunch"], None, 1.2, -11),
    C + "q_hit": ([P + "Qmissile_OnHit"], None, 0.9, -12),
    C + "w": ([P + "W_OnCast"], None, 1.2, -12),
    C + "w_land": ([P + "Wroot_OnBuffCast"], None, 1.2, -11),
    C + "w_hit": ([P + "CritAttack_OnHit"], None, 1.0, -12),
    C + "e": ([P + "E_OnCast"], None, 0.9, -13),
    C + "e_land": ([P + "EMissile_Landing_Dirt", P + "Emissile_landing_dirt"], None, 1.0, -13),
    C + "e_burst": ([S + "E_AggroSound_buffcast"], None, 1.0, -12),
    C + "e_hit": ([S + "E_Explosion", S + "E_explosion"], None, 1.2, -11),
    C + "r": ([P + "R_OnCast"], None, 1.5, -11),
    C + "r_wall": ([P + "rsoundmis_OnMissileLaunchEnd"], None, 2.5, -10),
    C + "r_hit": ([P + "rmis_OnHit"], None, 1.2, -12),
    C + "vo_q": ([V + "MaokaiQ_cast3D", V + "MaokaiQ_OnCast"], None, 2.0, -6),
    C + "vo_w": ([V + "Attack2DGeneral", V + "Attack2D"], None, 2.0, -6),
    C + "vo_e": ([V + "MaokaiE_cast3D"], None, 2.0, -6),
    C + "vo_r": ([V + "MaokaiRMis_cast3D"], None, 2.5, -6),
}
I = "assets/characters/maokai/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_maokai_skill": I + "maokai_q.dds",
    "league_maokai_skill2": I + "maokai_w.dds",
    "league_maokai_ult": I + "maokai_r.dds",
    "league_maokai_e": I + "maokai_e.dds",
    "league_maokai_passive": I + "maokai_passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Maokai.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Maokai.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (events, mid, max_s, peak) in CLIPS.items():
            got = None
            for event in events:
                variants = banks.event_media(event)
                if variants:
                    got = (event, variants)
                    break
            if got is None:
                sys.exit(f"{name}: none of {events} resolves - game patch changed the bank?")
            event, variants = got
            m = variants[0] if mid is None else mid
            if m not in variants:
                sys.exit(f"{event}: media {m} not found (variants: {variants})")
            sr, x = decode(media[m], args.vgmstream)
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
