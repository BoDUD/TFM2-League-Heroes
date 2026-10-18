r"""Pull Wukong's (MonkeyKing's) sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_wukong.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

Same route as extract_ziggs.py: reads (never writes) Game/DATA/FINAL/Champions/MonkeyKing.wad.client and
MonkeyKing.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a media id is given), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_MonkeyKing_MonkeyKing, named in the champion's bins): BasicAttack_OnCast / _OnHit,
BasicAttack2_OnHit0 (the clone's taps), QAttack_OnCast / _OnHit (Crushing Blow), Nimbus_OnCast / NimbusKick_hit (Nimbus
Strike), W_cast (Warrior Trickster), SpinToWin_OnCast / _hit / _hitbig (Cyclone). Voice (Play_vo_MonkeyKing_): the
spells' cast3D lines (QAttack, Nimbus, DecoySwipe_OnCast, SpinToWin).
Icons: MonkeyKingNimbusStrike = skill (E), MonkeyKingDecoy = skill2 (W), MonkeyKingCyclone = ult; MonkeyKingCrushingBlow
and MonkeyKingStoneSkin too (league_wukong_q, _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/monkeyking/skins/base/monkeyking_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/monkeyking/skins/base/monkeyking_base_vo_"  # same in every language
P = "Play_sfx_MonkeyKing_MonkeyKing"
V = "Play_vo_MonkeyKing_"
C = "league_wukong_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.6, -16),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -14),
    C + "q": ([P + "QAttack_OnCast", P + "DoubleAttack_OnCast"], None, 0.8, -13),
    C + "q_hit": ([P + "QAttack_OnHit"], None, 1.0, -11),
    C + "e": ([P + "Nimbus_OnCast"], None, 1.0, -13),
    C + "e_hit": ([P + "NimbusKick_hit"], None, 0.8, -13),
    C + "w": ([P + "W_cast", P + "Decoy_cast"], None, 1.0, -13),
    C + "w_hit": ([P + "BasicAttack2_OnHit0", P + "BasicAttack_OnHit"], None, 0.6, -16),
    C + "r": ([P + "SpinToWin_OnCast"], None, 1.4, -11),
    C + "r_spin": ([P + "SpinToWin_hit"], None, 0.5, -15),
    C + "r_up": ([P + "SpinToWin_hitbig"], None, 1.0, -11),
    C + "vo_q": ([V + "MonkeyKingQAttack_cast3D", V + "Spell3DQCast"], None, 2.0, -6),
    C + "vo_e": ([V + "MonkeyKingNimbus_cast3D", V + "Spell3DECast"], None, 2.0, -6),
    C + "vo_w": ([V + "MonkeyKingDecoySwipe_OnCast", V + "Spell3DBasic"], None, 2.0, -6),
    C + "vo_r": ([V + "MonkeyKingSpinToWin_cast3D", V + "Spell3DRCast"], None, 2.5, -6),
}
I = "assets/characters/monkeyking/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_wukong_skill": I + "monkeykingnimbusstrike.dds",
    "league_wukong_skill2": I + "monkeykingdecoy.dds",
    "league_wukong_ult": I + "monkeykingcyclone.dds",
    "league_wukong_q": I + "monkeykingcrushingblow.dds",
    "league_wukong_passive": I + "monkeykingstoneskin.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "MonkeyKing.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"MonkeyKing.{args.lang}.wad.client"))
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
