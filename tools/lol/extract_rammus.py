r"""Pull Rammus's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_rammus.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_poppy.py: reads (never writes) Game/DATA/FINAL/Champions/Rammus.wad.client and
Rammus.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event),
decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus
64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Events (prefix Play_sfx_Rammus_, named in the champion's bins): RammusBasicAttack_OnCast / OnHit (the tumble),
PowerBall_OnBuffActivate / hit (Powerball's curl and impact), DefensiveBallCurl_OnCast (W), PuncturingTaunt_OnCast /
OnHit (E), Tremors2_OnCast0 / land and RammusRKnockup_hit (Soaring Slam). Voice (Play_vo_Rammus_): he has no spell
lines, only his famous "OK." and a few grunts - Move2DStandard, Laugh3DGeneral, Taunt3DGeneralK, Attack2DGeneral.
Icons (the bins' mImgIconName): Armordillo_Powerball = skill (Q), Armordillo_ScaledPlating = skill2 (E Frenzying
Taunt), Armordillo_RecklessCharge = ult (R), Armordillo_ShellBash = W, Armordillo_ScavengeArmor = passive (for the
README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/rammus/skins/base/rammus_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/rammus/skins/base/rammus_base_vo_"  # same in every language
P = "Play_sfx_Rammus_"
V = "Play_vo_Rammus_"
C = "league_rammus_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a_swing": ([P + "RammusBasicAttack_OnCast"], None, 0.8, -16),
    C + "a_hit": ([P + "RammusBasicAttack_OnHit"], None, 0.8, -15),
    C + "q": ([P + "PowerBall_OnBuffActivate"], None, 1.4, -13),
    C + "q_hit": ([P + "PowerBall_hit"], None, 1.2, -12),
    C + "w": ([P + "DefensiveBallCurl_OnCast", P + "DefensiveBallCurl_OnBuffActivate2"], None, 1.2, -13),
    C + "e": ([P + "PuncturingTaunt_OnCast"], None, 1.2, -13),
    C + "e_hit": ([P + "PuncturingTaunt_OnHit"], None, 1.2, -13),
    C + "r": ([P + "Tremors2_OnCast0", P + "Tremors2_buffactivate"], None, 1.4, -12),
    C + "r_land": ([P + "Tremors2_land"], None, 1.6, -11),
    C + "r_hit": ([P + "RammusRKnockup_hit"], None, 1.2, -12),
    C + "vo_q": ([V + "Move2DStandard"], None, 2.0, -6),
    C + "vo_w": ([V + "Laugh3DGeneral"], None, 2.0, -6),
    C + "vo_e": ([V + "Taunt3DGeneralK", V + "Taunt3DGeneral"], None, 2.0, -6),
    C + "vo_r": ([V + "Attack2DGeneral"], None, 2.0, -6),
}
I = "assets/characters/rammus/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_rammus_skill": I + "armordillo_powerball.dds",
    "league_rammus_skill2": I + "armordillo_scaledplating.dds",
    "league_rammus_ult": I + "armordillo_recklesscharge.dds",
    "league_rammus_w": I + "armordillo_shellbash.dds",
    "league_rammus_passive": I + "armordillo_scavengearmor.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Rammus.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Rammus.{args.lang}.wad.client"))
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
