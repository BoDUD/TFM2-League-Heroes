"""Pull Briar's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_briar.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe

Same route as extract_garen.py (its decode/finish helpers are reused): reads (never writes)
Game/DATA/FINAL/Champions/Briar.wad.client and Briar.<lang>.wad.client, resolves the base-skin
Wwise events below to their media, decodes them with vgmstream and writes mono 16-bit WAVs to
league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus 64x64 ability icons to league/icons/.
Without --vgmstream only the icons are written. Voice language: zh_CN (Tencent client) by default.

Every event is named in Briar's skin bin. The basic attack keeps its hit (the engine plays nothing of its own);
Snack Attack the frenzied bite's hit; Head Rush the cast and the impact; Blood Frenzy the activation on her
(BriarWAttackSpell_buffactivate_self); Chilling Scream the charge, the charged launch and the knockback;
Certain Death the kick, the gem hitting its prey and her landing. Of the zh_CN voice takes (each its own
recording) the longest ones are used. The W events BriarW_OnCast4 and the frenzy state buffs resolve to no
media of their own in this bank, so the frenzy's sound is the self activation.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/briar/skins/base/briar_base_sfx_"
# the same path in every language WAD
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/briar/skins/base/briar_base_vo_"

# clip name -> (event, media id picked among the event's random variants, max seconds, peak dBFS)
CLIPS = {
    "league_briar_sfx_attack_hit": ("Play_sfx_Briar_BriarBasicAttack_OnHit", 346967776, 0.5, -6),
    "league_briar_sfx_snack": ("Play_sfx_Briar_BriarBasicAttackFrenzy_OnHit", 989498368, 1.0, -4),
    "league_briar_sfx_q_cast": ("Play_sfx_Briar_BriarQ_OnCast", 438296832, 1.0, -4),
    "league_briar_sfx_q_hit": ("Play_sfx_Briar_BriarQ_hit_vfx", 463314778, 1.2, -3),
    "league_briar_sfx_w_frenzy": ("Play_sfx_Briar_BriarWAttackSpell_buffactivate_self", 509331730, 1.6, -4),
    "league_briar_sfx_e_charge": ("Play_sfx_Briar_BriarEMisStrong_cast_charge", 751954609, 1.1, -5),
    "league_briar_sfx_e_scream": ("Play_sfx_Briar_BriarEMisStrong_missilelaunch_charged", 397557461, 1.6, -3),
    "league_briar_sfx_e_stun": ("Play_sfx_Briar_BriarEKnockback_buffcast", 319889801, 1.2, -5),
    "league_briar_sfx_r_cast": ("Play_sfx_Briar_BriarR_OnCast", 342737364, 1.4, -3),
    "league_briar_sfx_r_mark": ("Play_sfx_Briar_BriarR_OnHit", 699304794, 1.6, -4),
    "league_briar_sfx_r_land": ("Play_sfx_Briar_BriarR_hit_self", 400504619, 2.0, -2),
    "league_briar_vo_q": ("Play_vo_Briar_BriarQ_cast3D", 4149525649, 1.4, -2),
    "league_briar_vo_w": ("Play_vo_Briar_BriarW_cast3D", 1025121471, 1.6, -2),
    "league_briar_vo_r": ("Play_vo_Briar_BriarR_cast3D", 4032453267, 1.3, -2),
    "league_briar_vo_r_hit": ("Play_vo_Briar_Spell3DRHit", 665902220, 2.1, -2),
}
ICONS = {  # TFM2 slot -> Riot icon (skill is Head Rush with Blood Frenzy folded in: Q's icon)
    "league_briar_skill": "ASSETS/Characters/Briar/HUD/Icons2D/BriarQ.dds",
    "league_briar_skill2": "ASSETS/Characters/Briar/HUD/Icons2D/BriarE.dds",
    "league_briar_ult": "ASSETS/Characters/Briar/HUD/Icons2D/BriarR.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Briar.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Briar.{args.lang}.wad.client"))
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
