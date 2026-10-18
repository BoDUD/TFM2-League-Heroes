r"""Pull Poppy's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_poppy.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_poppy.py: reads (never writes) Game/DATA/FINAL/Champions/Poppy.wad.client and
Poppy.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event),
decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus
64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Poppy_Poppy, named in the champion's bins): BasicAttack_OnHit, PassiveAttack_*
and PassiveBounce / PassiveShield (Iron Ambassador's throw, bounce and pick-up), QSpell_OnCast / OnHitLocation / Q_hit2
(Hammer Shock and its rupture), W_OnCast / WKnockUp (Steadfast Presence and its interrupt), E_OnCast / E_hit / E_stun
(Heroic Charge and the wall), R_chargeup / RSpell_OnCast / RSpellInstant_cast / RMissile_hit (Keeper's Verdict charged,
tapped, its hit). Voice (Play_vo_Poppy_): the spells' cast3D lines.
Icons: poppy_q = skill (Q), poppy_e = skill2 (E), poppy_r = ult; poppy_w and poppy_passive too (league_poppy_w,
_passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/poppy/skins/base/poppy_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/poppy/skins/base/poppy_base_vo_"  # same in every language
P = "Play_sfx_Poppy_Poppy"
V = "Play_vo_Poppy_"
C = "league_poppy_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -15),
    C + "p_throw": ([P + "PassiveAttack_throw"], None, 0.8, -15),
    C + "p_hit": ([P + "PassiveAttack_OnHit"], None, 0.8, -14),
    C + "p_land": ([P + "PassiveBounce_OnHitLocation1", P + "PassiveBounce_OnMissileLaunch"], None, 0.8, -16),
    C + "p_pick": ([P + "PassiveShield_OnBuffActivate2"], None, 1.0, -14),
    C + "q": ([P + "QSpell_OnCast"], None, 0.8, -14),
    C + "q_slam": ([P + "QSpell_OnHitLocation"], None, 1.2, -12),
    C + "q_burst": ([P + "Q_hit2"], None, 1.2, -12),
    C + "q_hit": ([P + "DevastatingBlow_hit", P + "BasicAttack_OnHit"], None, 0.8, -15),
    C + "w": ([P + "W_OnCast", P + "WZone_OnBuffActivate"], None, 1.2, -13),
    C + "w_block": ([P + "WKnockUp_OnBuffActivate"], None, 1.0, -13),
    C + "e": ([P + "E_OnCast"], None, 1.0, -13),
    C + "e_hit": ([P + "E_hit"], None, 1.0, -13),
    C + "e_stun": ([P + "E_stun"], None, 1.2, -12),
    C + "r_charge": ([P + "R_chargeup", P + "R_OnCast"], None, 1.4, -13),
    C + "r_swing": ([P + "RSpell_OnCast", P + "RMissile_OnMissileLaunch"], None, 1.4, -11),
    C + "r_tap": ([P + "RSpellInstant_cast"], None, 1.2, -11),
    C + "r_hit": ([P + "RMissile_hit", P + "RKnockUp_OnBuffActivate"], None, 1.2, -12),
    C + "vo_q": ([V + "PoppyQ_cast3D"], None, 2.0, -6),
    C + "vo_w": ([V + "PoppyW_cast3D"], None, 2.0, -6),
    C + "vo_e": ([V + "PoppyE_cast3D"], None, 2.0, -6),
    C + "vo_r": ([V + "PoppyR_cast3D"], None, 2.5, -6),
}
I = "assets/characters/poppy/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_poppy_skill": I + "poppy_q.dds",
    "league_poppy_skill2": I + "poppy_e.dds",
    "league_poppy_ult": I + "poppy_r.dds",
    "league_poppy_w": I + "poppy_w.dds",
    "league_poppy_passive": I + "poppy_passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Poppy.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Poppy.{args.lang}.wad.client"))
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
