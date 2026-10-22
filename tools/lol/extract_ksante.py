r"""Pull K'Sante's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_ksante.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_neeko.py: reads (never writes) Game/DATA/FINAL/Champions/KSante.wad.client and
KSante.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event),
decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored: audio (c) Riot Games) plus
64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Events (named in the base skin's bin, CommunityDragon skins/skin0.bin): KSanteBasicAttack_OnCast / OnHit (the attack),
KSanteBasicAttack3_OnCast (an All Out swing), KSantePAttack_OnHit (the marked attack), KSanteQ1_cast / Q_hitlocation,
KSanteQ3_cast / Q3_hitlocation, KSanteW_OnCast (the brace) / W_dash_cast / W_dash_hit (the ram's landing),
KSanteCritAttack_OnHit (a rammed champion), KSanteR_cast / R_OnHitLocation (the bash) / RKnockback_dash_cast (the
chase) / RKnockback_wall_exit_groundslam_hit (the slam), KSanteRTransform_OnBuffActivate (All Out). Voice
(Play_vo_KSante_): KSanteQ_cast3D, KSanteQ3_cast3D, Spell3DWCast, KSanteR_cast3D.
Icons (KSante.bin's): Icons_KSante_Q1 = skill, Icons_KSante_W = skill2, Icons_KSante_R1 = ult, Icons_KSante_E = E,
Icons_KSante_P = passive.
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/ksante/skins/base/ksante_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/ksante/skins/base/ksante_base_vo_"  # same in every language
P = "Play_sfx_KSante_"
V = "Play_vo_KSante_"
C = "league_ksante_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "KSanteBasicAttack_OnCast"], None, 0.8, -16),
    C + "a_hit": ([P + "KSanteBasicAttack_OnHit"], None, 0.8, -15),
    C + "ao_a": ([P + "KSanteBasicAttack3_OnCast", P + "KSanteBasicAttack4_OnCast"], None, 0.9, -15),
    C + "p_hit": ([P + "KSantePAttack_OnHit"], None, 1.0, -13),
    C + "q": ([P + "KSanteQ1_cast", P + "KSanteQ2_cast"], None, 1.0, -14),
    C + "q_hit": ([P + "KSanteQ_hitlocation"], None, 0.8, -16),
    C + "q3": ([P + "KSanteQ3_cast", P + "KSanteQ3Missile_OnMissileCast"], None, 1.4, -12),
    C + "q3_hit": ([P + "KSanteQ3_hitlocation", P + "KSanteQ3_hitlocationJ"], None, 1.0, -14),
    C + "w": ([P + "KSanteW_OnCast", P + "KSanteW_charging_stun_block_buffactivate"], None, 1.2, -14),
    C + "w_dash": ([P + "KSanteW_dash_cast"], None, 1.0, -14),
    C + "w_land": ([P + "KSanteW_dash_hit"], None, 1.2, -12),
    C + "w_hit": ([P + "KSanteCritAttack_OnHit"], None, 0.8, -15),
    C + "r": ([P + "KSanteR_cast"], None, 1.4, -13),
    C + "r_hit": ([P + "KSanteR_OnHitLocation8", P + "KSanteRKnockback_wall_explosion1"], None, 1.2, -12),
    C + "r_dash": ([P + "KSanteRKnockback_dash_cast"], None, 1.0, -14),
    C + "r_slam": ([P + "KSanteRKnockback_wall_exit_groundslam_hit"], None, 1.6, -11),
    C + "ao_on": ([P + "KSanteRTransform_OnBuffActivate1"], None, 1.8, -12),
    C + "vo_q": ([V + "KSanteQ_cast3D"], None, 2.0, -6),
    C + "vo_q3": ([V + "KSanteQ3_cast3D"], None, 2.0, -6),
    C + "vo_w": ([V + "Spell3DWCast"], None, 2.0, -6),
    C + "vo_r": ([V + "KSanteR_cast3D"], None, 2.4, -6),
}
I = "assets/characters/ksante/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_ksante_skill": I + "icons_ksante_q1.dds",
    "league_ksante_skill2": I + "icons_ksante_w.dds",
    "league_ksante_ult": I + "icons_ksante_r1.dds",
    "league_ksante_e": I + "icons_ksante_e.dds",
    "league_ksante_passive": I + "icons_ksante_p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "KSante.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"KSante.{args.lang}.wad.client"))
        sfx_audio = main_wad.read_path(SFX_BANK + "audio.bnk")
        media = dict(bnk_media(sfx_audio))
        media.update(parse_wpk(vo_wad.read_path(VO_BANK + "audio.wpk")))
        banks = SoundBanks([main_wad.read_path(SFX_BANK + "events.bnk"), sfx_audio,
                            vo_wad.read_path(VO_BANK + "events.bnk")], media)
        out_dir = os.path.join(MOD, "sound", "sfx")
        os.makedirs(lp(out_dir), exist_ok=True)
        for name, (events, mid, max_s, peak) in CLIPS.items():
            event, variants = None, []
            # (the bins' names can carry a glued character - "OnBuffActivate1", "OnHitLocation8": also try them without it)
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
