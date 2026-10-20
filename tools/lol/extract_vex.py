r"""Pull Vex's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_vex.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_zoe.py: reads (never writes) Game/DATA/FINAL/Champions/Vex.wad.client and
Vex.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event),
decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus
64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Events (prefix Play_sfx_Vex_, named in the champion's bins): VexBasicAttack_OnCast / OnHit, VexQ_OnCast /
VexQ_missilelaunch / VexQ_OnHit (Mistral Bolt), VexW_cast / VexW_hit (Personal Space), VexE_OnCast / VexE_hit (Looming
Darkness), VexPGloom_buffactivate (Gloom laid), VexPGloomAttack_OnHitLocation (Gloom consumed), VexPDoom_buffactivate
(Doom ready), VexPFear_buffactivate (the fear), VexR_OnCast / VexR_missilelaunch / VexR_OnHit (Shadow Surge's
missile and mark), VexR2_OnCast / VexR2_hit (the surge and its blow). Voice (Play_vo_Vex_): VexQ_cast3D, VexE_cast3D,
VexW_cast3D, VexR_cast3D.
Icons (the bins' icons): Icons_Vex_Q01 = skill, Icons_Vex_E01 = skill2, Icons_Vex_R01 = ult, Icons_Vex_W01 = W,
Icons_Vex_Passive = passive (for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/vex/skins/base/vex_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/vex/skins/base/vex_base_vo_"  # same in every language
P = "Play_sfx_Vex_"
V = "Play_vo_Vex_"
C = "league_vex_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "VexBasicAttack_OnCast", P + "VexBasicAttack_missilelaunch"], None, 0.8, -16),
    C + "a_hit": ([P + "VexBasicAttack_OnHit"], None, 0.8, -15),
    C + "w": ([P + "VexW_cast"], None, 1.4, -13),
    C + "w_hit": ([P + "VexW_hit"], None, 1.0, -14),
    C + "q": ([P + "VexQ_OnCast", P + "VexQ_missilecast"], None, 1.0, -14),
    C + "q_fly": ([P + "VexQ_missilelaunch"], None, 1.4, -14),
    C + "q_hit": ([P + "VexQ_OnHit"], None, 1.0, -13),
    C + "e": ([P + "VexE_OnCast", P + "VexE_cast"], None, 1.0, -14),
    C + "e_land": ([P + "VexE_hit"], None, 1.6, -12),
    C + "e_hit": ([P + "VexPGloom_buffactivate"], None, 1.2, -14),
    C + "g_pop": ([P + "VexPGloomAttack_OnHitLocation", P + "VexPGloomAttack_buffactivate"], None, 1.2, -12),
    C + "p_ready": ([P + "VexPDoom_buffactivate"], None, 1.4, -14),
    C + "p_fear": ([P + "VexPFear_buffactivate"], None, 1.4, -13),
    C + "r": ([P + "VexR_OnCast"], None, 1.2, -13),
    C + "r_fly": ([P + "VexR_missilelaunch", P + "VexR_OnMissileCast"], None, 1.6, -14),
    C + "r_mark": ([P + "VexR_OnHit"], None, 1.2, -13),
    C + "r_dash": ([P + "VexR2_OnCast", P + "VexR2_travel_missilelaunch"], None, 1.2, -13),
    C + "r_hit": ([P + "VexR2_hit"], None, 1.4, -11),
    C + "vo_q": ([V + "VexQ_cast3D"], None, 2.0, -6),
    C + "vo_e": ([V + "VexE_cast3D"], None, 2.0, -6),
    C + "vo_w": ([V + "VexW_cast3DK", V + "VexW_cast3D"], None, 2.0, -6),
    C + "vo_r": ([V + "VexR_cast3D"], None, 2.0, -6),
}
I = "assets/characters/vex/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_vex_skill": I + "icons_vex_q01.dds",
    "league_vex_skill2": I + "icons_vex_e01.dds",
    "league_vex_ult": I + "icons_vex_r01.dds",
    "league_vex_w": I + "icons_vex_w01.dds",
    "league_vex_passive": I + "icons_vex_passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Vex.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Vex.{args.lang}.wad.client"))
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
