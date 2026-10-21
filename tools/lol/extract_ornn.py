r"""Pull Ornn's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_ornn.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Volibear route (extract_volibear.py): reads (never writes) Game/DATA/FINAL/Champions/Ornn.wad.client and
Ornn.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (named in the champion's bin, prefix Play_sfx_Ornn_Ornn): BasicAttack_OnCast / _OnHit (the hammer),
VulnerableDebuff_OnBuffActivate / _buffdeactivate (Brittle on, broken), W_OnCast / W_hit (Bellows Breath),
Q_OnCast / Q_OnMissileLaunch / Q_OnHitLocation / Q_SpellOnMissileEnd / Q_pillar_break (Volcanic Rupture and its pillar),
E_OnCast / E_BuffOnMoveEnd_explosion / EKnockUp_OnBuffActivate (Searing Charge, the quake),
R_cast / RWave_OnMissileLaunch1 (the ram's run) / RWave_OnHit / RCharge_OnCast / R_redirect_hit / RWave2_OnMissileLaunch
(the headbutt and the second run). Voice (Play_vo_Ornn_): OrnnQ_cast3D, OrnnE_cast3D, Attack2DGeneral (R1: no R line in
the bank), OrnnRCharge_cast3D (R2), OrnnBasicAttack2_cast3D (W: no W line).
Icons: OrnnQ = skill (Volcanic Rupture), OrnnE = skill2 (Searing Charge), OrnnR1 = ult (Call of the Forge God), OrnnW
(Bellows Breath, in the attack: league_ornn_w), OrnnR2 (the recast: league_ornn_r2) and OrnnP (league_ornn_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/ornn/skins/base/ornn_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/ornn/skins/base/ornn_base_vo_"  # same in every language
P = "Play_sfx_Ornn_Ornn"
V = "Play_vo_Ornn_"
C = "league_ornn_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast", P + "BasicAttack2_OnCast"], None, 0.9, -13),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.7, -14),
    C + "br": ([P + "VulnerableDebuff_OnBuffActivate"], None, 0.8, -16),
    C + "br_pop": ([P + "VulnerableDebuff_buffdeactivate"], None, 1.0, -12),
    C + "w": ([P + "W_OnCast"], None, 1.5, -12),
    C + "w_hit": ([P + "W_hit"], None, 0.6, -18),
    C + "q": ([P + "Q_OnCast"], None, 1.0, -13),
    C + "q_crack": ([P + "Q_OnMissileLaunch"], None, 1.2, -12),
    C + "q_hit": ([P + "Q_OnHitLocation"], None, 0.8, -15),
    C + "q_pillar": ([P + "Q_SpellOnMissileEnd"], None, 1.5, -11),
    C + "q_break": ([P + "Q_pillar_break"], None, 1.5, -11),
    C + "e": ([P + "E_OnCast"], None, 1.0, -12),
    C + "e_hit": ([P + "E_BuffOnMoveEnd_explosion"], None, 1.0, -12),
    C + "e_up": ([P + "EKnockUp_OnBuffActivate"], None, 1.0, -12),
    C + "r": ([P + "R_cast"], None, 1.5, -11),
    C + "r_run": ([P + "RWave_OnMissileCast", P + "RWave_OnMissileLaunch1"], None, 2.5, -11),
    C + "r_hit": ([P + "RWave_OnHit"], None, 0.8, -14),
    C + "r2": ([P + "RCharge_OnCast"], None, 1.0, -12),
    C + "r2_butt": ([P + "R_redirect_hit"], None, 1.2, -10),
    C + "r2_run": ([P + "RWave2_OnMissileLaunch"], None, 2.0, -11),
    C + "vo_q": ([V + "OrnnQ_cast3D"], None, 3.0, -6),
    C + "vo_w": ([V + "OrnnBasicAttack2_cast3D"], None, 3.0, -6),
    C + "vo_e": ([V + "OrnnE_cast3D"], None, 3.0, -6),
    C + "vo_r": ([V + "Attack2DGeneral"], None, 4.0, -6),
    C + "vo_r2": ([V + "OrnnRCharge_cast3D"], None, 4.0, -6),
}
I = "assets/characters/ornn/hud/icons2d/ornn"
ICONS = {  # TFM2 slot -> Riot icon
    "league_ornn_skill": I + "q.dds",
    "league_ornn_skill2": I + "e.dds",
    "league_ornn_ult": I + "r1.dds",
    "league_ornn_w": I + "w.dds",
    "league_ornn_r2": I + "r2.dds",
    "league_ornn_passive": I + "p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Ornn.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Ornn.{args.lang}.wad.client"))
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
