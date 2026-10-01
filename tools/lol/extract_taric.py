"""Pull Taric's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_taric.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe [--list]

Same route as extract_nami.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Taric.wad.client and Taric.<lang>.wad.client, resolves the base-skin Wwise events below
to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written; --list
prints every variant of the events with its length instead. Voice language: zh_CN (Tencent client) by default.

His spells in the base bins: TaricE = Dazzle (E_cast the cast, E_missilelaunch the beam forming, E_hit a unit it
stuns), TaricQ = Starlight's Touch (Q_OnCast, Q_heal1/2/3 by the stacks spent), TaricR = Cosmic Radiance (R_OnCast,
one long clip from the call to the light landing), the Bravado attacks (TaricPassiveAttack_OnCast / _OnHit). W
(Bastion) has no sound of its own in the base bank (its missile's event is empty), so the bind plays the W voice
and the first Q heal chime. The basic attack's cast sound is `league_taric_attack`, which the engine plays by
itself at every attack (text-audio.md).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/taric/skins/base/taric_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/taric/skins/base/taric_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_taric_sfx_attack": ("Play_sfx_Taric_TaricBasicAttack_OnCast", 552110327, 0.7, -8),
    "league_taric_sfx_attack_hit": ("Play_sfx_Taric_TaricBasicAttack_OnHit", 50330666, 0.9, -7),
    "league_taric_sfx_p_cast": ("Play_sfx_Taric_TaricPassiveAttack_OnCast", 492088543, 0.8, -7),
    "league_taric_sfx_p_hit": ("Play_sfx_Taric_TaricPassiveAttack_OnHit", 920707422, 1.0, -6),
    "league_taric_sfx_e_cast": ("Play_sfx_Taric_TaricE_cast", 852192195, 1.2, -6),
    "league_taric_sfx_e_beam": ("Play_sfx_Taric_TaricE_missilelaunch", 446844198, 1.5, -6),
    "league_taric_sfx_e_hit": ("Play_sfx_Taric_TaricE_hit", 271722324, 1.2, -5),
    "league_taric_sfx_q_cast": ("Play_sfx_Taric_TaricQ_OnCast", 662402347, 1.5, -6),
    "league_taric_sfx_q_heal1": ("Play_sfx_Taric_TaricQ_heal1", 382356432, 1.5, -7),
    "league_taric_sfx_q_heal2": ("Play_sfx_Taric_TaricQ_heal2", 921544932, 1.5, -7),
    "league_taric_sfx_q_heal3": ("Play_sfx_Taric_TaricQ_heal3", 547039402, 1.5, -7),
    "league_taric_sfx_r_cast": ("Play_sfx_Taric_TaricR_OnCast", 972024357, 5.5, -4),
    "league_taric_vo_q": ("Play_vo_Taric_TaricQ_cast3D", 2088239057, 1.2, -2),
    "league_taric_vo_w": ("Play_vo_Taric_TaricW_cast3D", 1064392505, 1.4, -2),
    "league_taric_vo_e": ("Play_vo_Taric_TaricE_cast3D", 1226497603, 1.4, -2),
    "league_taric_vo_r": ("Play_vo_Taric_TaricR_cast3D", 835370212, 2.4, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Bastion rides on Starlight's Touch, Bravado on every spell)
    "league_taric_skill": "ASSETS/Characters/Taric/HUD/Icons2D/Taric_E.dds",
    "league_taric_skill2": "ASSETS/Characters/Taric/HUD/Icons2D/Taric_Q.dds",
    "league_taric_ult": "ASSETS/Characters/Taric/HUD/Icons2D/Taric_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    ap.add_argument("--list", action="store_true", help="print each event's variants and their length, write nothing")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Taric.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Taric.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (event, mid, max_s, peak) in CLIPS.items():
            variants = banks.event_media(event)
            if args.list:
                lens = []
                for v in variants:
                    sr, x = decode(media[v], args.vgmstream)
                    lens.append(f"{v}:{len(x) / sr:.2f}s")
                print(f"{name:28s} {event}: {' '.join(lens)}")
                continue
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
        if args.list:
            return

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:32s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
