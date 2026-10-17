"""Pull Kayle's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_kayle.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Kayle.wad.client and Kayle.<lang>.wad.client, resolves the base-skin Wwise
events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without
--vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Her spells go by these names in the base bins: KayleBasicAttack (melee swing) / KayleBasicAttack3-4 (the
ranged star-fire bolt she throws from level 6 on), KayleEnrageConeMis = the fire wave of an Exalted attack
(Aflame, level 11), KayleEnrage = Exalted at five Zeal stacks, KayleQ / KayleQMis = Radiant Blast,
KayleWHeal = Celestial Blessing, KayleEAttack = Starfire Spellblade's empowered attack, KayleR = Divine
Judgment (blades_down as the swords fall), KaylePassiveCeremony1-3 = the three ascension ceremonies of
Divine Ascent (levels 6, 11 and 16 in League; 5, 8 and 12 in league_kayle). The voice bank holds four
passive-rank lines, Spell2DPRank1-4 for LevelForPassiveRank0-3 (levels 1, 6, 11, 16) going by their
numbering (not checked by ear): PRank2-4 go with the three ascensions. Every zh_CN line differs from the
en_US one; the shortest variant of each is taken, since TFM2 casts come quickly.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/kayle/skins/base/kayle_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/kayle/skins/base/kayle_base_vo_"  # same path in every language WAD

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_kayle_sfx_attack_hit": ("Play_sfx_Kayle_KayleBasicAttack_OnHit", 350815727, 0.7, -6),
    "league_kayle_sfx_attack_shot": ("Play_sfx_Kayle_KayleBasicAttack3_OnMissileCast", 818637153, 0.8, -7),
    "league_kayle_sfx_attack_ranged_hit": ("Play_sfx_Kayle_KayleBasicAttack3_OnHit", 286773117, 0.8, -6),
    "league_kayle_sfx_wave": ("Play_sfx_Kayle_KayleEnrageConeMis_OnMissileCast", 540660147, 0.9, -7),
    "league_kayle_sfx_exalted": ("Play_sfx_Kayle_KayleEnrage_buffactivate", 55720510, 1.5, -8),
    "league_kayle_sfx_q_cast": ("Play_sfx_Kayle_KayleQ_OnCast", 148057318, 1.2, -5),
    "league_kayle_sfx_q_fly": ("Play_sfx_Kayle_KayleQMis_OnMissileCast", 538052598, 1.0, -6),
    "league_kayle_sfx_q_hit": ("Play_sfx_Kayle_KayleQMis_OnHit", 188728287, 1.3, -5),
    "league_kayle_sfx_e_cast": ("Play_sfx_Kayle_KayleEAttack_OnMissileCast", 678524736, 1.0, -5),
    "league_kayle_sfx_e_hit": ("Play_sfx_Kayle_KayleEAttack_OnHit", 337742228, 1.2, -5),
    "league_kayle_sfx_w_heal": ("Play_sfx_Kayle_KayleWHeal_OnCast", 357813012, 1.6, -6),
    "league_kayle_sfx_r_cast": ("Play_sfx_Kayle_KayleR_OnCast", 667843458, 2.6, -4),
    "league_kayle_sfx_r_blades": ("Play_sfx_Kayle_KayleR_cast_blades_down", 673873780, 1.4, -4),
    "league_kayle_sfx_r_hit": ("Play_sfx_Kayle_KayleR_hit", 301686469, 2.0, -3),
    "league_kayle_sfx_ascend1": ("Play_sfx_Kayle_KaylePassiveCeremony1_cast", 544847462, 2.9, -5),
    "league_kayle_sfx_ascend2": ("Play_sfx_Kayle_KaylePassiveCeremony2_cast", 538164647, 3.0, -5),
    "league_kayle_sfx_ascend3": ("Play_sfx_Kayle_KaylePassiveCeremony3_cast", 671570586, 3.5, -5),
    "league_kayle_vo_q": ("Play_vo_Kayle_KayleQ_cast3D", 1115190410, 1.8, -2),
    "league_kayle_vo_w": ("Play_vo_Kayle_KayleW_hit3D", 1804332499, 2.4, -2),
    "league_kayle_vo_e": ("Play_vo_Kayle_KayleE_cast3D", 421668934, 2.0, -2),
    "league_kayle_vo_r": ("Play_vo_Kayle_KayleR_hit3D", 1707927164, 1.9, -2),
    "league_kayle_vo_ascend1": ("Play_vo_Kayle_Spell2DPRank2", 167125699, 4.8, -2),
    "league_kayle_vo_ascend2": ("Play_vo_Kayle_Spell2DPRank3", 194756270, 3.2, -2),
    "league_kayle_vo_ascend3": ("Play_vo_Kayle_Spell2DPRank4", 657633173, 3.9, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (Celestial Blessing rides on Starfire Spellblade, Divine Ascent is the attack)
    "league_kayle_skill": "ASSETS/Characters/Kayle/HUD/Icons2D/Kayle_Q.dds",
    "league_kayle_skill2": "ASSETS/Characters/Kayle/HUD/Icons2D/Kayle_E.dds",
    "league_kayle_ult": "ASSETS/Characters/Kayle/HUD/Icons2D/Kayle_R.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Kayle.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Kayle.{args.lang}.wad.client"))
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
