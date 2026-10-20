r"""Pull Graves's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_graves.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Volibear route (extract_volibear.py): reads (never writes) Game/DATA/FINAL/Champions/Graves.wad.client and
Graves.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (named in the champion's bin, prefix Play_sfx_Graves_Graves): BasicAttack_OnMissileLaunch /
_OnHit / _pump, BasicAttackSpread_reload_open / _close (New Destiny's reload), QLineSpell_OnCast / QLineMis_OnHit /
QZoneTimer_boom (End of the Line), SmokeGrenade_OnCast / SmokeGrenadeBoom_hit (Smoke Screen, in the attack), Move_OnCast
(Quickdraw), ChargeShot_OnCast / ChargeShotShot_OnMissileLaunch / _hit
(Collateral Damage). Voice (Play_vo_Graves_): Attack2DGeneral (End of the Line: no Q line in the bank), GravesMove_cast3D,
GravesSmokeGrenade_cast3D, GravesChargeShot_cast3D.
Icons: GravesQ = skill (End of the Line), GravesE = skill2 (Quickdraw), GravesR = ult (Collateral Damage), GravesW
(Smoke Screen, in the attack: league_graves_w) and GravesP (league_graves_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/graves/skins/base/graves_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/graves/skins/base/graves_base_vo_"  # same in every language
P = "Play_sfx_Graves_Graves"
V = "Play_vo_Graves_"
C = "league_graves_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnMissileLaunch"], None, 0.9, -13),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.6, -16),
    C + "a_pump": ([P + "BasicAttack_pump"], None, 0.8, -15),
    C + "a_open": ([P + "BasicAttackSpread_reload_open"], None, 0.8, -15),
    C + "a_close": ([P + "BasicAttackSpread_reload_close"], None, 0.8, -15),
    C + "q": ([P + "QLineSpell_OnCast"], None, 1.0, -13),
    C + "q_hit": ([P + "QLineMis_OnHit"], None, 0.8, -15),
    C + "q_bang": ([P + "QZoneTimer_boom"], None, 1.5, -11),
    C + "w": ([P + "SmokeGrenade_OnCast"], None, 1.0, -14),
    C + "w_bang": ([P + "SmokeGrenadeBoom_hit"], None, 1.5, -12),
    C + "e": ([P + "Move_OnCast"], None, 1.0, -13),
    C + "r": ([P + "ChargeShot_OnCast"], None, 1.2, -12),
    C + "r_fire": ([P + "ChargeShotShot_OnMissileLaunch"], None, 1.5, -10),
    C + "r_hit": ([P + "ChargeShotShot_hit"], None, 1.5, -10),
    C + "vo_q": ([V + "Attack2DGeneral"], None, 3.0, -6),
    C + "vo_w": ([V + "GravesSmokeGrenade_cast3D"], None, 3.0, -6),
    C + "vo_e": ([V + "GravesMove_cast3D"], None, 3.0, -6),
    C + "vo_r": ([V + "GravesChargeShot_cast3D"], None, 4.0, -6),
}
I = "assets/characters/graves/hud/icons2d/graves"
ICONS = {  # TFM2 slot -> Riot icon
    "league_graves_skill": I + "q.dds",
    "league_graves_skill2": I + "e.dds",
    "league_graves_ult": I + "r.dds",
    "league_graves_w": I + "w.dds",
    "league_graves_passive": I + "p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Graves.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Graves.{args.lang}.wad.client"))
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
