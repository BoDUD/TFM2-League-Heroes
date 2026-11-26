r"""Supplement missing League champion spell-cast Chinese voices from a local LoL client.

    python -I tools/lol/extract_missing_spell_vo.py --wire
    python -I tools/lol/extract_missing_spell_vo.py --lol "D:\WeGameApps\lol" --vgmstream "C:\t\ks_tools\vgm\vgmstream-cli.exe"
    python -I tools/lol/extract_missing_spell_vo.py --lol "D:\WeGameApps\lol" --vgmstream "C:\t\ks_tools\vgm\vgmstream-cli.exe" --wire --install-mods "D:\steam\steamapps\common\Teamfight Manager2\mods\league"

Audited against all 173 League champions in league/champion/ and D:\WeGameApps\lol\Game\DATA\FINAL\Champions\*.zh_CN.wad.client:
these 41 active spell slots across 39 champions previously played SFX only (e.g. Ashe R, Ahri Q, Camille Q/W, Morgana W/E,
Ezreal Q, Ekko E, Darius W, Riven E, Lee Sin W, Lux W, Vayne Q, Twisted Fate Q, Master Yi E, Shaco E, Pyke W, Ryze W,
Samira W, Kayn E, Lucian W, Kai'Sa E, Evelynn Q, etc.) even though Riot's zh_CN voice bank has real cast voice events for them.

Wiring gives each VO clip a `.sound_info` of its own, `league_<slug>_<slot>_vo` (tools/kit/vo_gate.py), takes it out of
the spell's `.sound_info` if it is there, and registers its clip override in `league/mod.override_info`. The packers
(tools/package_mod.py, addons/league_addons/assemble.py) then play the line through tools/kit/vo_gate.py where the
spell's sound plays: at most once every 10 s per hero and spell, as the kits' own lines (2026-11-26: wired as one more
clip in the spell's `.sound_info` it was said at every cast - Ezreal's Q all match long). No `.data_champion` edits.
Actual audio binaries (.wav / .mp3) remain git-ignored (c) Riot Games.
"""
import argparse
import json
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_garen import decode, finish, lp  # noqa: E402
from riot import SoundBanks, Wad, parse_wpk  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MOD = os.path.join(ROOT, "league")
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
from vo_gate import voice_name  # noqa: E402  each line's own .sound_info

