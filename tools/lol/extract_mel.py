r"""Pull Mel's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_mel.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

The Volibear route (extract_volibear.py): reads (never writes) Game/DATA/FINAL/Champions/Mel.wad.client and
Mel.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (named in the champion's bins, prefix Play_sfx_Mel_Mel): BasicAttack_OnMissileLaunch / _OnHit,
PassiveBonusMissileLeft_OnHit (Searing Brilliance's bolts), Q_OnCast / Q_hit (Radiant Volley), W_OnCast /
WReflect_Normal_buffactivate (Rebuttal and its reflection), E_OnCast / E_hit_root_champion_buffactivate (Solar Snare),
R_OnCast / R_enemy_hit (Golden Eclipse), Execute_champion (Overwhelm's execute, the add-on). Voice (Play_vo_Mel_):
MelQ_cast3D, MelW_cast3D, MelE_cast3D, MelR_cast3D. Voice clips are league_mel_sfx_vo_* (a clip never shares its
sound's name).
Icons: Mel_Q = skill (Radiant Volley), Mel_E = skill2 (Solar Snare), Mel_R = ult (Golden Eclipse), Mel_W (Rebuttal,
in the attack: league_mel_w) and Mel_Passive (league_mel_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/mel/skins/base/mel_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/mel/skins/base/mel_base_vo_"  # same in every language
P = "Play_sfx_Mel_Mel"
V = "Play_vo_Mel_Mel"
C = "league_mel_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnMissileLaunch", P + "BasicAttack_OnCast"], None, 0.8, -15),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -16),
    C + "p_hit": ([P + "PassiveBonusMissileLeft_OnHit", P + "PassiveBonusMissileRight_OnHit"], None, 0.6, -18),
    C + "q": ([P + "Q_OnCast", P + "Q_missilecast"], None, 1.2, -13),
    C + "q_hit": ([P + "Q_hit", P + "Q_hitlocation"], None, 1.0, -14),
    C + "w": ([P + "W_OnCast"], None, 1.5, -13),
    C + "w_reflect": ([P + "WReflect_Normal_buffactivate"], None, 1.0, -13),
    C + "e": ([P + "E_OnCast", P + "E_OnMissileLaunch"], None, 1.2, -13),
    C + "e_hit": ([P + "E_hit_root_champion_buffactivate", P + "E_hit_edge0"], None, 1.2, -13),
    C + "r": ([P + "R_OnCast"], None, 2.0, -12),
    C + "r_hit": ([P + "R_enemy_hit"], None, 1.5, -12),
    C + "x": ([P + "Execute_champion"], None, 1.5, -12),
    C + "vo_q": ([V + "Q_cast3D"], None, 3.0, -6),
    C + "vo_w": ([V + "W_cast3D"], None, 3.0, -6),
    C + "vo_e": ([V + "E_cast3D"], None, 3.0, -6),
    C + "vo_r": ([V + "R_cast3D"], None, 4.0, -6),
}
I = "assets/characters/mel/hud/icons2d/mel_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_mel_skill": I + "q.dds",
    "league_mel_skill2": I + "e.dds",
    "league_mel_ult": I + "r.dds",
    "league_mel_w": I + "w.dds",
    "league_mel_passive": I + "passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Mel.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Mel.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (events, mid, max_s, peak) in CLIPS.items():
            event, variants = None, []
            # (the bins' names can carry a glued character - "OnBuffActivate2", "Q_hit2": also try them without it)
            for ev in [e for ev_ in events for e in (ev_, ev_[:-1])]:
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
