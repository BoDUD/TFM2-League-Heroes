r"""Pull Gangplank's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_gangplank.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The route of tools/lol/extract_ziggs.py: reads (never writes) Game/DATA/FINAL/Champions/Gangplank.wad.client and
Gangplank.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a media id is given), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Gangplank_Gangplank, named in the champion's bins - not gangplank.bin, read every
PROP bin of the WAD): BasicAttack_OnCast / _OnHit, PassiveAttack_OnBuffCast, QProceed_OnMissileLaunch / _OnHit,
E_OnCast, EBarrelLife_OnBuffCast, EBarrelExplosionSound_OnBuffCast, W_OnCast / W_foley, R_OnCast / R_bigshot /
R_bomb_hit. Voice (Play_vo_Gangplank_): the spells' cast3D lines, or the Spell3D* names if those do not resolve.
Icons: Gangplank_Q = skill, Gangplank_E = skill2, Gangplank_R = ult; Gangplank_W and Gangplank_Passive too
(league_gangplank_w, _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/gangplank/skins/base/gangplank_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/gangplank/skins/base/gangplank_base_vo_"  # same in every language
P = "Play_sfx_Gangplank_Gangplank"
V = "Play_vo_Gangplank_"
C = "league_gangplank_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a_swing": ([P + "BasicAttack_OnCast"], None, 0.6, -16),
    C + "a_hit": ([P + "BasicAttack_OnHit", P + "CritAttack_OnHit"], None, 0.8, -14),
    C + "p_hit": ([P + "PassiveAttack_OnBuffCast", P + "PassiveAttackDoT_OnBuffCast"], None, 1.2, -12),
    C + "q_shot": ([P + "QProceed_OnMissileLaunch", P + "QProceed_OnCast", P + "QProceed_Cast_Point"], None, 1.0, -11),
    C + "q_hit": ([P + "QProceed_OnHit"], None, 0.8, -13),
    C + "e": ([P + "E_OnCast"], None, 0.8, -13),
    C + "e_land": ([P + "EBarrelLife_OnBuffCast", P + "E_powderburn"], None, 1.0, -14),
    C + "e_boom": ([P + "EBarrelExplosionSound_OnBuffCast", P + "R_bomb_hit"], None, 1.6, -9),   # the keg's own bank is not in the client
    C + "e_hit": ([P + "CritAttack_OnHit", P + "BasicAttack_OnHit"], None, 0.6, -15),
    C + "w": ([P + "W_OnCast"], None, 0.8, -13),
    C + "w_eat": ([P + "W_foley", P + "WAudioCleanse_OnBuffCast"], None, 1.2, -12),
    C + "r": ([P + "R_OnCast"], None, 1.4, -11),
    C + "r_call": ([P + "R_bigshot", P + "R_distantshots"], None, 2.0, -10),
    C + "r_wave": ([P + "R_bomb_hit"], None, 1.0, -11),
    C + "vo_q": ([V + "GangplankQProceed_cast3D", V + "Spell3DQCast"], None, 2.0, -6),
    C + "vo_e": ([V + "GangplankE_cast3D", V + "Spell3DEEnd"], None, 2.0, -6),
    C + "vo_w": ([V + "GangplankW_cast3D", V + "Spell3DWCast"], None, 2.0, -6),
    C + "vo_r": ([V + "GangplankR_cast3D", V + "Spell3DRCast"], None, 2.5, -6),
}
I = "assets/characters/gangplank/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_gangplank_skill": I + "gangplank_q.dds",
    "league_gangplank_skill2": I + "gangplank_e.dds",
    "league_gangplank_ult": I + "gangplank_r.dds",
    "league_gangplank_w": I + "gangplank_w.dds",
    "league_gangplank_passive": I + "gangplank_passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Gangplank.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Gangplank.{args.lang}.wad.client"))
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