# (slug, wad_name, slot, target_sound_info, clip_name, candidate_events, volume, max_s, peak_db)
SPELLS = [
    ("ahri", "Ahri", "q", "league_ahri_q_cast", "league_ahri_sfx_vo_q",
     ["Play_vo_Ahri_AhriQ_cast3D", "Play_vo_Ahri_Spell3DQCast"], 0.9, 2.0, -4),
    ("ashe", "Ashe", "r", "league_ashe_r_cast", "league_ashe_sfx_vo_r",
     ["Play_vo_Ashe_Spell2DRCast"], 1.0, 2.5, -2),
    ("aurora", "Aurora", "w", "league_aurora_w", "league_aurora_sfx_vo_w",
     ["Play_vo_Aurora_AuroraW_cast3D"], 0.85, 2.2, -5),
    ("camille", "Camille", "q", "league_camille_q2_cast", "league_camille_sfx_vo_q",
     ["Play_vo_Camille_CamilleQAttackEmpowered_cast3D", "Play_vo_Camille_CamilleQ_cast3D"], 0.9, 2.8, -3),
    ("camille", "Camille", "w", "league_camille_w_cast", "league_camille_sfx_vo_w",
     ["Play_vo_Camille_Spell3DWCast"], 0.9, 2.8, -3),
    ("darius", "Darius", "w", "league_darius_w_hit", "league_darius_sfx_vo_w",
     ["Play_vo_Darius_DariusNoxianTacticsONHAttack_cast3D"], 0.95, 2.0, -3),
    ("ekko", "Ekko", "e", "league_ekko_e_cast", "league_ekko_sfx_vo_e",
     ["Play_vo_Ekko_EkkoE_cast3D", "Play_vo_Ekko_EkkoEAttack_cast3D"], 0.95, 2.0, -3),
    ("evelynn", "Evelynn", "q", "league_evelynn_q_cast", "league_evelynn_sfx_vo_q",
     ["Play_vo_Evelynn_EvelynnQ_cast3D", "Play_vo_Evelynn_Spell3DQCast"], 0.85, 1.8, -4),
    ("ezreal", "Ezreal", "q", "league_ezreal_q_cast", "league_ezreal_sfx_vo_q",
     ["Play_vo_Ezreal_EzrealQ_cast3D", "Play_vo_Ezreal_Spell3DQCast"], 0.95, 1.8, -3),
    ("heimerdinger", "Heimerdinger", "w", "league_heimerdinger_w", "league_heimerdinger_sfx_vo_w",
     ["Play_vo_Heimerdinger_HeimerdingerW_cast3D"], 0.85, 2.2, -5),
    ("hwei", "Hwei", "w", "league_hwei_w_ww", "league_hwei_sfx_vo_w",
     ["Play_vo_Hwei_HweiWW_cast3D", "Play_vo_Hwei_HweiWQ_cast3D"], 0.85, 2.2, -5),
    ("ivern", "Ivern", "w", "league_ivern_w", "league_ivern_sfx_vo_w",
     ["Play_vo_Ivern_IvernW_cast3D"], 0.85, 2.2, -5),
    ("jhin", "Jhin", "e", "league_jhin_e_throw", "league_jhin_sfx_vo_e",
     ["Play_vo_Jhin_Spell3DEHit"], 0.9, 3.8, -3),
    ("kaisa", "Kaisa", "e", "league_kaisa_e_cast", "league_kaisa_sfx_vo_e",
     ["Play_vo_Kaisa_KaisaEAttack_cast3D", "Play_vo_Kaisa_KaisaEAttack2_cast3D"], 0.9, 2.0, -3),
    ("kalista", "Kalista", "w", "league_kalista_w_hit", "league_kalista_sfx_vo_w",
     ["Play_vo_Kalista_KalistaW_cast3D"], 0.85, 2.2, -5),
    ("kayn", "Kayn", "e", "league_kayn_e_cast", "league_kayn_sfx_vo_e",
     ["Play_vo_Kayn_KaynE_cast3D"], 0.9, 2.2, -3),
    ("khazix", "Khazix", "w", "league_khazix_w_throw", "league_khazix_sfx_vo_w",
     ["Play_vo_Khazix_KhazixW_cast3D"], 0.85, 2.0, -4),
    ("leesin", "LeeSin", "w", "league_leesin_w_shield", "league_leesin_sfx_vo_w",
     ["Play_vo_LeeSin_Spell3DW1Cast", "Play_vo_LeeSin_LeeSinWTwo_cast3D"], 0.95, 1.8, -3),
    ("lucian", "Lucian", "w", "league_lucian_w_cast", "league_lucian_sfx_vo_w",
     ["Play_vo_Lucian_LucianW_cast3D"], 0.95, 2.0, -3),
    ("lux", "Lux", "w", "league_lux_w_shield", "league_lux_sfx_vo_w",
     ["Play_vo_Lux_LuxPrismaticWave_cast3D", "Play_vo_Lux_Spell3DWCast"], 0.95, 2.2, -3),
    ("masteryi", "MasterYi", "e", "league_masteryi_e_cast", "league_masteryi_sfx_vo_e",
     ["Play_vo_MasterYi_Spell3DECast"], 0.95, 2.0, -3),
    ("morgana", "Morgana", "w", "league_morgana_w_cast", "league_morgana_sfx_vo_w",
     ["Play_vo_Morgana_MorganaW_cast3D", "Play_vo_Morgana_Spell3DWCast"], 0.9, 2.2, -3),
    ("morgana", "Morgana", "e", "league_morgana_e_cast", "league_morgana_sfx_vo_e",
     ["Play_vo_Morgana_MorganaE_cast3D"], 0.9, 2.2, -3),
    # The shield event has one 10-second line. Use a short combat voice that fits the cast.
    ("nautilus", "Nautilus", "w", "league_nautilus_w", "league_nautilus_sfx_vo_w",
     ["Play_vo_Nautilus_NautilusBasicAttack_cast3D"], 0.85, 2.8, -5),
    ("pyke", "Pyke", "w", "league_pyke_w_cast", "league_pyke_sfx_vo_w",
     ["Play_vo_Pyke_PykeW_cast2D"], 0.85, 3.0, -4),
    ("qiyana", "Qiyana", "w", "league_qiyana_w_on", "league_qiyana_sfx_vo_w",
     ["Play_vo_Qiyana_QiyanaWMis_Rock_hit3D", "Play_vo_Qiyana_QiyanaWMis_Grass_hit3D"], 0.85, 2.9, -5),
    ("riven", "Riven", "e", "league_riven_e", "league_riven_sfx_vo_e",
     ["Play_vo_Riven_RivenFeint_cast3D"], 0.9, 1.8, -3),
    ("ryze", "Ryze", "w", "league_ryze_w_cast", "league_ryze_sfx_vo_w",
     ["Play_vo_Ryze_RyzeW_cast3D", "Play_vo_Ryze_Spell3DWCast"], 0.85, 2.2, -4),
    ("samira", "Samira", "w", "league_samira_w_cast", "league_samira_sfx_vo_w",
     ["Play_vo_Samira_SamiraW_cast3D"], 0.85, 2.0, -4),
    ("sett", "Sett", "q", "league_sett_q_hit", "league_sett_sfx_vo_q",
     ["Play_vo_Sett_SettQAttack_cast3D", "Play_vo_Sett_SettQAttack2_cast3D"], 0.9, 1.8, -3),
    ("shaco", "Shaco", "e", "league_shaco_e_throw", "league_shaco_sfx_vo_e",
     ["Play_vo_Shaco_Spell3DECast"], 0.9, 2.0, -3),
    ("skarner", "Skarner", "w", "league_skarner_w", "league_skarner_sfx_vo_w",
     ["Play_vo_Skarner_SkarnerW_cast3D"], 0.85, 2.9, -5),
    ("taliyah", "Taliyah", "e", "league_taliyah_e_land", "league_taliyah_sfx_vo_e",
     ["Play_vo_Taliyah_TaliyahE_cast3D"], 0.85, 2.2, -5),
    ("twistedfate", "TwistedFate", "q", "league_twistedfate_q_cast", "league_twistedfate_sfx_vo_q",
     ["Play_vo_TwistedFate_Spell3DQCast"], 0.9, 2.0, -3),
    ("udyr", "Udyr", "w", "league_udyr_w", "league_udyr_sfx_vo_w",
     ["Play_vo_Udyr_Spell3DW1Cast"], 0.85, 2.2, -5),
    ("urgot", "Urgot", "w", "league_urgot_w_on", "league_urgot_sfx_vo_w",
     ["Play_vo_Urgot_UrgotW_cast3D"], 0.85, 2.2, -5),
    ("vayne", "Vayne", "q", "league_vayne_q_cast", "league_vayne_sfx_vo_q",
     ["Play_vo_Vayne_Spell3DQCast"], 0.9, 1.8, -3),
    ("wukong", "MonkeyKing", "q", "league_wukong_q_swing", "league_wukong_sfx_vo_q",
     ["Play_vo_MonkeyKing_MonkeyKingQAttack_cast3D", "Play_vo_MonkeyKing_Spell3DQCast"], 0.85, 2.0, -4),
    ("yorick", "Yorick", "w", "league_yorick_w_wall", "league_yorick_sfx_vo_w",
     ["Play_vo_Yorick_YorickW_cast3D"], 0.85, 2.2, -5),
    ("yuumi", "Yuumi", "e", "league_yuumi_e_hit", "league_yuumi_sfx_vo_e",
     ["Play_vo_Yuumi_YuumiE_cast3D"], 0.85, 2.2, -5),
    ("zac", "Zac", "w", "league_zac_w", "league_zac_sfx_vo_w",
     ["Play_vo_Zac_ZacW_cast3D"], 0.85, 2.0, -5),
]


