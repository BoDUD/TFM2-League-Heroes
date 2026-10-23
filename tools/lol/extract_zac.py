r"""Pull Zac's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_zac.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Illaoi route (extract_illaoi.py): reads (never writes) Game/DATA/FINAL/Champions/Zac.wad.client and
Zac.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event unless
a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Zac_, the event names his skin bins name): his punch and its hit; Stretching
Strikes' cast, the grab's hit and the slam (ZacQattack_OnHit); Unstable Matter's burst and its hit; the slingshot's
charge (ZacE_OnCast) and its landing (ZacE_hit) and the knock-up (ZacE_hitg); Let's Bounce!'s cast, a bounce, the
splat and the hit; a blob absorbed (ZacWPassive_buffactivate_heal). Voice (Play_vo_Zac_): ZacQ_cast3D, ZacE_cast3D,
ZacR_cast3D; the add-on's revive: zacrebirthstart_OnBuffActivate (the split), Respawn (the reform), the voice
Spell3DPReviveStart.
Icons: ZacQ = skill (Stretching Strikes), ZacE = skill2 (Elastic Slingshot), ZacR = ult (Let's Bounce!), ZacW = Unstable
Matter (league_zac_w), ZacPassive = Cell Division (league_zac_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/zac/skins/base/zac_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/zac/skins/base/zac_base_vo_"  # same in every language
P = "Play_sfx_Zac_"
V = "Play_vo_Zac_"
C = "league_zac_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS); the sfx at the level Illaoi's got, the voice as the others'
CLIPS = {
    C + "a": ([P + "ZacBasicAttack_OnCast"], None, 0.7, -8),
    C + "a_hit": ([P + "ZacBasicAttack_OnHit"], None, 0.8, -7),
    C + "q": ([P + "ZacQ_OnCast"], None, 1.0, -6),
    C + "q_hit": ([P + "ZacQmissile_OnHit", P + "ZacQHit_hit"], None, 1.0, -6),
    C + "q_slam": ([P + "ZacQattack_OnHit", P + "ZacQHit_hit"], None, 1.2, -5),
    C + "w": ([P + "ZacW_OnCast"], None, 1.2, -6),
    C + "w_hit": ([P + "ZacQmissile_OnHit"], 3, 0.8, -7),   # no W hit of its own in the base banks: another variant of the grab's hit
    C + "e": ([P + "ZacE_OnCast", P + "ZacE_OnBuffActivate"], None, 1.5, -6),
    C + "e_land": ([P + "ZacE_hit"], None, 1.5, -4),
    C + "e_hit": ([P + "ZacE_hit"], 3, 1.0, -6),   # the knock-up: another variant of the landing (no hitg media)
    C + "r": ([P + "ZacR_OnCast"], None, 1.5, -5),
    C + "r_hop": ([P + "ZacR_bounce_lua"], None, 0.8, -7),
    C + "r_land": ([P + "ZacR_bounce_lua"], 8, 1.0, -5),   # the splat: a later variant of the bounce (no hit_splatD media)
    C + "r_hit": ([P + "ZacQattack_OnHit"], 3, 1.0, -6),   # a slam hit (no hit_smallerslam media)
    C + "b_pick": ([P + "ZacWPassive_buffactivate_heal"], None, 1.0, -7),
    C + "p_split": ([P + "zacrebirthstart_OnBuffActivate", P + "Bloblet_Death"], None, 1.5, -5),   # the add-on's revive
    C + "p_reform": ([P + "Respawn"], None, 2.0, -5),
    C + "vo_p": ([V + "Spell3DPReviveStart"], None, 2.5, -6),
    C + "vo_q": ([V + "ZacQ_cast3D"], None, 2.5, -6),
    C + "vo_e": ([V + "ZacE_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "ZacR_cast3D"], None, 3.0, -6),
}
I = "assets/characters/zac/hud/icons2d/zac"
ICONS = {  # TFM2 slot -> Riot icon
    "league_zac_skill": I + "q.dds",
    "league_zac_skill2": I + "e.dds",
    "league_zac_ult": I + "r.dds",
    "league_zac_w": I + "w.dds",
    "league_zac_passive": I + "passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Zac.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Zac.{args.lang}.wad.client"))
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
