"""Pull Shaco's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_shaco.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Shaco.wad.client and Shaco.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events in the base bank: ShacoBasicAttack_OnCast / _OnHit (the stab), ShacoCritAttack_OnHit (the crit),
ShacoP_hit (Backstab), Deceive_OnCast (the vanish), TwoShivPoison_OnCast / _OnHit (the shiv),
JackInTheBox_OnCast / _BuffActivate (the box placed / springing open), ShacoBox_ShacoBoxSpell_OnMissileLaunch (a
box's shot), HallucinateFull_cast / _nova (the clone / its explosion); voice: ShacoCritAttack_cast3D (a backstab
line) and Laugh3DGeneral (his laugh). The icons: Jester_ManiacalCloak2 = Deceive, Jester_DeathWard = Jack In The
Box, Jester_HallucinogenBomb = Hallucinate (Jester_IncrediblyPrecise = Two-Shiv Poison and Jester_CarefulStrikes =
Backstab ride on the attack, which has no icon).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/shaco/skins/base/shaco_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/shaco/skins/base/shaco_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_shaco_sfx_attack": ("Play_sfx_Shaco_ShacoBasicAttack_OnCast", 15502583, 0.35, -10),
    "league_shaco_sfx_attack_hit": ("Play_sfx_Shaco_ShacoBasicAttack_OnHit", 435761436, 0.5, -9),
    "league_shaco_sfx_crit_hit": ("Play_sfx_Shaco_ShacoCritAttack_OnHit", 227599946, 0.7, -6),
    "league_shaco_sfx_bs_hit": ("Play_sfx_Shaco_ShacoP_hit", 510586559, 0.8, -7),
    "league_shaco_sfx_q_cast": ("Play_sfx_Shaco_Deceive_OnCast", 372280108, 1.0, -6),
    "league_shaco_sfx_e_throw": ("Play_sfx_Shaco_TwoShivPoison_OnCast", 403436983, 0.6, -8),
    "league_shaco_sfx_e_hit": ("Play_sfx_Shaco_TwoShivPoison_OnHit", 173956393, 0.6, -8),
    "league_shaco_sfx_w_cast": ("Play_sfx_Shaco_JackInTheBox_OnCast", 853466400, 0.9, -7),
    "league_shaco_sfx_w_pop": ("Play_sfx_Shaco_JackInTheBox_BuffActivate", 691698175, 1.8, -5),
    "league_shaco_sfx_w_shot": ("Play_sfx_ShacoBox_ShacoBoxSpell_OnMissileLaunch", 304116173, 0.5, -10),
    "league_shaco_sfx_r_cast": ("Play_sfx_Shaco_HallucinateFull_cast", 445424315, 1.5, -6),
    "league_shaco_sfx_r_boom": ("Play_sfx_Shaco_HallucinateFull_nova", 624821430, 1.6, -4),
    "league_shaco_vo_q_hit": ("Play_vo_Shaco_ShacoCritAttack_cast3D", 1329463451, 1.2, -2),
    "league_shaco_vo_r": ("Play_vo_Shaco_Laugh3DGeneral", 565203306, 2.5, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_shaco_skill": "ASSETS/Characters/Shaco/HUD/Icons2D/Jester_ManiacalCloak2.dds",
    "league_shaco_skill2": "ASSETS/Characters/Shaco/HUD/Icons2D/Jester_DeathWard.dds",
    "league_shaco_ult": "ASSETS/Characters/Shaco/HUD/Icons2D/Jester_HallucinogenBomb.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Shaco.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Shaco.{args.lang}.wad.client"))
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
