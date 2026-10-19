r"""Pull Cho'Gath's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_chogath.py --lol "D:\WeGameApps\lol" --vgmstream path	ogmstream-cli.exe

The Volibear route (extract_volibear.py): reads (never writes) Game/DATA/FINAL/Champions/Chogath.wad.client and
Chogath.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a variant is named), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (named in the champion's bin, prefix Play_sfx_Chogath_): ChogathBasicAttack_OnCast / OnHit,
ChogathCritAttack_OnCast / OnHit, ChogathEAttack_OnCast, VorpalSpikesMissle_OnMissileLaunch / _hit3 / VorpalSpikes_
buffactivate / _OnBuffDeactivate (Vorpal Spikes), Rupture_OnCast / _cast2 (Rupture), FeralScream_OnCast / _hit (Feral
Scream), Feast_OnHit (Feast); the bin's Rupture_cast1 / _cast2q / *_Cast_Anim and Taunt3DGeneralK resolve to nothing.
League gives him no spell lines - his voice (Play_vo_Chogath_) is Attack2DGeneral (three of its seven variants) and
Laugh3DGeneral, used for the spells' lines.
Icons (the bin's old names): GreenTerror_SpikeSlam = skill (Rupture), _FeralScream = skill2, _Feast = ult; _ChitinousExoplates
(drawn as Vorpal Spikes' flying spikes) and _TailSpike (his face: Carnivore) too (league_chogath_e, _passive).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/chogath/skins/base/chogath_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/chogath/skins/base/chogath_base_vo_"  # same in every language
P = "Play_sfx_Chogath_"
V = "Play_vo_Chogath_"
C = "league_chogath_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a_swing": ([P + "ChogathBasicAttack_OnCast"], None, 0.8, -16),
    C + "a_hit": ([P + "ChogathBasicAttack_OnHit"], None, 0.8, -15),
    C + "p_heal": ([P + "VorpalSpikes_OnBuffDeactivate"], None, 0.8, -16),
    C + "e_spikes": ([P + "VorpalSpikesMissle_OnMissileLaunch"], None, 1.0, -13),
    C + "e_hit": ([P + "VorpalSpikesMissle_hit3"], None, 0.8, -14),
    C + "q": ([P + "ChogathCritAttack_OnCast"], None, 1.0, -14),
    C + "q_crack": ([P + "Rupture_OnCast"], None, 1.2, -13),
    C + "q_burst": ([P + "Rupture_cast2"], None, 1.5, -11),
    C + "q_hit": ([P + "Rupture_cast2"], 1, 1.0, -13),
    C + "w": ([P + "FeralScream_OnCast"], None, 1.8, -11),
    C + "w_hit": ([P + "FeralScream_hit"], None, 1.0, -13),
    C + "r": (["Play_sfx_ChogathEAttack_OnCast"], None, 1.5, -12),
    C + "r_bite": ([P + "Feast_OnHit"], None, 1.5, -10),
    C + "r_hit": ([P + "ChogathCritAttack_OnHit"], None, 1.0, -12),
    C + "r_grow": ([P + "VorpalSpikes_buffactivate"], None, 1.2, -12),
    C + "vo_q": ([V + "Attack2DGeneral"], None, 2.5, -6),
    C + "vo_w": ([V + "Attack2DGeneral"], 2, 2.5, -6),
    C + "vo_e": ([V + "Attack2DGeneral"], 1, 2.5, -6),
    C + "vo_r": ([V + "Laugh3DGeneral"], None, 3.0, -6),
}
I = "assets/characters/chogath/hud/icons2d/greenterror_"
ICONS = {  # TFM2 slot -> Riot icon
    "league_chogath_skill": I + "spikeslam.dds",
    "league_chogath_skill2": I + "feralscream.dds",
    "league_chogath_ult": I + "feast.dds",
    "league_chogath_e": I + "chitinousexoplates.dds",
    "league_chogath_passive": I + "tailspike.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Chogath.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Chogath.{args.lang}.wad.client"))
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
