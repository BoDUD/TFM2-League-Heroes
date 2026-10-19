r"""Pull Yuumi's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_yuumi.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as the Zoe extractor: reads (never writes) Game/DATA/FINAL/Champions/Yuumi.wad.client and
Yuumi.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event),
decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus
64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Events (prefix Play_sfx_Yuumi_, named in the champion's bins): YuumiBasicAttack_OnCast / OnHit, YuumiPAttack_OnHit7
(Feline Friendship), YuumiQ_OnCast / YuumiQ_hit_champion / _empowered (Prowling Projectile), YuumiW_cast_jump /
YuumiW_cast_start / YuumiW_end_jumpoff (You and Me!), YuumiE_cast (Zoomies), YuumiR_OnCast / YuumiRmissile_OnMissileCast
/ YuumiRmissile_OnHit (Final Chapter), YuumiPHealMis_OnMissileCast (the heals). Voice (Play_vo_Yuumi_): YuumiQCast_cast3D,
YuumiWCast_cast3DGeneral, YuumiR_cast3D.
Icons (the bins' mImgIconName): YuumiQ = skill, YuumiW = skill2, YuumiR = ult, YuumiP = passive (for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/yuumi/skins/base/yuumi_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/yuumi/skins/base/yuumi_base_vo_"  # same in every language
P = "Play_sfx_Yuumi_"
V = "Play_vo_Yuumi_"
C = "league_yuumi_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "YuumiBasicAttack_OnCast"], None, 0.8, -16),
    C + "a_hit": ([P + "YuumiBasicAttack_OnHit"], None, 0.8, -15),
    C + "p_hit": ([P + "YuumiPAttack_OnHit7", P + "YuumiPAttack_cast"], None, 1.0, -13),
    C + "q": ([P + "YuumiQ_OnCast", P + "YuumiQcast_OnCast"], None, 1.0, -14),
    C + "q_hit": ([P + "YuumiQ_hit_champion", P + "YuumiQ_hit_minion"], None, 1.2, -13),
    C + "q_ehit": ([P + "YuumiQ_hit_champion_empowered", P + "YuumiQ_hit_minion_empowered"], None, 1.4, -12),
    C + "w": ([P + "YuumiW_cast_jump", P + "YuumiW_cast_start"], None, 1.0, -14),
    C + "w_on": ([P + "YuumiW_cast_start", P + "YuumiW_cast_flip"], None, 1.0, -14),
    C + "w_off": ([P + "YuumiW_end_jumpoff"], None, 1.0, -14),
    C + "e_hit": ([P + "YuumiE_cast", P + "YuumiEShield_buffactivate"], None, 1.4, -13),
    C + "r": ([P + "YuumiR_OnCast"], None, 1.6, -13),
    C + "r_wave": ([P + "YuumiRmissile_OnMissileCast"], None, 1.2, -15),
    C + "r_hit": ([P + "YuumiRmissile_OnHit", P + "YuumiRmissile_hit1"], None, 1.0, -14),
    C + "r_heal": ([P + "YuumiPHealMis_OnMissileCast", P + "YuumiPHealMark_OnBuffDeactivate"], None, 1.0, -15),
    C + "vo_q": ([V + "YuumiQCast_cast3D"], None, 2.0, -6),
    C + "vo_w": ([V + "YuumiWCast_cast3DGeneral"], None, 2.0, -6),
    C + "vo_r": ([V + "YuumiR_cast3D"], None, 2.0, -6),
}
I = "assets/characters/yuumi/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_yuumi_skill": I + "yuumiq.dds",
    "league_yuumi_skill2": I + "yuumiw.dds",
    "league_yuumi_ult": I + "yuumir.dds",
    "league_yuumi_passive": I + "yuumip.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Yuumi.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Yuumi.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (events, mid, max_s, peak) in CLIPS.items():
            event, variants = None, []
            # (the bins' names can carry a glued character - "OnBuffActivate2", "OnCast0": also try them without it)
            for ev in [e for ev_ in events for e in (ev_, ev_[:-1])]:
                variants = banks.event_media(ev)
                if variants:
                    event = ev
                    break
            if not variants:
                sys.exit(f"{name}: none of {events} resolves - game patch changed the bank?")
            m = variants[0] if mid is None else mid
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
