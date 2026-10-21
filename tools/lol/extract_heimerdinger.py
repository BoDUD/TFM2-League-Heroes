r"""Pull Heimerdinger's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_heimerdinger.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_zyra.py: reads (never writes) Game/DATA/FINAL/Champions/Heimerdinger.wad.client and
Heimerdinger.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each
event), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot
Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Events (named in the skin bins; the turrets' sounds sit in Heimerdinger's own bank): HeimerdingerBasicAttack_OnCast /
OnHit, HeimerdingerW_OnCast / HeimerdingerWAttack2_hit (a rocket), HeimerdingerQ_OnCast, the turret HeimerTYellow's
HeimerdingerQSpawnDestroyAudio_OnBuffActivate (it stands up), HeimerTYellowBasicAttack_OnHit (its shot),
HeimerdingerTurretEnergyBlast_OnHit (its beam), HeimerdingerE_OnCast / HeimerdingerESpell_hit, HeimerdingerR_OnBuffActivate,
HeimerdingerEUlt_OnCast / HeimerdingerESpell_Ult_hit (CH-3X), HeimerdingerSuperTurret_OnBuffActivate (the apex turret
cast), the apex HeimerTBlue's HeimerdingerRQEngineAudio_OnBuffActivate and HeimerTBlueBasicAttack_OnHit. Voice
(Play_vo_Heimerdinger_): HeimerdingerQ_cast3D, HeimerdingerE_cast3D, HeimerdingerR_cast3D.
Icons (the bin's): Q1 = skill, E1 = skill2, R = ult, W1 = W, Passive = passive (for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/heimerdinger/skins/base/heimerdinger_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/heimerdinger/skins/base/heimerdinger_base_vo_"  # every language
P = "Play_sfx_Heimerdinger_Heimerdinger"
TY = "Play_sfx_HeimerTYellow_"
TB = "Play_sfx_HeimerTBlue_"
V = "Play_vo_Heimerdinger_Heimerdinger"
C = "league_heimerdinger_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast", P + "BasicAttack_OnMissileLaunch"], None, 0.8, -16),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -15),
    C + "w": ([P + "W_OnCast", P + "WAttack2_OnMissileLaunch"], None, 1.2, -14),
    C + "w_hit": ([P + "WAttack2_hit"], None, 0.8, -16),
    C + "q": ([P + "Q_OnCast"], None, 1.0, -14),
    C + "t_spawn": ([TY + "HeimerdingerQSpawnDestroyAudio_OnBuffActivate"], None, 1.4, -14),
    C + "t_hit": ([TY + "HeimerTYellowBasicAttack_OnHit", TY + "HeimerTYellowBasicAttack2_OnHit"], None, 0.8, -17),
    C + "t_beam": ([TY + "HeimerdingerTurretEnergyBlast_OnHit", TY + "HeimerdingerTurretEnergyBlast_OnCast"], None, 1.2, -13),
    C + "e": ([P + "E_OnCast", P + "ESpell_OnMissileLaunch"], None, 1.0, -14),
    C + "e_land": ([P + "ESpell_hit"], None, 1.6, -12),
    C + "e_stun": ([P + "CritAttack_OnHit"], None, 0.8, -15),
    C + "r": ([P + "R_OnBuffActivate"], None, 1.6, -13),
    C + "re": ([P + "EUlt_OnCast", P + "ESpell_Ult_OnMissileLaunch"], None, 1.2, -13),
    C + "re_land": ([P + "ESpell_Ult_hit"], None, 1.8, -11),
    C + "rq": ([P + "SuperTurret_OnBuffActivate"], None, 1.6, -13),
    C + "x_spawn": ([TB + "HeimerdingerRQEngineAudio_OnBuffActivate"], None, 1.6, -14),
    C + "x_hit": ([TB + "HeimerTBlueBasicAttack_OnHit", TB + "HeimerdingerTurretBigEnergyBlast_OnHit"], None, 0.8, -15),
    C + "vo_q": ([V + "Q_cast3D"], None, 2.0, -6),
    C + "vo_e": ([V + "E_cast3D"], None, 2.0, -6),
    C + "vo_r": ([V + "R_cast3D"], None, 2.0, -6),
}
I = "assets/characters/heimerdinger/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_heimerdinger_skill": I + "heimerdinger_q1.dds",
    "league_heimerdinger_skill2": I + "heimerdinger_e1.dds",
    "league_heimerdinger_ult": I + "heimerdinger_r.dds",
    "league_heimerdinger_w": I + "heimerdinger_w1.dds",
    "league_heimerdinger_passive": I + "heimerdinger_passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Heimerdinger.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Heimerdinger.{args.lang}.wad.client"))
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
