r"""Pull Cassiopeia's sounds and ability icons out of a local League of Legends install.

    python tools/lol/extract_cassiopeia.py --lol "D:\WeGameApps\lol" --vgmstream path\to\vgmstream-cli.exe

Same route as extract_wukong.py: reads (never writes) Game/DATA/FINAL/Champions/Cassiopeia.wad.client and
Cassiopeia.<lang>.wad.client, resolves the base-skin Wwise events below to their media (the first variant of each event
unless a media id is given), decodes them with vgmstream and writes mono 16-bit WAVs to league/sound/sfx/ (git-ignored:
audio (c) Riot Games) plus 64x64 ability icons to league/icons/. Without --vgmstream only the icons are written.
Voice: zh_CN. Events (prefix Play_sfx_Cassiopeia_Cassiopeia, named in the champion's bins): E_OnCast / E_OnHit (Twin
Fang - her attack here), Q_OnCast / Q_hit / Q_hit_champ (Noxious Blast), W_OnCast / W_hit (Miasma), R_OnCast /
RStun_OnBuffActivate (Petrifying Gaze and the petrified). Voice (Play_vo_Cassiopeia_): the spells' cast3D lines.
Icons: cassiopeia_q = skill (Q), cassiopeia_w = skill2 (W), cassiopeia_r = ult; cassiopeia_e and cassiopeia_passive too
(league_cassiopeia_e, _passive, for the README).
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
SFX_BANK = "assets/sounds/wwise2016/sfx/characters/cassiopeia/skins/base/cassiopeia_base_sfx_"
VO_BANK = "assets/sounds/wwise2016/vo/en_us/characters/cassiopeia/skins/base/cassiopeia_base_vo_"  # same in every language
P = "Play_sfx_Cassiopeia_Cassiopeia"
V = "Play_vo_Cassiopeia_"
C = "league_cassiopeia_sfx_"

# clip name -> ([events to try, first that resolves], media id among the event's variants or None for the first,
# max seconds, peak dBFS)
CLIPS = {
    C + "a": ([P + "E_OnCast", P + "E_OnMissileLaunch"], None, 0.6, -16),
    C + "a_hit": ([P + "E_OnHit"], None, 0.8, -15),
    C + "q": ([P + "Q_OnCast"], None, 0.8, -14),
    C + "q_blast": ([P + "Q_hit", P + "Q_hit5"], None, 1.2, -12),
    C + "q_hit": ([P + "Q_hit_champ"], None, 0.8, -15),
    C + "w": ([P + "W_OnCast"], None, 1.0, -13),
    C + "w_land": ([P + "W_hit"], None, 1.2, -13),
    C + "r": ([P + "R_OnCast", P + "R_OnCast2"], None, 1.6, -11),
    C + "r_hit": ([P + "RStun_OnBuffActivate", P + "RStun_OnBuffActivate4"], None, 1.0, -12),
    C + "vo_q": ([V + "CassiopeiaQ_cast3D"], None, 2.0, -6),
    C + "vo_w": ([V + "CassiopeiaW_cast3D"], None, 2.0, -6),
    C + "vo_r": ([V + "CassiopeiaR_cast3D"], None, 2.5, -6),
}
I = "assets/characters/cassiopeia/hud/icons2d/"
ICONS = {  # TFM2 slot -> Riot icon
    "league_cassiopeia_skill": I + "cassiopeia_q.dds",
    "league_cassiopeia_skill2": I + "cassiopeia_w.dds",
    "league_cassiopeia_ult": I + "cassiopeia_r.dds",
    "league_cassiopeia_e": I + "cassiopeia_e.dds",
    "league_cassiopeia_passive": I + "cassiopeia_passive.dds",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", required=True, help="League of Legends folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="vgmstream-cli.exe; without it only the icons are written")
    args = ap.parse_args()
    champs = os.path.join(args.lol, "Game", "DATA", "FINAL", "Champions")
    main_wad = Wad(os.path.join(champs, "Cassiopeia.wad.client"))

    if args.vgmstream:
        vo_wad = Wad(os.path.join(champs, f"Cassiopeia.{args.lang}.wad.client"))
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
