r"""Pull Evelynn's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_evelynn.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Evelynn.wad.client and Evelynn.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN
(Tencent client) by default.

Her events in the base bank (the client's own names; lengths and peaks measured with work/ev/snd_probe_ev.py): the
attack is EvelynnBasicAttack_OnCast (the lash, 0.37 s) and _OnHit; Whiplash casts with EvelynnE_OnCast, the empowered
one with EvelynnE2_OnCast and hits with E2_OnHit; Hate Spike casts with EvelynnQ_OnCast over Q_OnMissileLaunch (the
lasher flying), hits with Q_OnHit, each spike flies with Q2_missilelaunch and hits with Qlinemissile_OnHit; Allure casts
with EvelynnW_OnCast, its mark lands with Wmissile_OnHit (the building hum), ripens with W_OnEnemy_Mark_ready and the
charm pops with Wcharmvfx_OnBuffCast's own clip; Last Caress is EvelynnR_OnCast (the demonic burst, loudest 0.5 s in)
and R_OnHit_basic; Demon Shade starts with EvelynnPassiveDemonCloak_buffcast. Voice: the empowered whip's effort,
Allure's line on an enemy and the ult's line. The icons: Evelynn_Q1 = Q, Evelynn_W = W, Evelynn_R = R (the
bin's own references; Evelynn_Passive and Evelynn_E1/E2 are not slots here).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/evelynn/skins/base/evelynn_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/evelynn/skins/base/evelynn_base_vo_"  # same in every language
P = "Play_sfx_Evelynn_Evelynn"
V = "Play_vo_Evelynn_Evelynn"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_evelynn_sfx_attack": (P + "BasicAttack_OnCast", 1032249374, 0.4, -10),
    "league_evelynn_sfx_attack_hit": (P + "BasicAttack_OnHit", 759816667, 0.6, -10),
    "league_evelynn_sfx_e": (P + "E_OnCast", 820758133, 0.8, -8),
    "league_evelynn_sfx_e2": (P + "E2_OnCast", 219033685, 0.9, -8),
    "league_evelynn_sfx_e2_hit": (P + "E2_OnHit", 486836671, 0.6, -8),
    "league_evelynn_sfx_q": (P + "Q_OnCast", 916201395, 0.35, -9),
    "league_evelynn_sfx_q_fly": (P + "Q_OnMissileLaunch", 640132631, 0.8, -10),
    "league_evelynn_sfx_q_hit": (P + "Q_OnHit", 1019808263, 0.6, -10),
    "league_evelynn_sfx_spike": (P + "Q2_missilelaunch", 673729701, 0.9, -9),
    "league_evelynn_sfx_spike_hit": (P + "Qlinemissile_OnHit", 702338524, 0.25, -12),
    "league_evelynn_sfx_w": (P + "W_OnCast", 344879134, 0.9, -8),
    "league_evelynn_sfx_w_hit": (P + "Wmissile_OnHit", 823719887, 1.2, -9),
    "league_evelynn_sfx_w_ready": (P + "W_OnEnemy_Mark_ready", 900001697, 0.9, -8),
    "league_evelynn_sfx_w_pop": (P + "Wcharmvfx_OnBuffCast", 316845264, 0.8, -7),
    "league_evelynn_sfx_r": (P + "R_OnCast", 379728968, 1.4, -6),
    "league_evelynn_sfx_r_hit": (P + "R_OnHit_basic", 203411897, 0.8, -8),
    "league_evelynn_sfx_shade": (P + "PassiveDemonCloak_buffcast", 740290478, 1.2, -9),
    "league_evelynn_vo_e2": (V + "E2_cast3D", 747009238, 1.0, -6),
    "league_evelynn_vo_w": (V + "W_OnEnemy_start", 1799013830, 1.8, -5),
    "league_evelynn_vo_r": (V + "R_cast3D", 1114925009, 1.6, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_evelynn_skill": "ASSETS/Characters/Evelynn/HUD/Icons2D/Evelynn_Q1.dds",
    "league_evelynn_skill2": "ASSETS/Characters/Evelynn/HUD/Icons2D/Evelynn_W.dds",
    "league_evelynn_ult": "ASSETS/Characters/Evelynn/HUD/Icons2D/Evelynn_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Evelynn.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Evelynn.{args.lang}.wad.client"))
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
            print(f"{name:38s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:38s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
