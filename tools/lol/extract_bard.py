r"""Pull Bard's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_bard.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_nidalee.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Bard.wad.client and Bard.<lang>.wad.client, resolves the base-skin Wwise events below to their
media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games)
plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.

His events (named in bard.bin / skin0.bin, the biggest or clearest variant of each): the attack BardBasicAttack_OnCast /
_OnHit; the Meeps meep_mis / meep_hit; Cosmic Binding's BardQMissile_OnMissileLaunch / _OnHit and BardQShackleDebuff (the
stun); the shrine BardWHealthPack_OnCast and BardWActualHealing (the heal); the door BardE_OnCast and
BardECreateDoor_exitappear; Tempered Fate BardR_OnCast, BardR_explo (landing) and BardR_statisfull_hit (a unit frozen).
Bard has no spoken lines - his "voice" is the melody his spells play (BardQ_OnCast's chime phrases, the shrine's
BardWHealthPack_cast3D tune).
Icons: Bard_Q = skill, Bard_W = skill2 (W + E), Bard_R = ult; Bard_E and the passive are written too (README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/bard/skins/base/bard_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/bard/skins/base/bard_base_vo_"  # same in every language
P = "Play_sfx_Bard_"
V = "Play_vo_Bard_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_bard_sfx_a_cast": (P + "BardBasicAttack_OnCast", 59629442, 0.6, -13),
    "league_bard_sfx_a_hit": (P + "BardBasicAttack_OnHit", 82431280, 0.5, -13),
    "league_bard_sfx_p_meep": (P + "meep_mis", 520639708, 0.5, -12),
    "league_bard_sfx_p_hit": (P + "meep_hit", 805843009, 0.6, -12),
    "league_bard_sfx_q_cast": (P + "BardQMissile_OnMissileLaunch", 126889257, 0.8, -10),
    "league_bard_sfx_q_hit": (P + "BardQMissile_OnHit", 390943040, 0.6, -10),
    "league_bard_sfx_q_bind": (P + "BardQShackleDebuff_buffactivate", 116361909, 0.9, -9),
    "league_bard_sfx_w_cast": (P + "BardWHealthPack_OnCast", 408369556, 0.6, -11),
    "league_bard_sfx_w_heal": (P + "BardWActualHealing_OnBuffActivate", 587016024, 0.9, -11),
    "league_bard_sfx_e_cast": (P + "BardE_OnCast", 311951408, 0.9, -10),
    "league_bard_sfx_e_out": (P + "BardECreateDoor_exitappear", 757884944, 0.7, -10),
    "league_bard_sfx_r_cast": (P + "BardR_OnCast", 413828850, 1.0, -9),
    "league_bard_sfx_r_land": (P + "BardR_explo", 219608814, 1.2, -8),
    "league_bard_sfx_r_lock": (P + "BardR_statisfull_hit", 15148679, 1.0, -11),
    "league_bard_sfx_vo_q": (P + "BardQ_OnCast", 536637702, 1.6, -6),
    "league_bard_sfx_vo_w": (V + "BardWHealthPack_cast3D", 680285372, 1.6, -6),
    "league_bard_sfx_vo_e": (P + "BardQ_OnCast", 1024659989, 1.6, -6),
    "league_bard_sfx_vo_r": (P + "BardQ_OnCast", 574073119, 1.8, -6),
}
I = "ASSETS/Characters/Bard/HUD/Icons2D/Bard_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_bard_skill": I + "Q.dds",
    "league_bard_skill2": I + "W.dds",
    "league_bard_ult": I + "R.dds",
    "league_bard_e": I + "E.dds",
    "league_bard_passive": I + "Passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Bard.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Bard.{args.lang}.wad.client"))
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
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
