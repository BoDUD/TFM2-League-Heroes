r"""Pull Udyr's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_udyr.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

The Volibear route (extract_volibear.py, extract_naafiri.py): reads (never writes) Game/DATA/FINAL/Champions/Udyr.wad.client
and Udyr.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Udyr_, the event names his skin bins name): each stance has its cast
(UdyrQ_stance_cast, ..._awakened), its two attack swings and hits (UdyrQAttack1_OnCast / _OnHit ...); the bear's
lightning bounces (UdyrQBounceMis_hit_*), the ram's stunning blow (UdyrEAttack_*), the phoenix's storm
(UdyrR_storm_buffactivate, _awakened, UdyrR_storm_hit). Voice (Play_vo_Udyr_): Spell3DQ1Cast, Spell3DE1Cast, Spell3DR1Cast.
Icons: Udyr_Q = skill (Wilding Claw), _E = skill2 (Blazing Stampede), _R = ult (Wingborne Storm), _W = the passive's Iron
Mantle (league_udyr_mantle), _P = the passive (league_udyr_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/udyr/skins/base/udyr_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/udyr/skins/base/udyr_base_vo_"  # same in every language
P = "Play_sfx_Udyr_"
V = "Play_vo_Udyr_"
C = "league_udyr_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "UdyrBasicAttack_OnCast"], None, 0.6, -14),
    C + "a_q": ([P + "UdyrQAttack1_OnCast"], None, 0.6, -14),
    C + "a_e": ([P + "UdyrEAttack_OnCast", P + "UdyrBasicAttack2_OnCast"], None, 0.6, -14),
    C + "a_r": ([P + "UdyrRAttack1_OnCast"], None, 0.6, -14),
    C + "a_hit": ([P + "UdyrBasicAttack_OnHit"], None, 0.8, -15),
    C + "q": ([P + "UdyrQ_stance_cast"], None, 1.2, -13),
    C + "q_wake": ([P + "UdyrQ_stance_cast_awakened"], None, 1.5, -12),
    C + "q_hit": ([P + "UdyrQAttack1_OnHit"], None, 0.8, -14),
    C + "q_bolt": ([P + "UdyrQBounceMis_hit_small"], None, 0.6, -15),
    C + "q_bolt_hit": ([P + "UdyrQBounceMis_hit_large"], None, 1.0, -12),
    C + "e": ([P + "UdyrE_stance_cast"], None, 1.2, -13),
    C + "e_wake": ([P + "UdyrE_stance_cast_awakened"], None, 1.5, -12),
    C + "e_dash": ([P + "UdyrEActivation_OnBuffActivate"], None, 1.0, -14),
    C + "e_hit_swing": ([P + "UdyrEAttack_OnCast"], None, 0.6, -13),
    C + "e_hit": ([P + "UdyrEAttack_OnHit"], None, 1.0, -12),
    C + "r": ([P + "UdyrR_stance_cast"], None, 1.2, -13),
    C + "r_pulse": ([P + "UdyrR_storm_buffactivate"], None, 0.6, -16),
    C + "r_rel": ([P + "UdyrR_storm_buffactivate_awakened"], None, 1.2, -12),
    C + "r_hit": ([P + "UdyrR_storm_hit"], None, 0.6, -16),
    C + "r_rel_hit": ([P + "UdyrRAttack1_OnHit", P + "UdyrR_storm_hit"], None, 1.0, -12),
    C + "w": ([P + "UdyrW_stance_cast"], None, 1.2, -13),
    C + "vo_q": ([V + "Spell3DQ1Cast"], None, 2.5, -6),
    C + "vo_e": ([V + "Spell3DE1Cast"], None, 2.5, -6),
    C + "vo_r": ([V + "Spell3DR1Cast"], None, 3.0, -6),
}
I = "assets/characters/udyr/hud/icons2d/udyr_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_udyr_skill": I + "q.dds",
    "league_udyr_skill2": I + "e.dds",
    "league_udyr_ult": I + "r.dds",
    "league_udyr_mantle": I + "w.dds",
    "league_udyr_passive": I + "p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Udyr.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Udyr.{args.lang}.wad.client"))
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
