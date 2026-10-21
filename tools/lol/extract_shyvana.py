r"""Pull Shyvana's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_shyvana.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Volibear route (extract_volibear.py): reads (never writes) Game/DATA/FINAL/Champions/Shyvana.wad.client and
Shyvana.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (named in the skin bins, League 16.20's rework; prefix Play_sfx_Shyvana_Shyvana): BasicAttack_OnCast
/ _OnHit and DragonBasicAttack_OnCast / _OnHit (the claws), QAttack_OnCast / _OnHit and QAttack2_* (Emberstrike's two
strikes), QAttackDragon_* / QAttackDragon2_* / QAttackDragon3_* (wing, tail, bite), W_buffcast / W_buffdeactivate
(Inferno Aegis on and its blast), DragonW_heal, E_OnCast / E_hitlocation and EDragon_OnCast / EDragon_hitlocation (Molten
Burst), R_oncast is the dragon's (DragonR_oncast, DragonR_hit), DragonRTransform_buffactivate_loop (the transformation),
DragonR_untransform, DragonR_ready_self (full Fury). Voice (Play_vo_Shyvana_): ShyvanaQAttack_cast3D,
ShyvanaQAttack2_cast3D, ShyvanaE_cast3D, ShyvanaR_cast3D (in the bins but not in the 16.20 zh_CN bank: R falls back to
Dragon_Taunt3DGeneral), Dragon_Attack2DGeneral (the dragon's roar on the bite).
Icons: Shyvana_Q1 = skill (Emberstrike), Shyvana_E = skill2 (Molten Burst), Shyvana_R = ult (Dragon's Descent),
Shyvana_W1 (Inferno Aegis, in the attack: league_shyvana_w) and Shyvana_Passive (league_shyvana_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/shyvana/skins/base/shyvana_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/shyvana/skins/base/shyvana_base_vo_"  # same in every language
P = "Play_sfx_Shyvana_Shyvana"
V = "Play_vo_Shyvana_"
C = "league_shyvana_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.8, -14),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -15),
    C + "d_a": ([P + "DragonBasicAttack_OnCast"], None, 1.0, -13),
    C + "d_a_hit": ([P + "DragonBasicAttack_OnHit"], None, 0.8, -14),
    C + "q": ([P + "QAttack_OnCast", P + "Q_buffactivate"], None, 1.0, -13),
    C + "q_hit": ([P + "QAttack_OnHit"], None, 1.0, -12),
    C + "q2": ([P + "QAttack2_OnCast", P + "Q2_buffactivate"], None, 1.0, -13),
    C + "q2_hit": ([P + "QAttack2_OnHit"], None, 1.0, -12),
    C + "d_q": ([P + "QAttackDragon_OnCast"], None, 1.0, -13),
    C + "d_q2": ([P + "QAttackDragon2_OnCast"], None, 1.0, -13),
    C + "d_q3": ([P + "QAttackDragon3_OnCast"], None, 1.2, -12),
    C + "d_q3_hit": ([P + "QAttackDragon3_OnHit"], None, 1.0, -12),
    C + "w": ([P + "W_buffcast", P + "W_buffactivate"], None, 1.5, -13),
    C + "w_blast": ([P + "W_buffdeactivate", P + "W_buffdeactivate_champ_hit"], None, 1.5, -12),
    C + "w_heal": ([P + "DragonW_heal"], None, 1.2, -14),
    C + "e": ([P + "E_OnCast", P + "E_OnMissileLaunch"], None, 1.0, -13),
    C + "e_hit": ([P + "E_hitlocation", P + "E_hit"], None, 1.5, -12),
    C + "de": ([P + "EDragon_OnCast", P + "EDragon_OnMissileLaunch"], None, 1.2, -12),
    C + "de_hit": ([P + "EDragon_hitlocation"], None, 1.5, -12),
    C + "r": ([P + "DragonR_oncast", P + "DragonR_omc"], None, 2.0, -11),
    C + "r_hit": ([P + "DragonR_hit"], None, 1.5, -12),
    C + "tf": ([P + "DragonRTransform_buffactivate_loop"], None, 2.0, -12),
    C + "untf": ([P + "DragonR_untransform"], None, 1.5, -13),
    C + "full": ([P + "DragonR_ready_self"], None, 1.5, -14),
    C + "vo_q": ([V + "ShyvanaQAttack_cast3D"], None, 3.0, -6),
    C + "vo_q3": ([V + "Dragon_Attack2DGeneral", V + "ShyvanaQAttack2_cast3D"], None, 3.0, -6),
    C + "vo_e": ([V + "ShyvanaE_cast3D"], None, 3.0, -6),
    C + "vo_r": ([V + "ShyvanaR_cast3D", V + "Dragon_Taunt3DGeneral", V + "Dragon_Kill3DGeneral"], None, 4.0, -6),
}
I = "assets/characters/shyvana/hud/icons2d/shyvana_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_shyvana_skill": I + "q1.dds",
    "league_shyvana_skill2": I + "e.dds",
    "league_shyvana_ult": I + "r.dds",
    "league_shyvana_w": I + "w1.dds",
    "league_shyvana_passive": I + "passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Shyvana.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Shyvana.{args.lang}.wad.client"))
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
