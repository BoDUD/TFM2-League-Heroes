r"""Pull Olaf's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_olaf.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

Same route as extract_zed.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Olaf.wad.client and Olaf.<lang>.wad.client, resolves the base-skin Wwise events below to their
media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games)
plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice language: zh_CN.

His events (found in his bins by work/ol/snd_names_ol.py, picked with work/ol/snd_probe_ol.py): the swing
OlafBasicAttack_OnCast / _OnHit; Undertow OlafQ_OnMissileLaunch (the throw), OlafQ_hit, OlafQ_land (the axe sticks),
OlafQ_grab (picked up); Tough It Out OlafW_OnCast; Reckless Swing OlafE_OnCast and OlafE_OnHit; Ragnarok OlafR_OnCast.
Voice: AxeThrowCast (Q), FrenziedStrikes (W), RecklessStrike (E), Ragnarok (R).
Icons: OlafQ = skill (Undertow), OlafE = skill2 (Reckless Swing), OlafR = ult (Tough It Out is automatic).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/olaf/skins/base/olaf_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/olaf/skins/base/olaf_base_vo_"  # same in every language
P = "Play_sfx_Olaf_Olaf"
V = "Play_vo_Olaf_Olaf"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_olaf_sfx_attack": (P + "BasicAttack_OnCast", 19270190, 0.4, -11),
    "league_olaf_sfx_attack_hit": (P + "BasicAttack_OnHit", 16480700, 0.4, -11),
    "league_olaf_sfx_q": (P + "Q_OnMissileLaunch", 369108734, 0.6, -9),
    "league_olaf_sfx_q_hit": (P + "Q_hit", 206631901, 0.4, -10),
    "league_olaf_sfx_q_land": (P + "Q_land", 1038314831, 0.4, -10),
    "league_olaf_sfx_q_pick": (P + "Q_grab", 248418304, 0.4, -9),
    "league_olaf_sfx_w": (P + "W_OnCast", 588130155, 0.9, -9),
    "league_olaf_sfx_e": (P + "E_OnCast", 229082654, 0.4, -9),
    "league_olaf_sfx_e_hit": (P + "E_OnHit", 429152417, 0.8, -8),
    "league_olaf_sfx_r": (P + "R_OnCast", 799808365, 1.3, -8),
    "league_olaf_sfx_vo_q": (V + "AxeThrowCast_cast3D", 1358618860, 0.8, -4),
    "league_olaf_sfx_vo_w": (V + "FrenziedStrikes_cast3D", 1747513883, 1.4, -4),
    "league_olaf_sfx_vo_e": (V + "RecklessStrike_cast3D", 862807654, 1.0, -4),
    "league_olaf_sfx_vo_r": (V + "Ragnarok_cast3D", 887013514, 1.6, -3),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_olaf_skill": "assets/characters/olaf/hud/icons2d/olafq.dds",
    "league_olaf_skill2": "assets/characters/olaf/hud/icons2d/olafe.dds",
    "league_olaf_ult": "assets/characters/olaf/hud/icons2d/olafr.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Olaf.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Olaf.{args.lang}.wad.client"))
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
