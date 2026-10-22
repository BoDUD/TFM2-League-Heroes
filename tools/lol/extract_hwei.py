r"""Pull Hwei's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_hwei.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Qiyana route (extract_qiyana.py): reads (never writes) Game/DATA/FINAL/Champions/Hwei.wad.client and
Hwei.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event unless
a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Hwei_, the event names his skin bins name): the attack's cast and hit; the
signature's burst (HweiP_explosion); Subject: Disaster's three - Devastating Fire (QQ cast, explosion), Severing Bolt (QW
cast, the AoE's explosion), Molten Fissure (QE cast, the lava's eruption: its first variant on the spot, its second on
each unit); Subject: Torment's three (EQ / EW / EE casts, EQ's hit on the unit); Serenity's shield (WW cast) on every
Torment cast; Spiraling Despair's cast, its hit, the canvas growing and shattering. Voice (Play_vo_Hwei_): HweiQQ_cast3D,
HweiEQ_cast3D, HweiR_cast3D.
Icons: HweiQ = skill (Subject: Disaster), HweiE = skill2 (Subject: Torment), HweiR = ult (Spiraling Despair), HweiW =
Serenity (league_hwei_w), HweiPassive = the signature (league_hwei_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/hwei/skins/base/hwei_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/hwei/skins/base/hwei_base_vo_"  # same in every language
P = "Play_sfx_Hwei_Hwei"
V = "Play_vo_Hwei_Hwei"
C = "league_hwei_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS); the sfx at the level Orianna's, Zoe's, K'Sante's and Qiyana's got, the voice as the others'
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast", P + "BasicAttack_OnMissileLaunch"], None, 0.6, -8),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -7),
    C + "p_burst": ([P + "P_explosion_buffactivate", P + "P_explosion_buffactivate2"], None, 1.2, -5),
    C + "q_q": ([P + "QQ_OnCast", P + "QQ_OnMissileLaunch"], None, 1.0, -6),
    C + "q_q_hit": ([P + "QQ_explosion"], None, 1.2, -5),
    C + "q_w": ([P + "QW_OnCast"], None, 1.0, -6),
    C + "q_w_hit": ([P + "QW_AoE_explode", P + "QW_aoe_explode"], None, 1.5, -4),
    C + "q_e": ([P + "QE_OnCast"], None, 1.0, -6),
    C + "q_e_hit": ([P + "QE_lava_explode"], None, 1.5, -5),
    C + "q_e_burn": ([P + "QE_lava_explode"], 1, 0.8, -9),
    C + "e_q": ([P + "EQ_OnCast", P + "EQ_OnMissileLaunch"], None, 1.0, -6),
    C + "e_w": ([P + "EW_OnCast", P + "EW_OnMissileLaunch"], None, 1.0, -6),
    C + "e_e": ([P + "EE_OnCast"], None, 1.0, -6),
    C + "e_hit": ([P + "EQ_OnHit", P + "EW_hit", P + "EE_hit"], None, 1.0, -6),
    C + "w_ww": ([P + "WW_OnCast", P + "WWShield_OnBuffActivate"], None, 1.0, -8),
    C + "r": ([P + "R_OnCast", P + "R_OnMissileLaunch"], None, 1.5, -5),
    C + "r_canvas": ([P + "R_AoE_grow_buffactivate", P + "R_aoe_grow_buffactivate"], None, 2.5, -6),
    C + "r_burst": ([P + "R_AoE_shatter_buffactivate", P + "R_aoe_shatter_buffactivate"], None, 1.8, -4),
    C + "r_hit": ([P + "R_OnHit"], None, 1.2, -5),
    C + "vo_q": ([V + "QQ_cast3D", V + "QE_cast3D"], None, 2.5, -6),
    C + "vo_e": ([V + "EQ_cast3D", V + "EE_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "R_cast3D"], None, 3.0, -6),
}
I = "assets/characters/hwei/hud/icons2d/hwei"
ICONS = {  # TFM2 slot -> Riot icon
    "league_hwei_skill": I + "q.dds",
    "league_hwei_skill2": I + "e.dds",
    "league_hwei_ult": I + "r.dds",
    "league_hwei_w": I + "w.dds",
    "league_hwei_passive": I + "passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Hwei.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Hwei.{args.lang}.wad.client"))
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
