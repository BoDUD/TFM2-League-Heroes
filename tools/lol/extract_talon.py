r"""Pull Talon's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_talon.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_zed.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Talon.wad.client and Talon.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN.

His events (found in his bins by work/tl/snd_names_tl.py, picked with work/tl/snd_probe_tl.py): the slash
TalonBasicAttack_OnCast / _OnHit, the bleed TalonPassive_hit; Noxian Diplomacy TalonQ_cast (the leap), TalonQAttack_OnCast
(the stab) and TalonQAttack_OnHit; Rake TalonW_OnCast, TalonWMissileOne_OnHit (out), TalonWMissileTwo_OnMissileLaunch /
_OnHit (back); Assassin's Path TalonE_cast; Shadow Assault TalonR_OnCast, TalonR_hit, TalonR_hold_active (the blades
come back). Voice: Q, W, E (Spell3DECast), R.
Icons: TalonW = skill (Rake), TalonQ = skill2 (Noxian Diplomacy), TalonR = ult (Assassin's Path is automatic).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/talon/skins/base/talon_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/talon/skins/base/talon_base_vo_"  # same in every language
P = "Play_sfx_Talon_Talon"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_talon_sfx_a_swing": (P + "BasicAttack_OnCast", 300418282, 0.4, -11),
    "league_talon_sfx_a_hit": (P + "BasicAttack_OnHit", 61863565, 0.4, -11),
    "league_talon_sfx_p_bleed": (P + "Passive_hit", 1035343969, 1.2, -8),
    "league_talon_sfx_q": (P + "Q_cast", 780715100, 0.6, -9),
    "league_talon_sfx_q_stab": (P + "QAttack_OnCast", 593266443, 0.5, -9),
    "league_talon_sfx_q_hit": (P + "QAttack_OnHit", 579209947, 0.5, -8),
    "league_talon_sfx_w": (P + "W_OnCast", 690050094, 0.6, -9),
    "league_talon_sfx_w_hit": (P + "WMissileOne_OnHit", 724494087, 0.4, -11),
    "league_talon_sfx_w_back": (P + "WMissileTwo_OnMissileLaunch", 222513359, 0.5, -10),
    "league_talon_sfx_w_hit2": (P + "WMissileTwo_OnHit", 607561340, 0.45, -10),
    "league_talon_sfx_e": (P + "E_cast", 611480907, 0.45, -9),
    "league_talon_sfx_r": (P + "R_OnCast", 605543501, 1.0, -8),
    "league_talon_sfx_r_hit": (P + "R_hit", 976149757, 0.55, -9),
    "league_talon_sfx_r_back": (P + "R_hold_active", 343872035, 0.8, -9),
    "league_talon_sfx_vo_q": ("Play_vo_Talon_TalonQ_cast3D", 1779008074, 1.2, -4),
    "league_talon_sfx_vo_w": ("Play_vo_Talon_TalonW_cast3D", 1699135484, 1.0, -4),
    "league_talon_sfx_vo_e": ("Play_vo_Talon_Spell3DECast", 783303150, 0.5, -4),
    "league_talon_sfx_vo_r": ("Play_vo_Talon_TalonR_cast3D", 1184073097, 1.0, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_talon_skill": "ASSETS/Characters/Talon/HUD/Icons2D/TalonW.dds",
    "league_talon_skill2": "ASSETS/Characters/Talon/HUD/Icons2D/TalonQ.dds",
    "league_talon_ult": "ASSETS/Characters/Talon/HUD/Icons2D/TalonR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Talon.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Talon.{args.lang}.wad.client"))
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
