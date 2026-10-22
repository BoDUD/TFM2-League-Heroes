r"""Pull Ivern's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_ivern.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Hwei route (extract_hwei.py): reads (never writes) Game/DATA/FINAL/Champions/Ivern.wad.client and
Ivern.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event unless
a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c)
Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Ivern_Ivern, the event names his skin bins name): the ranged attack's cast and hit;
the brush's growing (WPassive); Triggerseed's cast, its shield bursting and its hit; Rootcaller's cast and its hit on
the spot; Daisy!'s cast, Daisy's spawn, her punch's hit and her slam's hit. Voice (Play_vo_Ivern_Ivern): E_cast3D,
Q_cast3D, R_cast3D.
Icons: IvernE = skill (Triggerseed), IvernQ = skill2 (Rootcaller), IvernR = ult (Daisy!), IvernW = the brush
(league_ivern_w), IvernP = Friend of the Forest (league_ivern_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/ivern/skins/base/ivern_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/ivern/skins/base/ivern_base_vo_"  # same in every language
P = "Play_sfx_Ivern_Ivern"
V = "Play_vo_Ivern_Ivern"
C = "league_ivern_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS); the sfx at the level Qiyana's and Hwei's got, the voice as the others'
CLIPS = {
    C + "a": ([P + "BasicAttackRanged_cast", P + "BasicAttack_cast"], None, 0.6, -8),
    C + "a_hit": ([P + "BasicAttackRanged_hit", P + "BasicAttack_OnHit"], None, 0.8, -7),
    C + "w": ([P + "WPassive_OnBuffActivate"], None, 1.5, -7),
    C + "e": ([P + "E_OnCast"], None, 1.0, -6),
    C + "e_burst": ([P + "E_OnBuffDeactivate", P + "E_shield_obd"], None, 1.2, -5),
    C + "e_hit": ([P + "E_hit"], None, 0.8, -7),
    C + "q": ([P + "Q_OnCast", P + "Q_OnMissileLaunch"], None, 1.0, -6),
    C + "q_hit": ([P + "Q_OnHitLocation"], None, 1.2, -5),
    C + "r": ([P + "R_OnCast"], None, 1.5, -5),
    C + "r_drop": ([P + "R_DaisySpawn_cast"], None, 2.0, -4),
    C + "r_punch": ([P + "R_Daisy_hit"], None, 1.0, -5),
    C + "r_slam": ([P + "R_Daisy_slam_hit"], None, 1.5, -4),
    C + "vo_e": ([V + "E_cast3D"], None, 2.5, -6),
    C + "vo_q": ([V + "Q_cast3D"], None, 2.5, -6),
    C + "vo_r": ([V + "R_cast3D"], None, 3.0, -6),
}
I = "assets/characters/ivern/hud/icons2d/ivern"
ICONS = {  # TFM2 slot -> Riot icon
    "league_ivern_skill": I + "e.dds",
    "league_ivern_skill2": I + "q.dds",
    "league_ivern_ult": I + "r.dds",
    "league_ivern_w": I + "w.dds",
    "league_ivern_passive": I + "p.dds",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Ivern.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Ivern.{args.lang}.wad.client"))
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
