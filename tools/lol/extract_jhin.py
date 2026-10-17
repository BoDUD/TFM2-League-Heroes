"""Pull Jhin's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_jhin.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Jhin.wad.client and Jhin.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language:
zh_CN (Tencent client) by default.

His events in the base bank (the client's own names): JhinBasicAttack_OnMissileLaunch / _OnHit (Whisper's shots),
JhinPassiveAttack_OnMissileCast (the fourth shot) with JhinCritAttack_OnHit, JhinPassiveReload_cast (the reload),
JhinQ_OnMissileLaunch / _OnHit and JhinQMisBounce_OnMissileLaunch (Dancing Grenade and its bounces), JhinW_OnCast /
_misslelaunch / _champ_hit (Deadly Flourish), JhinETrap_OnMissileLaunch / _OnBuffActivate and
JhinETrapSlow_buffcast_trigger / _buffdeactivate_explodeondeath (Captive Audience: thrown, landed, bloom, burst),
JhinR_OnCast, JhinRShotMis(4)_OnMissileLaunch / _hit_champ (Curtain Call and its fourth shot); the shots' reports
(_OnMissileCast: BasicAttack, PassiveAttack, JhinQ, JhinRShotMis(4)) and the casts' clicks (_OnCast: PassiveAttack,
JhinQ, JhinE, JhinRShot), which League plays with the launches. Voice: the
JhinPassiveAttack / JhinQ / JhinW / JhinR cast3D lines. The icons: Jhin_Q = Q, Jhin_W = W (E rides on it),
Jhin_R = R.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/jhin/skins/base/jhin_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/jhin/skins/base/jhin_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_jhin_sfx_attack": ("Play_sfx_Jhin_JhinBasicAttack_OnMissileLaunch", 278011448, 0.8, -9),
    "league_jhin_sfx_attack_hit": ("Play_sfx_Jhin_JhinBasicAttack_OnHit", 989996, 0.6, -14),
    "league_jhin_sfx_a4_shot": ("Play_sfx_Jhin_JhinPassiveAttack_OnMissileCast", 391640925, 1.4, -5),
    "league_jhin_sfx_a4_hit": ("Play_sfx_Jhin_JhinCritAttack_OnHit", 19197881, 0.8, -8),
    "league_jhin_sfx_reload": ("Play_sfx_Jhin_JhinPassiveReload_cast", 473566671, 1.8, -10),
    "league_jhin_sfx_q_cast": ("Play_sfx_Jhin_JhinQ_OnMissileLaunch", 724305760, 0.9, -8),
    "league_jhin_sfx_q_hit": ("Play_sfx_Jhin_JhinQ_OnHit", 106086491, 0.8, -9),
    "league_jhin_sfx_q_bounce": ("Play_sfx_Jhin_JhinQMisBounce_OnMissileLaunch", 89392143, 0.8, -11),
    "league_jhin_sfx_w_cast": ("Play_sfx_Jhin_JhinW_OnCast", 24477680, 1.6, -7),
    "league_jhin_sfx_w_shot": ("Play_sfx_Jhin_JhinW_misslelaunch", 894016858, 1.4, -5),
    "league_jhin_sfx_w_hit": ("Play_sfx_Jhin_JhinW_champ_hit", 277853850, 0.9, -7),
    "league_jhin_sfx_e_throw": ("Play_sfx_Jhin_JhinETrap_OnMissileLaunch", 380502552, 0.9, -9),
    "league_jhin_sfx_e_land": ("Play_sfx_Jhin_JhinETrap_OnBuffActivate", 346047627, 0.9, -11),
    "league_jhin_sfx_e_bloom": ("Play_sfx_Jhin_JhinETrapSlow_buffcast_trigger", 718335309, 1.6, -7),
    "league_jhin_sfx_e_boom": ("Play_sfx_Jhin_JhinETrapSlow_buffdeactivate_explodeondeath", 134754004, 1.8, -6),
    "league_jhin_sfx_r_cast": ("Play_sfx_Jhin_JhinR_OnCast", 203818737, 3.0, -6),
    "league_jhin_sfx_r_shot": ("Play_sfx_Jhin_JhinRShotMis_OnMissileLaunch", 597566841, 1.4, -5),
    "league_jhin_sfx_r_shot4": ("Play_sfx_Jhin_JhinRShotMis4_OnMissileLaunch", 162033505, 1.6, -4),
    "league_jhin_sfx_r_hit": ("Play_sfx_Jhin_JhinRShotMis_hit_champ", 466662020, 1.0, -7),
    "league_jhin_sfx_r_hit4": ("Play_sfx_Jhin_JhinRShotMis4_hit_champ", 40846800, 1.4, -6),
    # the shots' report: League plays _OnMissileCast with _OnMissileLaunch; the first clips above took only the launch
    # layer, a whoosh that peaks 250-530 ms in (the user: 「烬的技能音效…不太对」); _OnMissileCast peaks in its first 5 ms
    "league_jhin_sfx_attack_fire": ("Play_sfx_Jhin_JhinBasicAttack_OnMissileCast", 505400768, 0.8, -8),
    "league_jhin_sfx_a4_flourish": ("Play_sfx_Jhin_JhinPassiveAttack_OnCast", 655766925, 1.0, -9),
    "league_jhin_sfx_q_flick": ("Play_sfx_Jhin_JhinQ_OnCast", 196141365, 0.6, -10),
    "league_jhin_sfx_q_throw": ("Play_sfx_Jhin_JhinQ_OnMissileCast", 53175217, 0.8, -8),
    "league_jhin_sfx_e_cast": ("Play_sfx_Jhin_JhinE_OnCast", 594274455, 0.9, -9),
    "league_jhin_sfx_r_click": ("Play_sfx_Jhin_JhinRShot_OnCast", 831471844, 0.5, -10),
    "league_jhin_sfx_r_fire": ("Play_sfx_Jhin_JhinRShotMis_OnMissileCast", 46429787, 2.1, -5),
    "league_jhin_sfx_r_fire4": ("Play_sfx_Jhin_JhinRShotMis4_OnMissileCast", 642455238, 2.1, -4),
    "league_jhin_vo_a4": ("Play_vo_Jhin_JhinPassiveAttack_cast3D", 955336664, 1.4, -2),
    "league_jhin_vo_q": ("Play_vo_Jhin_JhinQ_cast3D", 1985355450, 1.4, -2),
    "league_jhin_vo_w": ("Play_vo_Jhin_JhinW_cast3D", 1266575895, 1.4, -2),
    "league_jhin_vo_r": ("Play_vo_Jhin_JhinR_cast3D", 193966281, 2.6, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_jhin_skill": "ASSETS/Characters/Jhin/HUD/Icons2D/Jhin_Q.dds",
    "league_jhin_skill2": "ASSETS/Characters/Jhin/HUD/Icons2D/Jhin_W.dds",
    "league_jhin_ult": "ASSETS/Characters/Jhin/HUD/Icons2D/Jhin_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Jhin.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Jhin.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (event, mid, max_s, peak) in CLIPS.items():
            variants = banks.event_media(event)
            if mid not in variants:
                sys.exit(f"{event}: media {mid} not found (variants: {variants}) - game patch changed the bank?")
            sr, x = decode(media[mid], args.vgmstream)
            pcm = finish(x, sr, max_s, peak)
            with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(pcm.tobytes())
            print(f"{name:34s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:34s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
