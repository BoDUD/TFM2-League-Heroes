r"""Pull Nunu & Willump's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_nunu.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Illaoi route (extract_illaoi.py): reads (never writes) Game/DATA/FINAL/Champions/Nunu.wad.client and
Nunu.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event unless
a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Nunu_Nunu, the event names his skin bins name): Willump's swipe and its hit;
Consume's bite and its swallow; the snowball's cast and its explosion; the barrage's cast, a snowball thrown and the
root's ice (ESnowballMissile_OnHit1 resolves to no media in the local banks: e_hit takes ERoot's first variant, r_hit its
fifth); Absolute Zero's cast and its burst. Voice (Play_vo_Nunu_): Attack2DGeneral (the bite), NunuW_cast3D,
NunuE_cast3D, NunuR_cast3D.
Icons: NunuW1 = skill (Biggest Snowball Ever!), NunuE = skill2 (Snowball Barrage), NunuR = ult (Absolute Zero), NunuQ =
Consume (league_nunu_q), NunuPassive = Call of the Freljord (league_nunu_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/nunu/skins/base/nunu_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/nunu/skins/base/nunu_base_vo_"  # same in every language
P = "Play_sfx_Nunu_Nunu"
V = "Play_vo_Nunu_"
C = "league_nunu_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS); the sfx at the level Illaoi's got, the voice as the others'
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.7, -8),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -7),
    C + "q": ([P + "Q_OnCast"], None, 1.0, -6),
    C + "q_hit": ([P + "Q_OnCast_swallow", P + "Q_OnCast"], None, 1.0, -6),
    C + "w": ([P + "W_OnCast", P + "W_cast"], None, 1.2, -6),
    C + "w_hit": ([P + "WExplodeLarge_cast", P + "WExplodeSmall_cast"], None, 1.5, -5),
    C + "e": ([P + "E_OnCast"], None, 1.0, -6),
    C + "e_throw": ([P + "ESnowballBurstFire_OnCast"], None, 0.6, -8),
    C + "e_hit": ([P + "ESnowballMissile_OnHit1", P + "ERoot_OnBuffCast"], None, 0.8, -7),
    C + "r": ([P + "R_OnCast"], None, 2.0, -5),
    C + "r_boom": ([P + "R_hit"], None, 2.0, -4),
    C + "r_hit": ([P + "ERoot_OnBuffCast", P + "ESnowballMissile_OnHit1"], 4, 1.0, -6),   # another variant than e_hit's
    C + "vo_q": ([V + "Attack2DGeneral"], None, 2.5, -6),
    C + "vo_w": ([V + "NunuW_cast3D"], None, 2.5, -6),
    C + "vo_e": ([V + "NunuE_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "NunuR_cast3D"], None, 3.0, -6),
}
I = "assets/characters/nunu/hud/icons2d/nunu"
ICONS = {  # TFM2 slot -> Riot icon
    "league_nunu_skill": I + "w1.dds",
    "league_nunu_skill2": I + "e.dds",
    "league_nunu_ult": I + "r.dds",
    "league_nunu_q": I + "q.dds",
    "league_nunu_passive": I + "passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Nunu.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Nunu.{args.lang}.wad.client"))
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
