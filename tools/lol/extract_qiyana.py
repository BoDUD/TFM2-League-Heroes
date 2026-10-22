r"""Pull Qiyana's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_qiyana.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Udyr route (extract_udyr.py): reads (never writes) Game/DATA/FINAL/Champions/Qiyana.wad.client and
Qiyana.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event unless
a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Qiyana_, the event names her skin bins name): the attack's swing and hit, the crit's
hit for Royal Privilege's first strike; Q's cast and hit, plain and by element (QiyanaQ_Water_* river, _Rock_* rock,
_Grass_* grass); W's enchant (QiyanaWMis_Rock_OnMissileCast); E's dash and hit; R's cast, its shockwave leaving
(QiyanaRmis_OnMissileCast) and striking (QiyanaRMis_OnHit). Voice (Play_vo_Qiyana_): QiyanaQ_cast3D, QiyanaE_cast3D,
QiyanaR_cast3D.
Icons: Qiyana_Q1 = skill (Edge of Ixtal), _E = skill2 (Audacity), _R = ult (Supreme Display of Talent), _W = Terrashape
(league_qiyana_w), _Passive = the passive (league_qiyana_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/qiyana/skins/base/qiyana_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/qiyana/skins/base/qiyana_base_vo_"  # same in every language
P = "Play_sfx_Qiyana_"
V = "Play_vo_Qiyana_"
C = "league_qiyana_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS); the sfx at the level Orianna's, Zoe's and K'Sante's got (2026-10-22: 8 dB over the old -11..-16
# peaks, 「佐伊的音效也照奥莉安娜的办法调响」), the voice as the other heroes'
CLIPS = {
    C + "a": ([P + "QiyanaBasicAttack_OnCast"], None, 0.6, -8),
    C + "a_hit": ([P + "QiyanaBasicAttack_OnHit"], None, 0.8, -7),
    C + "p_hit": ([P + "QiyanaCritAttack_OnHit"], None, 0.8, -5),
    C + "w_on": ([P + "QiyanaWMis_Rock_OnMissileCast", P + "QiyanaWMis_Water_OnMissileCast"], None, 1.0, -5),
    C + "q": ([P + "QiyanaQ_OnCast"], None, 1.0, -6),
    C + "q_w": ([P + "QiyanaQ_Water_OnCast"], None, 1.2, -5),
    C + "q_r": ([P + "QiyanaQ_Rock_OnCast"], None, 1.2, -5),
    C + "q_g": ([P + "QiyanaQ_Grass_OnCast"], None, 1.2, -5),
    C + "q_hit": ([P + "QiyanaQ_hit"], None, 0.8, -7),
    C + "q_w_hit": ([P + "QiyanaQ_Water_hit"], None, 1.0, -6),
    C + "q_r_hit": ([P + "QiyanaQ_Rock_hit"], None, 1.0, -6),
    C + "q_g_hit": ([P + "QiyanaQ_Grass_hit"], None, 1.0, -6),
    C + "e": ([P + "QiyanaE_OnCast"], None, 1.0, -6),
    C + "e_hit": ([P + "QiyanaE_hit"], None, 1.0, -5),
    C + "r": ([P + "QiyanaR_OnCast"], None, 1.5, -5),
    C + "r_burst": ([P + "QiyanaRmis_OnMissileCast"], None, 1.5, -4),
    C + "r_hit": ([P + "QiyanaRMis_OnHit", P + "QiyanaR_Rock_stun"], None, 1.2, -4),
    C + "vo_q": ([V + "QiyanaQ_cast3D"], None, 2.5, -6),
    C + "vo_e": ([V + "QiyanaE_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "QiyanaR_cast3D"], None, 3.0, -6),
}
I = "assets/characters/qiyana/hud/icons2d/qiyana_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_qiyana_skill": I + "q1.dds",
    "league_qiyana_skill2": I + "e.dds",
    "league_qiyana_ult": I + "r.dds",
    "league_qiyana_w": I + "w.dds",
    "league_qiyana_passive": I + "passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Qiyana.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Qiyana.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (events, mid, max_s, peak) in CLIPS.items():
            event, variants = None, []
            for ev in events:
                variants = banks.event_media(ev)
                if variants:
                    event = ev
                    break
            if not variants:
                sys.exit(f"{name}: none of {events} resolves - game patch changed the bank?")
            m = variants[0] if mid is None else variants[min(mid, len(variants) - 1)]
            sr, x = decode(media[m], args.vgmstream)
            pcm = finish(x, sr, max_s, peak)
            with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(pcm.tobytes())
            print(f"{name:40s} {len(pcm) / sr:4.2f}s  <- {event} ({len(variants)} variants)")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:40s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
