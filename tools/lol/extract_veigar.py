"""Pull Veigar's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_veigar.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Veigar.wad.client and Veigar.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without
--vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

His spells in the base bins: VeigarBalefulStrike = Q (VeigarBalefulStrike_OnCast, the bolt
VeigarBalefulStrikeMis_OnMissileLaunch / _OnHit), VeigarDarkMatter = W (_OnCast as it starts to fall, _hit),
VeigarEventHorizon = E (_OnCast, _buffactivate on a stunned unit, _loop while the cage stands), VeigarR =
Primordial Burst (_OnCast, _OnMissileLaunch, _OnHit) and the basic attack (VeigarBasicAttack_*). The base
skin's voice bank has no spell lines, only Attack2DGeneral, Death3D, Joke3DGeneral, Kill3DR / Laugh3DGeneral
(the same six laughs), Move2DStandard and Taunt3DGeneral: E takes the shortest zh_CN attack line (1.7 s) and R
his laugh (1.5 s). Q's powerup event (a stack gained) has no media in the base skin.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/veigar/skins/base/veigar_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/veigar/skins/base/veigar_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_veigar_sfx_attack_shot": ("Play_sfx_Veigar_VeigarBasicAttack_OnMissileLaunch", 19349797, 0.6, -8),
    "league_veigar_sfx_attack_hit": ("Play_sfx_Veigar_VeigarBasicAttack_OnHit", 23359294, 0.5, -8),
    "league_veigar_sfx_q_cast": ("Play_sfx_Veigar_VeigarBalefulStrike_OnCast", 302668892, 0.8, -6),
    "league_veigar_sfx_q_launch": ("Play_sfx_Veigar_VeigarBalefulStrikeMis_OnMissileLaunch", 975455126, 0.8, -7),
    "league_veigar_sfx_q_hit": ("Play_sfx_Veigar_VeigarBalefulStrikeMis_OnHit", 239843725, 0.8, -7),
    "league_veigar_sfx_w_cast": ("Play_sfx_Veigar_VeigarDarkMatter_OnCast", 912236945, 1.2, -6),
    "league_veigar_sfx_w_hit": ("Play_sfx_Veigar_VeigarDarkMatter_hit", 594660187, 1.2, -4),
    "league_veigar_sfx_e_cast": ("Play_sfx_Veigar_VeigarEventHorizon_OnCast", 482149243, 1.2, -5),
    "league_veigar_sfx_e_loop": ("Play_sfx_Veigar_VeigarEventHorizon_loop", 793797834, 3.0, -9),
    "league_veigar_sfx_e_stun": ("Play_sfx_Veigar_VeigarEventHorizon_buffactivate", 504841607, 1.0, -6),
    "league_veigar_sfx_r_cast": ("Play_sfx_Veigar_VeigarR_OnCast", 848154997, 0.8, -5),
    "league_veigar_sfx_r_launch": ("Play_sfx_Veigar_VeigarR_OnMissileLaunch", 673008509, 1.2, -6),
    "league_veigar_sfx_r_hit": ("Play_sfx_Veigar_VeigarR_OnHit", 589703976, 1.5, -4),
    "league_veigar_vo_e": ("Play_vo_Veigar_Attack2DGeneral", 1977573622, 1.8, -2),
    "league_veigar_vo_r": ("Play_vo_Veigar_Laugh3DGeneral", 828624673, 1.6, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Dark Matter rides on Event Horizon, Phenomenal Evil Power on every spell)
    "league_veigar_skill": "ASSETS/Characters/Veigar/HUD/Icons2D/VeigarBalefulStrike.dds",
    "league_veigar_skill2": "ASSETS/Characters/Veigar/HUD/Icons2D/VeigarEventHorizon.dds",
    "league_veigar_ult": "ASSETS/Characters/Veigar/HUD/Icons2D/VeigarPrimordialBurst.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Veigar.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Veigar.{args.lang}.wad.client"))
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
            print(f"{name:32s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:32s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
