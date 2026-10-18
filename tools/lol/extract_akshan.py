r"""Pull Akshan's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_akshan.py --lol "D:\WeGameApps\lol" --vgmstream pathgmstream-cli.exe

Same route as extract_wukong.py: reads (never writes) Game/DATA/FINAL/Champions/Akshan.wad.client and
Akshan.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a media id is given), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Akshan_Akshan, named in the champion's bins): BasicAttack / BasicAttack2
_OnMissileCast / _OnHit (the double shot), PassiveDetonate_hit, Q_OnCast / Q_missilelaunch_return / Q_hit_champ,
E_OnCast / E_swinging_buffactivate / EAttack_OnMissileCast / EAttack_OnHit / E3_OnCast, WStealth_buffactivate,
WMark_buffactivate, WRevive_buffcast, WGold_buffcast, R_OnCast / RAmmo_cast / RMissile_OnMissileLaunch / RMissile_OnHit.
Voice (Play_vo_Akshan_Akshan): Q_cast3D, E2_cast3D, W_cast3D, R_cast3D.
Icons: akshan_q = skill (Q), akshan_e = skill2 (E), Akshan_R = ult; akshan_w and akshan_p too (league_akshan_w,
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/akshan/skins/base/akshan_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/akshan/skins/base/akshan_base_vo_"  # same in every language
P = "Play_sfx_Akshan_Akshan"
V = "Play_vo_Akshan_Akshan"
C = "league_akshan_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnMissileCast"], None, 0.6, -16),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.6, -16),
    C + "a2": ([P + "BasicAttack2_OnMissileCast"], None, 0.6, -18),
    C + "a_hit2": ([P + "BasicAttack2_OnHit0", P + "BasicAttack2_OnHit"], None, 0.6, -18),
    C + "p_hit": ([P + "PassiveDetonate_hit", P + "PassiveDetonate_hit5"], None, 0.9, -12),
    C + "q": ([P + "Q_OnCast", P + "Q_missilelaunch"], None, 0.9, -13),
    C + "q_turn": ([P + "Q_missilelaunch_return", P + "Q_catch"], None, 0.8, -16),
    C + "q_hit": ([P + "Q_hit_champ", P + "Q_hit_minion"], None, 0.8, -13),
    C + "e": ([P + "E_OnCast"], None, 1.0, -13),
    C + "e_swing": ([P + "E_swinging_buffactivate", P + "E_idle"], None, 1.2, -16),
    C + "e_shot": ([P + "EAttack_OnMissileCast"], None, 0.5, -17),
    C + "e_hit": ([P + "EAttack_OnHit"], None, 0.5, -17),
    C + "e_roll": ([P + "E3_OnCast", P + "E2_OnCast"], None, 0.9, -13),
    C + "w": ([P + "WStealth_buffactivate"], None, 1.0, -13),
    C + "w_mark": ([P + "WMark_buffactivate", P + "WMark_buffcast"], None, 1.0, -13),
    C + "w_revive": ([P + "WRevive_buffcast"], None, 1.6, -11),
    C + "w_gold": ([P + "WGold_buffcast"], None, 1.0, -13),
    C + "r": ([P + "R_OnCast"], None, 1.4, -11),
    C + "r_store": ([P + "RAmmo_cast"], None, 0.6, -15),
    C + "r_shot": ([P + "RMissile_OnMissileLaunch", P + "RMissile_OnCast"], None, 0.8, -12),
    C + "r_hit": ([P + "RMissile_OnHit"], None, 0.8, -12),
    C + "vo_q": ([V + "Q_cast3D"], None, 2.0, -6),
    C + "vo_e": ([V + "E2_cast3D"], None, 2.0, -6),
    C + "vo_w": ([V + "W_cast3D"], None, 2.0, -6),
    C + "vo_r": ([V + "R_cast3D", V + "RMissile_cast3D"], None, 2.5, -6),
}
I = "assets/characters/akshan/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_akshan_skill": I + "akshan_q.dds",
    "league_akshan_skill2": I + "akshan_e.dds",
    "league_akshan_ult": I + "akshan_r.dds",
    "league_akshan_w": I + "akshan_w.dds",
    "league_akshan_passive": I + "akshan_p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Akshan.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Akshan.{args.lang}.wad.client"))
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
