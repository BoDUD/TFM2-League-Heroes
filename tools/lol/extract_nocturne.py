"""Pull Nocturne's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_nocturne.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Nocturne.wad.client and Nocturne.<lang>.wad.client, resolves the base-skin Wwise events
below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events in the base bank: NocturneBasicAttack_OnCast / _OnHit (the blade strike), NocturneUmbraBladesAttack_OnCast /
_hit (the passive's cleave), NocturneDuskbringer_OnCast / _hit (Q), NocturneUnspeakableHorror_OnCast / _fear (E),
NocturneShroudofDarkness_OnCast and NocturneShroudofDarknessBuff_OnBuffActivate (W raised / W's attack speed), and
NocturneParanoia_OnCast, NocturneParanoiaDash_OnBuffActivate / _hit (R's darkness, the flight, the landing); voice:
NocturneDuskbringer_cast3D, NocturneUnspeakableHorror_cast3D, Spell3DWProc and NocturneParanoiaTargetChaosVO. The
icons: Nocturne_Duskbringer = Q, Nocturne_UnspeakableHorror = E (W rides on it), Nocturne_Paranoia = R
(Nocturne_UmbraBlades and Nocturne_ShroudOfDarkness are folded into the attack and E, which have no icon of their own).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/nocturne/skins/base/nocturne_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/nocturne/skins/base/nocturne_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_nocturne_sfx_attack": ("Play_sfx_Nocturne_NocturneBasicAttack_OnCast", 389421540, 0.55, -10),
    "league_nocturne_sfx_attack_hit": ("Play_sfx_Nocturne_NocturneBasicAttack_OnHit", 51822368, 0.4, -9),
    "league_nocturne_sfx_p_cast": ("Play_sfx_Nocturne_NocturneUmbraBladesAttack_OnCast", 104188284, 1.0, -7),
    "league_nocturne_sfx_p_hit": ("Play_sfx_Nocturne_NocturneUmbraBladesAttack_hit", 7569282, 0.6, -7),
    "league_nocturne_sfx_q_cast": ("Play_sfx_Nocturne_NocturneDuskbringer_OnCast", 298540178, 1.2, -6),
    "league_nocturne_sfx_q_hit": ("Play_sfx_Nocturne_NocturneDuskbringer_hit", 692187811, 0.8, -7),
    "league_nocturne_sfx_e_cast": ("Play_sfx_Nocturne_NocturneUnspeakableHorror_OnCast", 199361093, 1.35, -6),
    "league_nocturne_sfx_e_fear": ("Play_sfx_Nocturne_NocturneUnspeakableHorror_fear", 888142576, 1.45, -5),
    "league_nocturne_sfx_w_cast": ("Play_sfx_Nocturne_NocturneShroudofDarkness_OnCast", 866652499, 1.9, -6),
    "league_nocturne_sfx_w_proc": ("Play_sfx_Nocturne_NocturneShroudofDarknessBuff_OnBuffActivate", 144336875, 1.1, -6),
    "league_nocturne_sfx_r_cast": ("Play_sfx_Nocturne_NocturneParanoia_OnCast", 723869920, 1.5, -5),
    "league_nocturne_sfx_r_dash": ("Play_sfx_NocturneParanoiaDash_OnBuffActivate", 249611512, 1.2, -6),
    "league_nocturne_sfx_r_hit": ("Play_sfx_Nocturne_NocturneParanoiaDash_hit", 247784095, 1.1, -5),
    "league_nocturne_vo_q": ("Play_vo_Nocturne_NocturneDuskbringer_cast3D", 1151487222, 1.0, -2),
    "league_nocturne_vo_e": ("Play_vo_Nocturne_NocturneUnspeakableHorror_cast3D", 1517920667, 1.3, -2),
    "league_nocturne_vo_w": ("Play_vo_Nocturne_Spell3DWProc", 15557510, 2.2, -2),
    "league_nocturne_vo_r": ("Play_vo_Nocturne_NocturneParanoiaTargetChaosVO_OnBuffActivate", 476573893, 2.2, -2),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_nocturne_skill": "ASSETS/Characters/Nocturne/HUD/Icons2D/Nocturne_Duskbringer.dds",
    "league_nocturne_skill2": "ASSETS/Characters/Nocturne/HUD/Icons2D/Nocturne_UnspeakableHorror.dds",
    "league_nocturne_ult": "ASSETS/Characters/Nocturne/HUD/Icons2D/Nocturne_Paranoia.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Nocturne.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Nocturne.{args.lang}.wad.client"))
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
