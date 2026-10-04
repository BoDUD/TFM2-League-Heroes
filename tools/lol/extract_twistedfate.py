"""Pull Twisted Fate's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_twistedfate.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/TwistedFate.wad.client and TwistedFate.<lang>.wad.client, resolves the base-skin Wwise events
below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio
(c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written. Voice
language: zh_CN (Tencent client) by default.

His events in the base bank (the client's own names; lengths and peaks measured with work/tw/snd_probe_tw.py): the attack
is TwistedFateBasicAttack_OnCast (the flick, loudest 0.12-0.15 s in), _OnMissileLaunch (the card leaving) and _OnHit;
Stacked Deck's fourth attack throws with CardmasterStack_missilelaunch, its impact is the crit's _OnHit; Wild Cards
casts with WildCards_OnCast (the fan, loudest ~0.16 s in) over SealFateMissile_OnMissileLaunch (the cards flying) and
hits with SealFateMissile_OnHit; Pick a Card starts with PickACard_OnCast and flips a card with PickACard_flip; each
card has <Colour>CardPreAttack_OnBuffActivate (locked), _OnMissileLaunch (thrown) and <Colour>CardAttack_hit (its
impact); Destiny_OnCast (+ _OnBuffActivate) is the cast, Gate_OnBuffActivate the channel, Gate_marker the gate where
he lands (it builds to its peak 1.3 s in - the channel's 1.5 s), Destiny_OnBuffDeactivate his arrival. Voice: the
three cards' lock lines and the Destiny line. The icons: Cardmaster_PowerCard = Q, CardMaster_FatesGambit = W,
Destiny_temp = R (the bin's own references; Cardmaster_SealFate, the dice, is the passive's).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/twistedfate/skins/base/twistedfate_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/twistedfate/skins/base/twistedfate_base_vo_"  # same in every language
P = "Play_sfx_TwistedFate_"

# clip name -> (event, media id picked among the event's variants, max seconds, peak dBFS)
CLIPS = {
    "league_twistedfate_sfx_attack": (P + "TwistedFateBasicAttack_OnCast", 193139396, 0.5, -10),
    "league_twistedfate_sfx_card_fly": (P + "TwistedFateBasicAttack_OnMissileLaunch", 443517749, 0.4, -12),
    "league_twistedfate_sfx_attack_hit": (P + "TwistedFateBasicAttack_OnHit", 59766754, 0.6, -10),
    "league_twistedfate_sfx_e_throw": (P + "CardmasterStack_missilelaunch", 444840894, 0.9, -8),
    "league_twistedfate_sfx_e_hit": (P + "TwistedFateCritAttack_OnHit", 133802608, 0.7, -8),
    "league_twistedfate_sfx_q": (P + "WildCards_OnCast", 705558182, 1.0, -7),
    "league_twistedfate_sfx_q_fly": (P + "SealFateMissile_OnMissileLaunch", 593349300, 1.0, -11),
    "league_twistedfate_sfx_q_hit": (P + "SealFateMissile_OnHit", 1018677556, 0.5, -11),
    "league_twistedfate_sfx_w": (P + "PickACard_OnCast", 283303473, 0.6, -9),
    "league_twistedfate_sfx_w_flip": (P + "PickACard_flip", 834832808, 0.35, -12),
    "league_twistedfate_sfx_lock_blue": (P + "BlueCardPreAttack_OnBuffActivate", 26711449, 0.8, -8),
    "league_twistedfate_sfx_lock_red": (P + "RedCardPreAttack_OnBuffActivate", 295922981, 0.8, -8),
    "league_twistedfate_sfx_lock_gold": (P + "GoldCardPreAttack_OnBuffActivate", 623499601, 0.8, -8),
    "league_twistedfate_sfx_blue_throw": (P + "BlueCardAttack_OnMissileLaunch", 564653219, 0.6, -9),
    "league_twistedfate_sfx_red_throw": (P + "RedCardAttack_OnMissileLaunch", 791601176, 0.6, -9),
    "league_twistedfate_sfx_gold_throw": (P + "GoldCardAttack_OnMissileLaunch", 724441632, 0.8, -9),
    "league_twistedfate_sfx_blue_hit": (P + "BlueCardAttack_hit", 748344037, 1.0, -7),
    "league_twistedfate_sfx_red_hit": (P + "RedCardAttack_hit", 931683055, 1.0, -7),
    "league_twistedfate_sfx_gold_hit": (P + "GoldCardAttack_hit", 1033313971, 1.0, -7),
    "league_twistedfate_sfx_r": (P + "Destiny_OnCast", 349208112, 1.6, -7),
    "league_twistedfate_sfx_r_buff": (P + "Destiny_OnBuffActivate", 588745234, 0.8, -10),
    "league_twistedfate_sfx_gate": (P + "Gate_OnBuffActivate", 146622604, 1.2, -8),
    "league_twistedfate_sfx_gate_marker": (P + "Gate_marker", 537911484, 2.2, -9),
    "league_twistedfate_sfx_r_in": (P + "Destiny_OnBuffDeactivate", 164462257, 0.5, -10),
    "league_twistedfate_vo_blue": ("Play_vo_TwistedFate_BlueCardPreAttack_cast3D", 308901230, 0.9, -4),
    "league_twistedfate_vo_red": ("Play_vo_TwistedFate_RedCardPreAttack_cast3D", 1070747068, 0.9, -4),
    "league_twistedfate_vo_gold": ("Play_vo_TwistedFate_GoldCardPreAttack_cast3D", 475366823, 1.0, -4),
    "league_twistedfate_vo_r": ("Play_vo_TwistedFate_Destiny_cast3D", 14814922, 1.4, -3),
    "league_twistedfate_vo_gate": ("Play_vo_TwistedFate_Gate_cast3D", 1323513997, 1.0, -4),
}
ICONS = {  # TFM2 slot -> Riot icon
    "league_twistedfate_skill": "ASSETS/Characters/TwistedFate/HUD/Icons2D/Cardmaster_PowerCard.dds",
    "league_twistedfate_skill2": "ASSETS/Characters/TwistedFate/HUD/Icons2D/CardMaster_FatesGambit.dds",
    "league_twistedfate_ult": "ASSETS/Characters/TwistedFate/HUD/Icons2D/Destiny_temp.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "TwistedFate.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"TwistedFate.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (event, mid, max_s, peak) in CLIPS.items():
            variants = banks.event_media(event)
            if mid not in variants:
                sys.exit(f"{event}: media {mid} not found (variants: {variants}) - game patch changed the bank?")
            sr, x = decode(media[mid], args.vgmstream)
            pcm = finish(x, sr, max_s, peak)
            with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes(pcm.tobytes())
            print(f"{name:38s} {len(pcm) / sr:4.2f}s  <- {event}")

    icon_dir = os.path.join(MOD, "icons")
    os.makedirs(lp(icon_dir), exist_ok=True)
    for name, path in ICONS.items():
        img = Image.open(io.BytesIO(main_wad.read_path(path))).convert("RGBA")
        img.resize((64, 64), Image.LANCZOS).save(lp(os.path.join(icon_dir, name + ".png")))
        print(f"{name:38s} icon {img.size} <- {path}")


if __name__ == "__main__":
    main()
