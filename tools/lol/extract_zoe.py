r"""Pull Zoe's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_zoe.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_rammus.py: reads (never writes) Game/DATA/FINAL/Champions/Zoe.wad.client and
Zoe.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event),
decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus
64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Events (prefix Play_sfx_Zoe_, named in the champion's bins): ZoeBasicAttack_OnCast / OnHit, ZoeBasicAttackSpecial
(More Sparkles!), ZoeQ_OnCast / ZoeQMissile_OnMissileLaunch / ZoeQMis2_big_hit (Paddle Star), ZoeE_OnCast /
ZoeEMisAudio_OnMissileLaunch0 / ZoeEB_pop / ZoeESleepStun_buffactivate (the bubble, the trap, the sleep),
ZoeQMis2SleepCombo_big_hit (the wake), ZoeR_OnCast / ZoeR_buffonactivate (Portal Jump out and back), ZoeW_orb_missilelaunch
/ ZoeW_orb_hit (Spell Thief's missiles). Voice (Play_vo_Zoe_): ZoeQ_OnCast, ZoeE_OnCast, ZoeR_OnCast.
Icons (the bins' mImgIconName): Zoe_Q = skill, Zoe_E = skill2, Zoe_R = ult, Zoe_W = W, Zoe_P = passive (for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/zoe/skins/base/zoe_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/zoe/skins/base/zoe_base_vo_"  # same in every language
P = "Play_sfx_Zoe_"
V = "Play_vo_Zoe_"
C = "league_zoe_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "ZoeBasicAttack_OnCast", P + "ZoeBasicAttack_OnMissileLaunch"], None, 0.8, -16),
    C + "a_hit": ([P + "ZoeBasicAttack_OnHit"], None, 0.8, -15),
    C + "p": ([P + "ZoeBasicAttackSpecial_OnCast", P + "ZoeCritAttack_OnCast"], None, 1.0, -14),
    C + "p_hit": ([P + "ZoeBasicAttackSpecial_OnHit", P + "ZoeCritAttack_OnHit"], None, 1.0, -13),
    C + "q": ([P + "ZoeQ_OnCast"], None, 1.0, -14),
    C + "q_fly": ([P + "ZoeQMissile_OnMissileLaunch", P + "ZoeQMissile_OnMissileCast"], None, 1.2, -14),
    C + "q_hit": ([P + "ZoeQMis2_big_hit", P + "ZoeQMis2_OnHit"], None, 1.4, -12),
    C + "e": ([P + "ZoeE_OnCast", P + "ZoeE_Cast"], None, 1.0, -14),
    C + "e_fly": ([P + "ZoeEMisAudio_OnMissileLaunch0", P + "ZoeE_OnMissileCast"], None, 1.4, -14),
    C + "e_hit": ([P + "ZoeESleepCountDownSlow_buffactivate", P + "ZoeESleepCountDownSlow_hit"], None, 1.4, -13),
    C + "e_pop": ([P + "ZoeEB_pop"], None, 1.0, -13),
    C + "e_sleep": ([P + "ZoeESleepStun_buffactivate"], None, 1.6, -13),
    C + "e_wake": ([P + "ZoeQMis2SleepCombo_big_hit", P + "ZoeQMis2SleepCombo_OnHit"], None, 1.6, -11),
    C + "r": ([P + "ZoeR_OnCast", P + "ZoeR_cast_self"], None, 1.2, -13),
    C + "r_back": ([P + "ZoeR_buffonactivate"], None, 1.2, -13),
    C + "w_shot": ([P + "ZoeW_orb_missilelaunch"], None, 0.8, -15),
    C + "w_hit": ([P + "ZoeW_orb_hit"], None, 0.8, -14),
    C + "vo_q": ([V + "ZoeQ_OnCast"], None, 2.0, -6),
    C + "vo_e": ([V + "ZoeE_OnCast"], None, 2.0, -6),
    C + "vo_r": ([V + "ZoeR_OnCast"], None, 2.0, -6),
}
I = "assets/characters/zoe/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_zoe_skill": I + "zoe_q.dds",
    "league_zoe_skill2": I + "zoe_e.dds",
    "league_zoe_ult": I + "zoe_r.dds",
    "league_zoe_w": I + "zoe_w.dds",
    "league_zoe_passive": I + "zoe_p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Zoe.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Zoe.{args.lang}.wad.client"))
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
