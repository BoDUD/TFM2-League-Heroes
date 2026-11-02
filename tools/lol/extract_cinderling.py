r"""Pull the Cinderling's sounds (绯红树怪) out of the local League of Legends install (the Riot client).

    python tools/lol/extract_cinderling.py --riot "D:\Riot Games\League of Legends" --vgmstream path\vgmstream-cli.exe

Its own sounds (the user: 「音效什么都要自己找」). Set 18 (DA_Cinderling18) names no event and the client ships no set-18
bank; its skin bin borrows the Rift's SRU_RedMini, and unlike the Blue camp's silent minis the Red camp's little ones
have a real voice: Map11's NPC_Map11_RedMini_SFX banks (18 clips). Named by guessing their hashes (2026-11-02):
SRU_RedMiniBasicAttack_OnCast (4 lunging growls ~1.7 s) / _OnHit (3 bites ~1.15 s), Aggro_buffactivate (a 4.45 s cry,
loudest at 2.2 s), Aggro2_buffactivate (2.4 s), Idle1_buffactivate (1.3 s), Death_cast (1.85 s), Death2_cast (1.3 s).
Its Scarlet Buff stack is the Red Brambleback's own buff pickup (Map11 NPC_Map11_Red_SFX n2a_buffactivate).
The rest is League's leaves, fire and burrowing, Champions/<name>.wad.client: Zyra's seeds and Deadly Spines (the ember
leaf, 刃叶), Brand's burning hit (the burn) and Pyroclasm (燎原叶暴's burning leaves), Rek'Sai's burrow and unburrow
(钻土突袭).
Read, never written; the bank's Wwise events resolved to their media (the first variant unless picked), decoded with
vgmstream and written as mono 16-bit WAVs to tft/sound/sfx/ (git-ignored: audio (c) Riot Games).
"""
import argparse
import os
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_garen import decode, finish, lp  # noqa: E402
from riot import SoundBanks, Wad, bnk_media, parse_wpk  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
MOD = os.path.join(ROOT, "tft")
C = "tft_cinderling_sfx_"
M = "play_sfx_sru_redmini_"
Z, B, R = "Play_sfx_Zyra_", "Play_sfx_Brand_Brand", "Play_sfx_Reksai_"

# clip name -> (source, [events to try, first that resolves], max seconds, peak dBFS[, variant, else the first])
CLIPS = {
    C + "a": ("Zyra", [Z + "ZyraBasicAttack_OnCast", Z + "ZyraBasicAttack_OnMissileLaunch"], 0.7, -13),   # the ember leaf
    C + "a_hit": ("Zyra", [Z + "ZyraBasicAttack_OnHit"], 0.6, -13),
    C + "p": ("red", ["Play_sfx_SRU_Red_n2a_buffactivate"], 1.2, -12),               # Scarlet Buff: a stack
    C + "p_burn": ("Brand", [B + "BasicAttack_OnHit"], 0.5, -14),                     # full stacks: attacks burn
    C + "q": ("Zyra", [Z + "ZyraQ_OnCast"], 1.0, -11),                                 # 刃叶: the leaves rise
    C + "q_vo": ("redmini", [M + "aggro2_buffactivate"], 1.2, -9),                    # its cry
    C + "q_hit": ("Zyra", [Z + "ZyraQ_hit", Z + "ZyraCritAttack_OnHit"], 0.9, -11),
    C + "q_burn": ("Brand", [B + "W_hit"], 1.0, -12),                                 # wound + burn on the target
    C + "e": ("Reksai", [R + "ReksaiW_buffactivate"], 1.2, -11),                      # 钻土突袭: digs in
    C + "e_out": ("Reksai", [R + "ReksaiW_hit"], 1.2, -10),                           # bursts out
    C + "e_vo": ("redmini", [M + "idle1_buffactivate"], 1.3, -10),
    C + "r": ("Brand", [B + "R_OnCast"], 1.4, -9),                                    # 燎原叶暴: the mane catches fire
    C + "r_vo": ("redmini", [M + "aggro_buffactivate"], 2.2, -7),
    C + "r_shot": ("Zyra", [Z + "ZyraE_OnCast", Z + "ZyraE_OnMissileLaunch"], 0.6, -14),
    C + "r_hit": ("Brand", [B + "R_hit"], 0.6, -12),
    C + "d": ("redmini", [M + "death_cast"], 1.9, -8),
}
MAP11 = "assets/sounds/wwise2016/sfx/shared/npc_map11_{}_sfx_"


def banks_of(src, a, cache):
    """A source's sfx banks (events + audio), read once: redmini / red = Map11's Red camp, else a champion's base skin."""
    if src in cache:
        return cache[src]
    if src in ("redmini", "red"):
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Maps", "Shipping", "Map11.wad.client"))
        stem = MAP11.format(src)
    else:
        w = Wad(os.path.join(a.riot, "Game", "DATA", "FINAL", "Champions", f"{src}.wad.client"))
        stem = f"assets/sounds/wwise2016/sfx/characters/{src.lower()}/skins/base/{src.lower()}_base_sfx_"
    audio = w.read_path(stem + "audio.bnk")
    media = dict(bnk_media(audio))
    if w.has(stem + "audio.wpk"):
        media.update(parse_wpk(w.read_path(stem + "audio.wpk")))
    cache[src] = SoundBanks([w.read_path(stem + "events.bnk"), audio], media)
    return cache[src]


def variants_of(banks, ev):
    """An event's media, by its name or (unnamed) its event id."""
    if isinstance(ev, int):
        return [m for m in dict.fromkeys(banks._resolve(ev, set())) if m in banks.media]
    return banks.event_media(ev)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--riot", required=True, help="the Riot client's League of Legends folder (Map11 and the champions)")
    ap.add_argument("--vgmstream", required=True, help="vgmstream-cli.exe")
    a = ap.parse_args()
    out_dir = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out_dir), exist_ok=True)
    cache = {}
    for name, (src, events, max_s, peak, *pick) in CLIPS.items():
        banks = banks_of(src, a, cache)
        event, variants = None, []
        for ev in events:
            variants = variants_of(banks, ev)
            if variants:
                event = ev
                break
        if not variants:
            sys.exit(f"{name}: none of {events} resolves in {src} - game patch changed the bank?")
        sr, x = decode(banks.media[variants[pick[0] if pick else 0]], a.vgmstream)
        pcm = finish(x, sr, max_s, peak)
        with wave.open(lp(os.path.join(out_dir, name + ".wav")), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())
        print(f"{name:28s} {len(pcm) / sr:4.2f}s  <- {src} {event} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
