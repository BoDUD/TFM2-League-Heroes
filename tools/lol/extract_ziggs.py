r"""Pull Ziggs's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_ziggs.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_jarvaniv.py: reads (never writes) Game/DATA/FINAL/Champions/Ziggs.wad.client and
Ziggs.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a media id is given), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Ziggs_Ziggs, named in data/characters/ziggs/ziggs.bin): BasicAttack_OnCast /
_OnHit, PassiveAttack_OnMissileLaunch / _OnHit1, Q_OnCast / Q_hit_bounce / Q_hit, E_OnCast / E2_OnMissileLaunch /
E_detonate, W_OnCast / W_detonate / W_hit_stop, R_OnCast / R_hit. Voice (Play_vo_Ziggs_): the spells' cast3D lines, or
the Spell3D* names if those do not resolve (league_jarvaniv's case).
Icons: ZiggsQ = skill, ZiggsE = skill2, ZiggsR = ult; ZiggsW and ZiggsPassiveReady too (league_ziggs_w, _passive, for
the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/ziggs/skins/base/ziggs_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/ziggs/skins/base/ziggs_base_vo_"  # same in every language
P = "Play_sfx_Ziggs_Ziggs"
V = "Play_vo_Ziggs_"
C = "league_ziggs_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.6, -16),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -14),
    C + "p": ([P + "PassiveAttack_OnMissileLaunch", P + "PassiveAttack_OnCast"], None, 0.8, -14),
    C + "p_hit": ([P + "PassiveAttack_OnHit1", P + "PassiveAttack_OnHit", P + "CritAttack_OnHit"], None, 1.0, -12),
    C + "q": ([P + "Q_OnCast", P + "QSpell_OnMissileLaunch"], None, 0.8, -13),
    C + "q_bounce": ([P + "Q_hit_bounce"], None, 0.6, -15),
    C + "q_blast": ([P + "Q_hit"], None, 1.2, -11),
    C + "q_hit": ([P + "Q_hit"], None, 0.6, -14),
    C + "e": ([P + "E_OnCast"], None, 0.8, -13),
    C + "e_land": ([P + "E2_OnMissileLaunch", P + "E2_OnBuffActivate"], None, 1.0, -13),
    C + "e_hit": ([P + "E_detonate"], None, 0.9, -12),
    C + "w": ([P + "W_OnCast"], None, 0.6, -14),
    C + "w_blast": ([P + "W_detonate"], None, 1.4, -10),
    C + "w_hit": ([P + "W_hit_stop"], None, 0.8, -13),
    C + "r": ([P + "R_OnCast", P + "R_missilelaunch"], None, 1.4, -11),
    C + "r_boom": ([P + "R_hit"], None, 2.4, -9),
    C + "r_hit": ([P + "R_hit"], None, 0.8, -13),
    C + "vo_q": ([V + "ZiggsQ_cast3D", V + "Spell3DQCast"], None, 2.0, -6),
    C + "vo_e": ([V + "ZiggsE_cast3D", V + "Spell3DECast"], None, 2.0, -6),
    C + "vo_w": ([V + "ZiggsW_cast3D", V + "Spell3DWHitSelf", V + "Spell3DWCast"], None, 2.0, -6),
    C + "vo_r": ([V + "ZiggsR_cast3D", V + "Spell3DRCast"], None, 2.5, -6),
}
I = "assets/characters/ziggs/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_ziggs_skill": I + "ziggsq.dds",
    "league_ziggs_skill2": I + "ziggse.dds",
    "league_ziggs_ult": I + "ziggsr.dds",
    "league_ziggs_w": I + "ziggsw.dds",
    "league_ziggs_passive": I + "ziggspassiveready.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Ziggs.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Ziggs.{args.lang}.wad.client"))
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
