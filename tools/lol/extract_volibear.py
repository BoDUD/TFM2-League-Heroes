r"""Pull Volibear's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_volibear.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_poppy.py: reads (never writes) Game/DATA/FINAL/Champions/Volibear.wad.client and
Volibear.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event),
decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus
64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Volibear_Volibear, named in the champion's bins): BasicAttack_OnCast / OnHit,
PApplicator_OnBuffActivate / PChain_hit (The Relentless Storm's charge and its chain lightning), W_cast / W_hit /
WEmp_hit (Frenzied Maul, the second bite), Q_OnCast / QAttack_OnCast / QAttack_OnHit (Thundering Smash), E_OnCast /
E_buffactivate / E_explo / E_hit (Sky Splitter's cast, warning, bolt, hit), R_jump / R_hit_ground / RSweetSpot_hit /
RTowerDisable_hit (Stormbringer). Voice (Play_vo_Volibear_Volibear): the spells' cast3D lines.
Icons: Volibear_Icon_Q = skill (Q), _E = skill2 (E), _R = ult; _W and _P too (league_volibear_w, _passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/volibear/skins/base/volibear_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/volibear/skins/base/volibear_base_vo_"  # same in every language
P = "Play_sfx_Volibear_Volibear"
V = "Play_vo_Volibear_Volibear"
C = "league_volibear_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a_swing": ([P + "BasicAttack_OnCast"], None, 0.8, -16),
    C + "a_hit": ([P + "BasicAttack_OnHit1"], None, 0.8, -15),
    C + "p_bolt": ([P + "PApplicator_OnBuffActivate6"], None, 1.0, -15),
    C + "p_hit": ([P + "PChain_hit"], None, 0.8, -14),
    C + "w": ([P + "W_cast"], None, 0.8, -14),
    C + "w_hit": ([P + "W_hit"], None, 0.8, -13),
    C + "w_heal": ([P + "WEmp_hit", P + "WEmp_cast"], None, 1.0, -13),
    C + "q": ([P + "Q_OnCast", P + "Q_OnBuffActivate"], None, 1.2, -13),
    C + "q_smash": ([P + "QAttack_OnCast"], None, 0.8, -13),
    C + "q_hit": ([P + "QAttack_OnHit"], None, 1.0, -12),
    C + "e": ([P + "E_OnCast0"], None, 1.0, -14),
    C + "e_cloud": ([P + "E_buffactivate"], None, 1.5, -14),
    C + "e_bolt": ([P + "E_explo"], None, 1.5, -11),
    C + "e_hit": ([P + "E_hit"], None, 1.0, -13),
    C + "e_sh": ([P + "EShield_OnBuffActivate2"], None, 1.0, -14),
    C + "r": ([P + "R_jump", P + "R_cast"], None, 1.2, -12),
    C + "r_land": ([P + "R_hit_ground"], None, 1.8, -10),
    C + "r_hit": ([P + "RSweetSpot_hit"], None, 1.0, -12),
    C + "r_tower": ([P + "RTowerDisable_hit2"], None, 1.2, -13),
    C + "vo_q": ([V + "Q_cast3D"], None, 2.0, -6),
    C + "vo_w": ([V + "W_cast3DK"], None, 2.0, -6),
    C + "vo_e": ([V + "E_cast3D"], None, 2.0, -6),
    C + "vo_r": ([V + "R_cast3D"], None, 2.5, -6),
}
I = "assets/characters/volibear/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_volibear_skill": I + "volibear_icon_q.dds",
    "league_volibear_skill2": I + "volibear_icon_e.dds",
    "league_volibear_ult": I + "volibear_icon_r.dds",
    "league_volibear_w": I + "volibear_icon_w.dds",
    "league_volibear_passive": I + "volibear_icon_p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Volibear.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Volibear.{args.lang}.wad.client"))
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