def pick_best_variant(variants, media, vgmstream):
    """Decode up to 12 variants and pick a clear, complete spoken line (prefer 0.9-2.8s over tiny grunts/long monologues)."""
    best = None
    best_score = -1e9
    for mid in variants[:12]:
        if mid not in media:
            continue
        sr, x = decode(media[mid], vgmstream)
        # Measure active speech duration (samples > 0.015)
        nz = np.nonzero(np.abs(x) > 0.015)[0]
        if len(nz) < int(0.12 * sr):
            continue
        dur = (nz[-1] - nz[0]) / sr
        rms = float(np.sqrt(np.mean(x[nz[0]:nz[-1] + 1] ** 2)))
        # Prefer 0.9-2.8s clear complete spoken lines; penalize <0.5s grunts and >3.5s monologues
        if 0.85 <= dur <= 2.8:
            score = 10.0 + min(dur, 1.9) + rms * 5.0
        elif dur < 0.85:
            score = dur * 8.0 + rms * 4.0
        else:
            score = 9.0 - (dur - 2.8) * 2.5 + rms * 4.0
        if score > best_score:
            best_score = score
            best = (mid, sr, x, dur)
    if best is None:
        mid = variants[0]
        sr, x = decode(media[mid], vgmstream)
        return mid, sr, x, len(x) / sr
    return best


