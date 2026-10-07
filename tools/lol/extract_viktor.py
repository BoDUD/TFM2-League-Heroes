r"""Pull Viktor's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_viktor.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Viktor.wad.client and Viktor.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events are Play_sfx_Viktor_Viktor<spell>_<event>; the voice events Play_vo_Viktor_Viktor<key>_cast3D. The bolt
BasicAttack_missilelaunch / _OnHit; Siphon Power Q_OnCast, Q_OnHit, Q_buffactivate (the shield), QBuff_OnCast (the
empowered attack readied) and QBuff_hit (its hit); Gravity Field W_OnCast, W_OnHitLocation (the field lands) and
WDebuffSlow_buffactivate (the stun); Hextech Ray E_OnCast (the sweep) and R_hit's third variant for the aftershock (the
E missile and augment events resolve to no media in this patch's bank); Arcane Storm R_OnCast, R_hit_initial,
R_hit and R_OnHitLocation (its hum, cut short); Glorious Evolution Passive_buffactivate_self. Voice clips are
league_viktor_sfx_vo_* (never the sound's own name); W's own cast line has no media, so W speaks Spell3DWStun.
Icons: Viktor_Q1 = skill, Viktor_E1 = skill2 (W -> E; W is in its text), Viktor_R1 = ult.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/viktor/skins/base/viktor_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/viktor/skins/base/viktor_base_vo_"  # same in every language
P = "Play_sfx_Viktor_Viktor"
V = "Play_vo_Viktor_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_viktor_sfx_shot": (P + "BasicAttack_missilelaunch", 356593953, 0.5, -12),
    "league_viktor_sfx_hit": (P + "BasicAttack_OnHit", 922862014, 0.5, -12),
    "league_viktor_sfx_q_cast": (P + "Q_OnCast", 366956455, 0.6, -10),
    "league_viktor_sfx_q_hit": (P + "Q_OnHit", 748611133, 0.8, -9),
    "league_viktor_sfx_q_shield": (P + "Q_buffactivate", 643230895, 0.9, -11),
    "league_viktor_sfx_q_ready": (P + "QBuff_OnCast", 744100474, 0.7, -11),
    "league_viktor_sfx_q_blast": (P + "QBuff_hit", 531075080, 0.8, -9),
    "league_viktor_sfx_w_cast": (P + "W_OnCast", 501318637, 1.0, -10),
    "league_viktor_sfx_w_field": (P + "W_OnHitLocation", 118191803, 1.8, -10),
    "league_viktor_sfx_w_stun": (P + "WDebuffSlow_buffactivate", 168379789, 1.0, -9),
    "league_viktor_sfx_e_ray": (P + "E_OnCast", 317269538, 1.2, -8),
    "league_viktor_sfx_e_after": (P + "R_hit", 411302885, 0.9, -9),
    "league_viktor_sfx_r_cast": (P + "R_OnCast", 492941568, 1.2, -9),
    "league_viktor_sfx_r_burst": (P + "R_hit_initial", 265099124, 1.1, -8),
    "league_viktor_sfx_r_tick": (P + "R_hit", 97748433, 0.8, -11),
    "league_viktor_sfx_r_storm": (P + "R_OnHitLocation", 822444257, 1.6, -11),
    "league_viktor_sfx_evo": (P + "Passive_buffactivate_self", 1055760268, 1.4, -9),
    "league_viktor_sfx_vo_q": (V + "ViktorQBuff_cast3D", 1295973291, 2.0, -4),
    "league_viktor_sfx_vo_w": (V + "Spell3DWStun", 1422253854, 2.2, -4),
    "league_viktor_sfx_vo_e": (V + "ViktorE_cast3D", 86822936, 2.0, -4),
    "league_viktor_sfx_vo_r": (V + "ViktorR_cast3D", 545655080, 2.5, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_viktor_skill": "ASSETS/Characters/Viktor/HUD/Icons2D/Viktor_Q1.dds",
    "league_viktor_skill2": "ASSETS/Characters/Viktor/HUD/Icons2D/Viktor_E1.dds",
    "league_viktor_ult": "ASSETS/Characters/Viktor/HUD/Icons2D/Viktor_R1.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Viktor.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Viktor.{args.lang}.wad.client"))
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
