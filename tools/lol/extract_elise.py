r"""Pull Elise's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_elise.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_jayce.py (extract_garen.py's decode/finish helpers): reads (never writes)
Game/DATA/FINAL/Champions/Elise.wad.client and Elise.<lang>.wad.client, resolves the base-skin Wwise events below to
their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice: zh_CN.

Her events (named in skin0.bin, listed with %TEMP%/el_work/sndprobe.py): the human spit EliseBasicAttack_OnMissileLaunch
/ _OnHit; the spider bite EliseSpiderBasicAttack_OnCast / _OnHit; a spiderling's bite EliseSpiderlingBasicAttack_hit;
Neurotoxin EliseHumanQ_OnCast / _OnHit; Volatile Spiderling EliseHumanW_OnCast and its blast EliseHumanWBoom_buffdeactivate;
Cocoon EliseHumanE_OnCast / _hit; Venomous Bite EliseSpiderQCast_OnCast / _OnHit; Skittering Frenzy EliseSpiderW_OnCast;
Rappel EliseSpiderE_OnCast (rise), _descent, _land and _buffactivate (the ult's call); the turns EliseR_OnCast (to the
spider) and EliseRSpider_OnCast (to the human). Voice: EliseHumanQ / W / E_cast3D and EliseRSpider_cast3D; the spider's
spells have no voice event of their own, so they take lines of Attack2DGeneral. Clip names differ from the sound names
(league_elise_sfx_*, memory vo-clip-names).
Icons: EliseHumanQ (Neurotoxin, the default form's Q) = skill, EliseHumanE (Cocoon, skill2's first spell) = skill2,
EliseR (Spider Form, the ult turns her) = ult; the human W, the spider's Q / W / E and the passive are written too
(league_elise_w / _cq / _cw / _ce / _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/elise/skins/base/elise_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/elise/skins/base/elise_base_vo_"  # same in every language
P = "Play_sfx_Elise_Elise"
V = "Play_vo_Elise_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_elise_sfx_a_spit": (P + "BasicAttack_OnMissileLaunch", 275003804, 0.6, -13),
    "league_elise_sfx_a_hit": (P + "BasicAttack_OnHit", 300925865, 0.6, -13),
    "league_elise_sfx_c_swing": (P + "SpiderBasicAttack_OnCast", 72237943, 0.5, -13),
    "league_elise_sfx_c_hit": (P + "SpiderBasicAttack_OnHit", 110570079, 0.7, -12),
    "league_elise_sfx_sl_bite": (P + "SpiderlingBasicAttack_hit", 303755331, 0.6, -15),
    "league_elise_sfx_q": (P + "HumanQ_OnCast", 629141348, 0.8, -12),
    "league_elise_sfx_q_hit": (P + "HumanQ_OnHit", 219375792, 1.0, -11),
    "league_elise_sfx_w": (P + "HumanW_OnCast", 715782150, 0.8, -12),
    "league_elise_sfx_w_boom": (P + "HumanWBoom_buffdeactivate", 962137005, 1.4, -10),
    "league_elise_sfx_e": (P + "HumanE_OnCast", 396780579, 0.8, -12),
    "league_elise_sfx_e_hit": (P + "HumanE_hit", 566309000, 1.4, -10),
    "league_elise_sfx_cq": (P + "SpiderQCast_OnCast", 19463831, 0.7, -12),
    "league_elise_sfx_cq_hit": (P + "SpiderQCast_OnHit", 287917389, 0.8, -11),
    "league_elise_sfx_cw": (P + "SpiderW_OnCast", 558484513, 1.2, -11),
    "league_elise_sfx_ce": (P + "SpiderE_OnCast", 892701175, 1.2, -11),
    "league_elise_sfx_ce_hit": (P + "SpiderE_descent", 641891108, 1.0, -11),
    "league_elise_sfx_ce_land": (P + "SpiderE_land", 439717968, 1.4, -10),
    "league_elise_sfx_r": (P + "SpiderE_buffactivate", 532680758, 1.6, -11),
    "league_elise_sfx_tf_spider": (P + "R_OnCast", 1055077248, 2.0, -10),
    "league_elise_sfx_tf_human": (P + "RSpider_OnCast", 132265407, 2.0, -10),
    "league_elise_sfx_vo_q": (V + "EliseHumanQ_cast3D", 146620732, 1.6, -6),
    "league_elise_sfx_vo_w": (V + "EliseHumanW_cast3D", 2008482315, 1.6, -6),
    "league_elise_sfx_vo_e": (V + "EliseHumanE_cast3D", 813852267, 1.6, -6),
    "league_elise_sfx_vo_human": (V + "EliseRSpider_cast3D", 2133883092, 2.0, -6),
    "league_elise_sfx_vo_spider": (V + "Attack2DGeneral", 1793980820, 2.4, -6),
    "league_elise_sfx_vo_cq": (V + "Attack2DGeneral", 200989633, 2.4, -6),
    "league_elise_sfx_vo_cw": (V + "Attack2DGeneral", 796328770, 2.4, -6),
    "league_elise_sfx_vo_ce": (V + "Attack2DGeneral", 1299175032, 2.4, -6),
    "league_elise_sfx_vo_r": (V + "Attack2DGeneral", 631023340, 2.4, -6),
}
I = "ASSETS/Characters/Elise/HUD/Icons2D/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_elise_skill": I + "EliseHumanQ.dds",
    "league_elise_skill2": I + "EliseHumanE.dds",
    "league_elise_ult": I + "EliseR.dds",
    "league_elise_w": I + "EliseHumanW.dds",
    "league_elise_cq": I + "EliseSpiderQ.dds",
    "league_elise_cw": I + "EliseSpiderW.dds",
    "league_elise_ce": I + "EliseSpiderE.dds",
    "league_elise_passive": I + "ElisePassive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Elise.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Elise.{args.lang}.wad.client"))
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