def voice_sound_info(clip, vol):
    return {"plays": [{"delay": 0.0, "clip": clip, "volume": vol}]}


def wire_repo():
    ov_path = lp(os.path.join(MOD, "mod.override_info"))
    ov = json.loads(open(ov_path, encoding="utf-8-sig").read())
    wired = 0
    for slug, _wad, slot, target_si, clip, _evs, vol, _max_s, _peak in SPELLS:
        si_path = lp(os.path.join(MOD, "sound", "sfx", f"{target_si}.sound_info"))
        if not os.path.isfile(si_path):
            sys.exit(f"Missing target sound_info: {si_path}")
        if clip == target_si:
            sys.exit(f"Clip name must differ from sound_info: {clip}")
        # the spell's own .sound_info: its effect sounds only (the line used to be one more clip here)
        data = json.loads(open(si_path, encoding="utf-8-sig").read())
        plays = data.get("plays", [])
        if any(p.get("clip") == clip for p in plays):
            data["plays"] = [p for p in plays if p.get("clip") != clip]
            with open(si_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        # the line's own .sound_info, played through tools/kit/vo_gate.py
        vo_path = lp(os.path.join(MOD, "sound", "sfx", f"{voice_name(slug, slot)}.sound_info"))
        vo = voice_sound_info(clip, vol)
        old = json.loads(open(vo_path, encoding="utf-8-sig").read()) if os.path.isfile(vo_path) else None
        if old != vo:
            with open(vo_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(vo, indent=2, ensure_ascii=False) + "\n")
            wired += 1
        key = f"asset/base/sound/sfx/{clip}"
        if key not in ov:
            ov[key] = {"remapping": f"asset/league/sound/sfx/{clip}", "type": "override"}
    # Keep keys sorted stably as repo does? Preserve insertion / sort cleanly
    with open(ov_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(ov, indent=2, ensure_ascii=False) + "\n")
    print(f"Wired {len(SPELLS)} spell VOs ({wired} line .sound_info files written) + mod.override_info")


def extract_all(lol_dir, vgmstream, lang="zh_CN", install_mods=None):
    import soundfile as sf

    champs = os.path.join(lol_dir, "Game", "DATA", "FINAL", "Champions")
    out_dir = os.path.join(MOD, "sound", "sfx")
    os.makedirs(lp(out_dir), exist_ok=True)

    cache = {}
    extracted = []
    for slug, wad_name, slot, target_si, clip, events, vol, max_s, peak in SPELLS:
        if wad_name not in cache:
            vo_wad = Wad(os.path.join(champs, f"{wad_name}.{lang}.wad.client"))
            b = wad_name.lower()
            vo_bank = f"assets/sounds/wwise2016/vo/en_us/characters/{b}/skins/base/{b}_base_vo_"
            media = parse_wpk(vo_wad.read_path(vo_bank + "audio.wpk"))
            banks = SoundBanks([vo_wad.read_path(vo_bank + "events.bnk")], media)
            cache[wad_name] = (media, banks)
        media, banks = cache[wad_name]

        event, variants = None, []
        for ev in events:
            variants = banks.event_media(ev)
            if variants:
                event = ev
                break
        if not variants:
            sys.exit(f"{clip}: none of {events} resolved in {wad_name}.{lang}.wad.client")

        mid, sr, x, raw_dur = pick_best_variant(variants, media, vgmstream)
        pcm = finish(x, sr, max_s, peak)
        wav_path = lp(os.path.join(out_dir, clip + ".wav"))
        with wave.open(wav_path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())
        extracted.append((clip, target_si, sr, pcm, event, mid, len(variants)))
        print(f"  {clip:32s} {len(pcm)/sr:4.2f}s (raw {raw_dur:4.2f}s) <- {event} [{mid}] ({len(variants)} vars)")

    if install_mods:
        bgm_dir = os.path.join(install_mods, "sound", "bgm")
        sfx_dir = os.path.join(install_mods, "sound", "sfx")
        os.makedirs(lp(bgm_dir), exist_ok=True)
        ov_path = lp(os.path.join(install_mods, "mod.override_info"))
        ov = json.loads(open(ov_path, encoding="utf-8-sig").read())
        voice_of = {s[4]: voice_name(s[0], s[2]) for s in SPELLS}
        for clip, target_si, sr, pcm, _ev, _mid, _n in extracted:
            mp3_path = lp(os.path.join(bgm_dir, clip + ".mp3"))
            sf.write(mp3_path, pcm.astype(np.float32) / 32768.0, sr, format="MP3")
            # Copy the updated minified .sound_info files: the spell's and the line's own (the installed .data_champion
            # plays the line only when it was packed by tools/package_mod.py, which runs tools/kit/vo_gate.py)
            for si in (target_si, voice_of[clip]):
                src_si = json.loads(open(lp(os.path.join(MOD, "sound", "sfx", f"{si}.sound_info")), encoding="utf-8-sig").read())
                with open(lp(os.path.join(sfx_dir, f"{si}.sound_info")), "w", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps(src_si, separators=(",", ":"), ensure_ascii=False))
            ov[f"asset/base/sound/sfx/{clip}"] = {"remapping": f"asset/league/sound/bgm/{clip}", "type": "override"}
        with open(ov_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(ov, separators=(",", ":"), ensure_ascii=False))
        print(f"Installed {len(extracted)} streamed MP3s + .sound_info + mod.override_info -> {install_mods}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wire", action="store_true", help="update league/sound/sfx/*.sound_info and league/mod.override_info")
    ap.add_argument("--lol", help="League of Legends install folder (contains Game/)")
    ap.add_argument("--lang", default="zh_CN")
    ap.add_argument("--vgmstream", help="path to vgmstream-cli.exe")
    ap.add_argument("--install-mods", help="also encode MP3s & sync .sound_info into an installed mods/league directory")
    args = ap.parse_args()
    if args.wire:
        wire_repo()
    if args.lol and args.vgmstream:
        extract_all(args.lol, args.vgmstream, args.lang, args.install_mods)
    elif not args.wire:
        ap.error("specify --wire and/or --lol + --vgmstream")


if __name__ == "__main__":
    main()
