"""Pull Vladimir's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_vladimir.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_xayah.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Vladimir.wad.client and Vladimir.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events (the client's names, found in his bins by work/vl/snd_names_vl.py and picked with work/vl/snd_probe_vl.py):
the attack is VladimirBasicAttack_OnMissileLaunch + _OnHit; Transfusion VladimirQ_OnCast + _OnHit, the blood reaching
him VladimirTransfusionHeal_OnHit, Crimson Rush's hit VladimirQFrenzy_start; Tides of Blood's charge VladimirE_OnBuffActivate,
the nova VladimirE_charged_onmissilelaunch, a bolt's hit VladimirE_charged_hit; the pool VladimirSanguinePool_OnCast and
_OnBuffDeactivate (also the combo's mist blink); Hemoplague VladimirHemoplague_OnCast, the cloud
VladimirHemoplagueDebuff_buffactivate, the burst VladimirHemoplague_hit. Voice: a Q, an E, an R and the pool's end line.
Icons: VladimirQ = skill, VladimirE = skill2, VladimirR = ult (W, the automatic pool, has no slot).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/vladimir/skins/base/vladimir_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/vladimir/skins/base/vladimir_base_vo_"  # same in every language
P = "Play_sfx_Vladimir_Vladimir"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_vladimir_sfx_attack": (P + "BasicAttack_OnMissileLaunch", 448112524, 0.5, -11),
    "league_vladimir_sfx_attack_hit": (P + "BasicAttack_OnHit", 41679235, 0.3, -12),
    "league_vladimir_sfx_q": (P + "Q_OnCast", 728495261, 0.4, -9),
    "league_vladimir_sfx_q_hit": (P + "Q_OnHit", 133649384, 0.7, -9),
    "league_vladimir_sfx_q_heal": (P + "TransfusionHeal_OnHit", 48071176, 1.1, -11),
    "league_vladimir_sfx_q_rush": (P + "QFrenzy_start", 954663749, 1.0, -8),
    "league_vladimir_sfx_e_charge": (P + "E_OnBuffActivate", 305879041, 1.1, -10),
    "league_vladimir_sfx_e": (P + "E_charged_onmissilelaunch", 495572975, 1.0, -8),
    "league_vladimir_sfx_e_hit": (P + "E_charged_hit", 388518403, 0.5, -13),
    "league_vladimir_sfx_w": (P + "SanguinePool_OnCast", 718995861, 0.8, -8),
    "league_vladimir_sfx_w_out": (P + "SanguinePool_OnBuffDeactivate", 131875393, 0.45, -9),
    "league_vladimir_sfx_blink": (P + "SanguinePool_OnBuffDeactivate", 988953811, 0.35, -10),
    "league_vladimir_sfx_r": (P + "Hemoplague_OnCast", 289936887, 0.5, -8),
    "league_vladimir_sfx_r_land": (P + "HemoplagueDebuff_buffactivate", 365565477, 0.65, -9),
    "league_vladimir_sfx_r_burst": (P + "Hemoplague_hit", 834435702, 1.2, -8),
    "league_vladimir_vo_q": ("Play_vo_Vladimir_VladimirQ_cast3D", 342794105, 1.6, -4),
    "league_vladimir_vo_e": ("Play_vo_Vladimir_VladimirE_cast3D", 254966897, 0.9, -4),
    "league_vladimir_vo_r": ("Play_vo_Vladimir_VladimirHemoplague_cast3D", 615529766, 1.5, -3),
    "league_vladimir_vo_w": ("Play_vo_Vladimir_Spell3DWEnd", 441862918, 1.7, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_vladimir_skill": "ASSETS/Characters/Vladimir/HUD/Icons2D/VladimirQ.dds",
    "league_vladimir_skill2": "ASSETS/Characters/Vladimir/HUD/Icons2D/VladimirE.dds",
    "league_vladimir_ult": "ASSETS/Characters/Vladimir/HUD/Icons2D/VladimirR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Vladimir.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Vladimir.{args.lang}.wad.client"))
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
