r"""Pull Gnar's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_gnar.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

Same route as extract_zyra.py: reads (never writes) Game/DATA/FINAL/Champions/Gnar.wad.client and
Gnar.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event),
decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus
64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Events (named in gnar.bin / gnarbig.bin; both forms' sounds sit in Gnar's bank): Mini - GnarBasicAttack_OnMissileLaunch /
OnHit, GnarWHit_hit (Hyper's third hit), GnarQ_OnCast / GnarQ_hit / GnarQCatch_hit, GnarE_OnCast / GnarEBounceEnemy_hit,
GnarTransformSoon_OnBuffActivate (full Rage), GnarTransform_OnBuffActivate, GnarTransformBack_buffactivate; Mega -
GnarBigBasicAttack_OnCast / OnHit, GnarBigQ_OnCast / GnarBigQMissile_hit / GnarBigQRockGround_hit / GnarBigQ_pickup,
GnarBigW_OnCast / GnarBigW_hit2 (the smash; GnarBigCritAttack_OnHit on each unit), GnarBigE_OnCast / GnarBigE_hit (the
landing; GnarBigE_hit2 on each unit), GnarR_OnCast / GnarR_hit (the throw; GnarBigAttackTower_OnHit on each unit).
Voice: Play_vo_Gnar_GnarQ_cast3D, _GnarE_cast3D (Mini), Play_vo_GnarBig_Attack2DGeneral (the transform),
_Move2DStandard (Mega's spells), _Taunt3DGeneralK (R).
Icons (Gnar.bin's): Gnar_Q = skill, Gnar_E = skill2, GnarBig_R = ult; Gnar_W, GnarBig_Q / _W / _E, Gnar_Passive for
the README.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/gnar/skins/base/gnar_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/gnar/skins/base/gnar_base_vo_"  # same in every language
P = "Play_sfx_Gnar_"
V = "Play_vo_Gnar_"
VB = "Play_vo_GnarBig_"
C = "league_gnar_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "GnarBasicAttack_OnMissileLaunch", P + "GnarBasicAttack_OnCast"], None, 0.8, -16),
    C + "a_hit": ([P + "GnarBasicAttack_OnHit"], None, 0.8, -15),
    C + "a_hyper": ([P + "GnarWHit_hit"], None, 1.0, -13),
    C + "q": ([P + "GnarQ_OnCast", P + "GnarQMissile_OnMissileLaunch0"], None, 1.0, -14),
    C + "q_hit": ([P + "GnarQ_hit"], None, 0.8, -14),
    C + "q_catch": ([P + "GnarQCatch_hit"], None, 0.8, -13),
    C + "e": ([P + "GnarE_OnCast"], None, 1.0, -14),
    C + "e_hit": ([P + "GnarEBounceEnemy_hit"], None, 0.8, -13),
    C + "full": ([P + "GnarTransformSoon_OnBuffActivate"], None, 1.4, -14),
    C + "tf_mega": ([P + "GnarTransform_OnBuffActivate"], None, 2.0, -11),
    C + "tf_mini": ([P + "GnarTransformBack_buffactivate"], None, 1.6, -13),
    C + "m_a": ([P + "GnarBigBasicAttack_OnCast"], None, 0.8, -15),
    C + "m_hit": ([P + "GnarBigBasicAttack_OnHit"], None, 0.8, -14),
    C + "q2": ([P + "GnarBigQ_OnCast", P + "GnarBigQ_OnMissileLaunch"], None, 1.0, -13),
    C + "q2_hit": ([P + "GnarBigQMissile_hit"], None, 1.0, -12),
    C + "q_land": ([P + "GnarBigQRockGround_hit"], None, 1.0, -14),
    C + "q_pick": ([P + "GnarBigQ_pickup"], None, 0.8, -13),
    C + "w": ([P + "GnarBigW_OnCast"], None, 1.0, -13),
    C + "w_land": ([P + "GnarBigW_hit2"], None, 1.2, -11),
    C + "w_hit": ([P + "GnarBigCritAttack_OnHit"], None, 0.8, -14),
    C + "c": ([P + "GnarBigE_OnCast"], None, 1.0, -13),
    C + "c_land": ([P + "GnarBigE_hit"], None, 1.2, -11),
    C + "c_hit": ([P + "GnarBigE_hit2"], None, 0.8, -14),
    C + "r": ([P + "GnarR_OnCast"], None, 1.2, -12),
    C + "r_land": ([P + "GnarR_hit"], None, 1.6, -10),
    C + "r_hit": ([P + "GnarBigAttackTower_OnHit"], None, 0.8, -13),
    C + "vo_q": ([V + "GnarQ_cast3D"], None, 2.0, -6),
    C + "vo_e": ([V + "GnarE_cast3D"], None, 2.0, -6),
    C + "vo_mega": ([VB + "Attack2DGeneral"], None, 2.0, -6),
    C + "vo_big": ([VB + "Move2DStandard"], None, 2.0, -6),
    C + "vo_r": ([VB + "Taunt3DGeneralK", VB + "Attack2DGeneral"], None, 2.5, -6),
}
I = "assets/characters/gnar/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_gnar_skill": I + "gnar_q.dds",
    "league_gnar_skill2": I + "gnar_e.dds",
    "league_gnar_ult": I + "gnarbig_r.dds",
    "league_gnar_w": I + "gnar_w.dds",
    "league_gnar_q2": I + "gnarbig_q.dds",
    "league_gnar_w2": I + "gnarbig_w.dds",
    "league_gnar_e2": I + "gnarbig_e.dds",
    "league_gnar_passive": I + "gnar_passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Gnar.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Gnar.{args.lang}.wad.client"))
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
