"""Pull Morgana's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_morgana.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Morgana.wad.client and Morgana.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without
--vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Her spells in the base bins: MorganaQ = Dark Binding (OnCast the throw, OnHit the binding), MorganaW =
Tormented Shadow (W_cast, the pool's hiss), MorganaE = Black Shield (E_cast_others cast on an ally,
E_OnBuffActivate the shield forming), MorganaR = Soul Shackles (R_cast_self the chains flying out,
R_hit_others a champion chained, R_detonate the chains snapping into the stun). The basic attack's cast sound
is `league_morgana_attack`, which the engine plays by itself at every attack (text-audio.md). Every spell
voice line is translated in the zh_CN bank; one of the shorter variants is taken. Black Shield has no cast
line of its own (only a chat line when it lands on Kayle), and W's line would follow Q's by a few ticks
(W's pool rides on Q), so neither has one.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/morgana/skins/base/morgana_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/morgana/skins/base/morgana_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_morgana_sfx_attack": ("Play_sfx_Morgana_MorganaBasicAttack_OnCast", 981738760, 0.6, -7),
    "league_morgana_sfx_attack_hit": ("Play_sfx_Morgana_MorganaBasicAttack_OnHit", 865485901, 0.8, -6),
    "league_morgana_sfx_q_cast": ("Play_sfx_Morgana_MorganaQ_OnCast", 1068013637, 1.2, -5),
    "league_morgana_sfx_q_hit": ("Play_sfx_Morgana_MorganaQ_OnHit", 387836197, 1.6, -4),
    "league_morgana_sfx_w_cast": ("Play_sfx_Morgana_MorganaW_cast", 931864068, 3.0, -6),
    "league_morgana_sfx_e_cast": ("Play_sfx_Morgana_MorganaE_cast_others", 969810828, 1.2, -5),
    "league_morgana_sfx_e_shield": ("Play_sfx_Morgana_MorganaE_OnBuffActivate", 905946698, 1.6, -6),
    "league_morgana_sfx_r_cast": ("Play_sfx_Morgana_MorganaR_cast_self", 303111616, 2.0, -4),
    "league_morgana_sfx_r_hit": ("Play_sfx_Morgana_MorganaR_hit_others", 314270290, 1.4, -5),
    "league_morgana_sfx_r_snap": ("Play_sfx_Morgana_MorganaR_detonate", 55759941, 1.6, -4),
    "league_morgana_vo_q": ("Play_vo_Morgana_MorganaQ_cast3D", 1227051729, 1.4, -2),
    "league_morgana_vo_r": ("Play_vo_Morgana_MorganaR_cast3D", 134237569, 1.8, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Tormented Shadow rides on Dark Binding, Soul Siphon on every spell)
    "league_morgana_skill": "ASSETS/Characters/Morgana/HUD/Icons2D/FallenAngel_DarkBinding.dds",
    "league_morgana_skill2": "ASSETS/Characters/Morgana/HUD/Icons2D/FallenAngel_BlackShield.dds",
    "league_morgana_ult": "ASSETS/Characters/Morgana/HUD/Icons2D/FallenAngel_Purgatory.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Morgana.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Morgana.{args.lang}.wad.client"))
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
