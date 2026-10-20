r"""Pull Sylas's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_sylas.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

The Volibear route (extract_volibear.py): reads (never writes) Game/DATA/FINAL/Champions/Sylas.wad.client and
Sylas.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (named in the champion's bins, prefix Play_sfx_Sylas_Sylas): BasicAttack_OnCast / _OnHit (the
chain swing), PassiveAttack_OnCast / _OnHit (Petricite Burst's whirl), W_OnCast / W_hit (Kingslayer), Q_OnCast / Q1_hit /
Q2_hit (Chain Lash: the lash, the burst), E_OnCast (Abscond), E2_OnMissileCast / E2_hit (Abduct), R_OnCast / R_hit
(Hijack's chain and the steal), R2_cast / RCosmeticMissile_OnHit2 (the stolen ult). Voice (Play_vo_Sylas_Sylas):
Q_cast3D, W_cast3D, E_cast3D, R_hit3D, R2_cast.
Icons: SylasQ = skill (Chain Lash), SylasE = skill2 (Abscond / Abduct), SylasR = ult (Hijack), SylasW (Kingslayer, in
the attack: league_sylas_w) and SylasP (league_sylas_passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/sylas/skins/base/sylas_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/sylas/skins/base/sylas_base_vo_"  # same in every language
P = "Play_sfx_Sylas_Sylas"
V = "Play_vo_Sylas_Sylas"
C = "league_sylas_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "BasicAttack_OnCast"], None, 0.8, -14),
    C + "a_hit": ([P + "BasicAttack_OnHit"], None, 0.8, -15),
    C + "p": ([P + "PassiveAttack_OnCast"], None, 1.0, -13),
    C + "p_hit": ([P + "PassiveAttack_OnHit"], None, 1.0, -14),
    C + "w": ([P + "W_OnCast"], None, 1.2, -13),
    C + "w_hit": ([P + "W_hit"], None, 1.2, -12),
    C + "q": ([P + "Q_OnCast"], None, 1.2, -13),
    C + "q_hit": ([P + "Q1_hit"], None, 1.0, -14),
    C + "q_boom": ([P + "Q2_hit", P + "Q2_cast"], None, 1.5, -11),
    C + "e": ([P + "E_OnCast"], None, 1.0, -13),
    C + "e2": ([P + "E2_OnMissileCast", P + "E2_OnCast"], None, 1.2, -13),
    C + "e_hit": ([P + "E2_hit", P + "E2_hittarget"], None, 1.2, -12),
    C + "r": ([P + "R_OnCast", P + "R_OnMissileCast"], None, 1.5, -12),
    C + "r_steal": ([P + "R_hit"], None, 2.0, -11),
    C + "r2": ([P + "R2_cast", P + "R2_self_cast"], None, 2.0, -11),
    C + "r2_boom": ([P + "RCosmeticMissile_OnHit2", P + "RCosmeticMissile_OnHit"], None, 2.0, -11),
    C + "vo_q": ([V + "Q_cast3D"], None, 3.0, -6),
    C + "vo_w": ([V + "W_cast3D"], None, 3.0, -6),
    C + "vo_e": ([V + "E_cast3D"], None, 3.0, -6),
    C + "vo_r": ([V + "R_hit3D"], None, 4.0, -6),
    C + "vo_r2": ([V + "R2_cast"], None, 4.0, -6),
}
I = "assets/characters/sylas/hud/icons2d/sylas"
ICONS = {  # TFM2 slot -> Riot icon
    "league_sylas_skill": I + "q.dds",
    "league_sylas_skill2": I + "e.dds",
    "league_sylas_ult": I + "r.dds",
    "league_sylas_w": I + "w.dds",
    "league_sylas_passive": I + "p.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Sylas.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Sylas.{args.lang}.wad.client"))
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
