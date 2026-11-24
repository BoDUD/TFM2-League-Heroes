#!/usr/bin/env python3
"""Generate Abyss Pact (渊契) shared pack files:
- abysspact/text/champion.i18n (5 languages, strictly checked against TOOLTIP_MAX)
- abysspact/style/champion_view.champion_view
- abysspact/sound/sfx/*.sound_info (100% verified against .data_champion + addons/abysspact/src/*.rs)
- abysspact/mod.mod_info
- abysspact/mod.override_info (text, champion_view, skeleton unit sheet/anim, all sounds & clips)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
MOD_ID = "abysspact"
MOD = os.path.join(REPO, MOD_ID)
VERSION = "0.3.0"
NAME = "Abyss Pact · 渊契"

sys.path.insert(0, HERE)
import build_abysspact as B  # noqa: E402

TOOLTIP_MAX = {"zh-hans": 130, "zh-hant": 130, "en": 334, "ja": 147, "ko": 185}
ADi = "<i#asset/base/ui/banpick/champion_stat_icon:ad_0>"
APi = "<i#asset/base/ui/banpick/champion_stat_icon:ap_0>"
O = "<#ff9028ff>"
A = "<#ffb900ff>"
R = "<#ef5350ff>"
M = "<#a974ffff>"
S = "<#e8d44dff>"
E = "<>"


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def save(path, data):
    os.makedirs(os.path.dirname(lp(path)), exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", "\r\n") + "\r\n"
    with open(lp(path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def shown_length(s):
    s = re.sub(r"\{\w+\}", "000", s)
    s = re.sub(r"<i#[^>]*>", "*", s)
    return len(re.sub(r"<[^>]*>", "", s))


def secs(t):
    return f"{t / 60:.2f}".rstrip("0").rstrip(".")


def ad(d, r):
    return f"{O}{d}{E}+{ADi}{O}{r}%{E}"


def ap(d, r):
    return f"{M}{d}{E}+{APi}{M}{r}%{E}"


# ---------------------------------------------------------------------------
# Sound event -> [(clip_basename, volume, delay)] mapping (never self-named!)
# ---------------------------------------------------------------------------
SOUNDS = {
    "abysspact_oathbreaker": {
        "a":          [("abysspact_oathbreaker_sfx_attack_swing", 0.45, 0.0)],
        "a_hit":      [("abysspact_oathbreaker_sfx_attack_hit", 0.50, 0.0)],
        "q_cast":     [("abysspact_oathbreaker_sfx_cleave_cast", 0.55, 0.0)],
        "q_hit":      [("abysspact_oathbreaker_sfx_cleave_hit", 0.55, 0.0)],
        "w_cast":     [("abysspact_oathbreaker_sfx_chain_release", 0.55, 0.0)],
        "w_pull":     [("abysspact_oathbreaker_sfx_chain_pull", 0.60, 0.0)],
        "r_plant":    [("abysspact_oathbreaker_sfx_ult_plant", 0.65, 0.0)],
        "r_erupt":    [("abysspact_oathbreaker_sfx_ult_eruption", 0.70, 0.0)],
        "oath_pulse": [("abysspact_oathbreaker_sfx_oath_pulse", 0.55, 0.0)],
        "v_start":    [("abysspact_oathbreaker_vo_start", 0.85, 0.0)],
        "v_ult":      [("abysspact_oathbreaker_vo_ult", 0.90, 0.0)],
        "v_kill":     [("abysspact_oathbreaker_vo_kill", 0.85, 0.0)],
        "v_respawn":  [("abysspact_oathbreaker_vo_respawn", 0.85, 0.0)],
        "v_dead":     [("abysspact_oathbreaker_vo_dead", 0.85, 0.0),
                       ("abysspact_oathbreaker_sfx_death_armor", 0.55, 0.1)],
    },
    "abysspact_faceless": {
        "a":           [("abysspact_faceless_sfx_attack_cross", 0.45, 0.0)],
        "a_hit":       [("abysspact_faceless_sfx_attack_hit", 0.50, 0.0)],
        "q_dash":      [("abysspact_faceless_sfx_dash_out", 0.55, 0.0)],
        "q_pass":      [("abysspact_faceless_sfx_dash_pass", 0.55, 0.0)],
        "w_hide":      [("abysspact_faceless_sfx_fade_hide", 0.55, 0.0)],
        "w_fear":      [("abysspact_faceless_sfx_fear_stinger", 0.60, 0.0)],
        "r_grasp":     [("abysspact_faceless_sfx_mask_grasp", 0.65, 0.0)],
        "r_return":    [("abysspact_faceless_sfx_mask_return", 0.60, 0.0)],
        "shroud_rise": [("abysspact_faceless_sfx_shroud_rise", 0.60, 0.0)],
        "mask_crack":  [("abysspact_faceless_sfx_mask_crack", 0.60, 0.0)],
        "v_start":     [("abysspact_faceless_vo_start", 0.85, 0.0)],
        "v_ult":       [("abysspact_faceless_vo_ult", 0.90, 0.0)],
        "v_kill":      [("abysspact_faceless_vo_kill", 0.85, 0.0)],
        "v_respawn":   [("abysspact_faceless_vo_respawn", 0.85, 0.0)],
        "v_dead":      [("abysspact_faceless_vo_dead", 0.85, 0.0),
                        ("abysspact_faceless_sfx_death_shards", 0.55, 0.1)],
    },
    "abysspact_whisperer": {
        "a":             [("abysspact_whisperer_sfx_bead_launch", 0.45, 0.0)],
        "a_hit":         [("abysspact_whisperer_sfx_bead_hit", 0.48, 0.0)],
        "q_cast":        [("abysspact_whisperer_sfx_whisper_cast", 0.55, 0.0)],
        "q_pass":        [("abysspact_whisperer_sfx_whisper_pass", 0.50, 0.0)],
        "w_open":        [("abysspact_whisperer_sfx_ground_eye_open", 0.58, 0.0)],
        "w_blink":       [("abysspact_whisperer_sfx_ground_eye_blink", 0.42, 0.0)],
        "r_open":        [("abysspact_whisperer_sfx_mouths_open", 0.65, 0.0)],
        "r_pulse":       [("abysspact_whisperer_sfx_mouths_pulse", 0.65, 0.0)],
        "madness_stack": [("abysspact_whisperer_sfx_madness_stack", 0.48, 0.0)],
        "madness_burst": [("abysspact_whisperer_sfx_madness_burst", 0.65, 0.0)],
        "v_start":       [("abysspact_whisperer_vo_start", 0.85, 0.0)],
        "v_ult":         [("abysspact_whisperer_vo_ult", 0.90, 0.0)],
        "v_kill":        [("abysspact_whisperer_vo_kill", 0.85, 0.0)],
        "v_respawn":     [("abysspact_whisperer_vo_respawn", 0.85, 0.0)],
        "v_dead":        [("abysspact_whisperer_vo_dead", 0.85, 0.0),
                          ("abysspact_whisperer_sfx_death_beads", 0.55, 0.1)],
    },
    "abysspact_bonebow": {
        "a":             [("abysspact_bonebow_sfx_arrow_release", 0.45, 0.0)],
        "a_hit":         [("abysspact_bonebow_sfx_arrow_hit", 0.48, 0.0)],
        "q_draw":        [("abysspact_bonebow_sfx_piercer_draw", 0.50, 0.0)],
        "q_release":     [("abysspact_bonebow_sfx_piercer_release", 0.55, 0.0)],
        "q_hit":         [("abysspact_bonebow_sfx_piercer_hit", 0.55, 0.0)],
        "funeral_burst": [("abysspact_bonebow_sfx_funeral_burst", 0.62, 0.0)],
        "r_launch":      [("abysspact_bonebow_sfx_army_launch", 0.62, 0.0)],
        "r_rain":        [("abysspact_bonebow_sfx_army_rain", 0.65, 0.0)],
        "skeleton_rise": [("abysspact_bonebow_sfx_skeleton_rise", 0.52, 0.0)],
        "v_start":       [("abysspact_bonebow_vo_start", 0.85, 0.0)],
        "v_ult":         [("abysspact_bonebow_vo_ult", 0.90, 0.0)],
        "v_kill":        [("abysspact_bonebow_vo_kill", 0.85, 0.0)],
        "v_respawn":     [("abysspact_bonebow_vo_respawn", 0.85, 0.0)],
        "v_dead":        [("abysspact_bonebow_vo_dead", 0.85, 0.0),
                          ("abysspact_bonebow_sfx_death_bones", 0.55, 0.1)],
    },
    "abysspact_corvus": {
        "a":          [("abysspact_corvus_sfx_vial_launch", 0.45, 0.0)],
        "a_hit":      [("abysspact_corvus_sfx_vial_break", 0.48, 0.0)],
        "q_cast":     [("abysspact_corvus_sfx_miasma_release", 0.55, 0.0)],
        "q_ring":     [("abysspact_corvus_sfx_miasma_ring", 0.55, 0.0)],
        "w_cast":     [("abysspact_corvus_sfx_raven_takeoff", 0.55, 0.0)],
        "w_wing":     [("abysspact_corvus_sfx_raven_wing", 0.50, 0.0)],
        "raven_peck": [("abysspact_corvus_sfx_raven_peck", 0.48, 0.0)],
        "r_cane":     [("abysspact_corvus_sfx_cane_tap", 0.60, 0.0)],
        "r_cast":     [("abysspact_corvus_sfx_quarantine", 0.68, 0.0)],
        "transmit":   [("abysspact_corvus_sfx_transmit", 0.45, 0.0)],
        "heal_lift":  [("abysspact_corvus_sfx_heal_lift", 0.45, 0.0)],
        "v_start":    [("abysspact_corvus_vo_start", 0.85, 0.0)],
        "v_ult":      [("abysspact_corvus_vo_ult", 0.90, 0.0)],
        "v_kill":     [("abysspact_corvus_vo_kill", 0.85, 0.0)],
        "v_respawn":  [("abysspact_corvus_vo_respawn", 0.85, 0.0)],
        "v_dead":     [("abysspact_corvus_vo_dead", 0.85, 0.0),
                       ("abysspact_corvus_sfx_death_censer", 0.55, 0.1)],
    },
    # --- Batch 2 ---
    "abysspact_bloodmoon": {
        "a_silver":        [("abysspact_bloodmoon_sfx_silver_release", 0.45, 0.0)],
        "a_silver_hit":    [("abysspact_bloodmoon_sfx_silver_hit", 0.48, 0.0)],
        "a_wolf":          [("abysspact_bloodmoon_sfx_wolf_claw", 0.50, 0.0)],
        "pounce_hit":      [("abysspact_bloodmoon_sfx_pounce_hit", 0.54, 0.0)],
        "q_silver_volley": [("abysspact_bloodmoon_sfx_silver_volley", 0.56, 0.0)],
        "q_pounce":        [("abysspact_bloodmoon_sfx_pounce", 0.58, 0.0)],
        "w_transform":     [("abysspact_bloodmoon_sfx_transform", 0.62, 0.0)],
        "w_rollback":      [("abysspact_bloodmoon_sfx_return_roll", 0.54, 0.0)],
        "r_moon":          [("abysspact_bloodmoon_sfx_moon_rise", 0.65, 0.0)],
        "r_howl":          [("abysspact_bloodmoon_sfx_giant_howl", 0.72, 0.0)],
        "wolf_growl":      [("abysspact_bloodmoon_sfx_wolf_growl", 0.58, 0.0)],
        "giant_sweep":     [("abysspact_bloodmoon_sfx_giant_sweep", 0.60, 0.0)],
        "v_start":         [("abysspact_bloodmoon_vo_start", 0.85, 0.0)],
        "v_ult":           [("abysspact_bloodmoon_vo_ult", 0.90, 0.0)],
        "v_kill":          [("abysspact_bloodmoon_vo_kill", 0.85, 0.0)],
        "v_respawn":       [("abysspact_bloodmoon_vo_respawn", 0.85, 0.0)],
        "v_dead":          [("abysspact_bloodmoon_vo_dead", 0.85, 0.0),
                            ("abysspact_bloodmoon_sfx_death", 0.55, 0.1)],
    },
    "abysspact_undertaker": {
        "a":            [("abysspact_undertaker_sfx_coffin_swing", 0.48, 0.0)],
        "a_hit":        [("abysspact_undertaker_sfx_coffin_hit", 0.52, 0.0)],
        "q_cast":       [("abysspact_undertaker_sfx_burial_cast", 0.58, 0.0)],
        "q_crack":      [("abysspact_undertaker_sfx_burial_crack", 0.60, 0.0)],
        "w_chain":      [("abysspact_undertaker_sfx_send_chain", 0.56, 0.0)],
        "w_anchor":     [("abysspact_undertaker_sfx_send_anchor", 0.60, 0.0)],
        "r_open":       [("abysspact_undertaker_sfx_coffin_open", 0.66, 0.0)],
        "coffin_close": [("abysspact_undertaker_sfx_coffin_close", 0.66, 0.0)],
        "coffin_leak":  [("abysspact_undertaker_sfx_coffin_leak", 0.46, 0.0)],
        "coffin_drop":  [("abysspact_undertaker_sfx_coffin_drop", 0.68, 0.0)],
        "guard":        [("abysspact_undertaker_sfx_guard", 0.54, 0.0)],
        "v_start":      [("abysspact_undertaker_vo_start", 0.85, 0.0)],
        "v_ult":        [("abysspact_undertaker_vo_ult", 0.90, 0.0)],
        "v_kill":       [("abysspact_undertaker_vo_kill", 0.85, 0.0)],
        "v_respawn":    [("abysspact_undertaker_vo_respawn", 0.85, 0.0)],
        "v_dead":       [("abysspact_undertaker_vo_dead", 0.85, 0.0),
                         ("abysspact_undertaker_sfx_death", 0.55, 0.1)],
    },
    "abysspact_effigy": {
        "a":             [("abysspact_effigy_sfx_needle_launch", 0.45, 0.0)],
        "a_hit":         [("abysspact_effigy_sfx_hit", 0.48, 0.0)],
        "q_fan":         [("abysspact_effigy_sfx_sew_fan", 0.55, 0.0)],
        "q_hit":         [("abysspact_effigy_sfx_sew_hit", 0.52, 0.0)],
        "w_throw":       [("abysspact_effigy_sfx_thread_throw", 0.56, 0.0)],
        "w_taut":        [("abysspact_effigy_sfx_thread_taut", 0.52, 0.0)],
        "r_unpick":      [("abysspact_effigy_sfx_unpick", 0.66, 0.0)],
        "unpick_return": [("abysspact_effigy_sfx_unpick_return", 0.60, 0.0)],
        "needle_mark":   [("abysspact_effigy_sfx_needle_mark", 0.46, 0.0)],
        "thread_knot":   [("abysspact_effigy_sfx_thread_knot", 0.54, 0.0)],
        "thread_snap":   [("abysspact_effigy_sfx_thread_snap", 0.66, 0.0)],
        "v_start":       [("abysspact_effigy_vo_start", 0.85, 0.0)],
        "v_ult":         [("abysspact_effigy_vo_ult", 0.90, 0.0)],
        "v_kill":        [("abysspact_effigy_vo_kill", 0.85, 0.0)],
        "v_respawn":     [("abysspact_effigy_vo_respawn", 0.85, 0.0)],
        "v_dead":        [("abysspact_effigy_vo_dead", 0.85, 0.0),
                          ("abysspact_effigy_sfx_doll_after", 0.52, 0.1)],
    },
    "abysspact_sevenfold": {
        "a":              [("abysspact_sevenfold_sfx_round_flash", 0.46, 0.0)],
        "a_hit":          [("abysspact_sevenfold_sfx_round_hit", 0.48, 0.0)],
        "q_triple":       [("abysspact_sevenfold_sfx_triple_volley", 0.58, 0.0)],
        "w_roll":         [("abysspact_sevenfold_sfx_reload_roll", 0.54, 0.0)],
        "r_salvo":        [("abysspact_sevenfold_sfx_salvo", 0.66, 0.0)],
        "r_curse_launch": [("abysspact_sevenfold_sfx_curse_launch", 0.64, 0.0)],
        "abyss_eye":      [("abysspact_sevenfold_sfx_abyss_eye", 0.62, 0.0)],
        "curse_burst":    [("abysspact_sevenfold_sfx_curse_burst", 0.68, 0.0)],
        "charge_ping":    [("abysspact_sevenfold_sfx_charge_ping", 0.54, 0.0)],
        "v_start":        [("abysspact_sevenfold_vo_start", 0.85, 0.0)],
        "v_ult":          [("abysspact_sevenfold_vo_ult", 0.90, 0.0)],
        "v_kill":         [("abysspact_sevenfold_vo_kill", 0.85, 0.0)],
        "v_respawn":      [("abysspact_sevenfold_vo_respawn", 0.85, 0.0)],
        "v_dead":         [("abysspact_sevenfold_vo_dead", 0.85, 0.0),
                           ("abysspact_sevenfold_sfx_death_pip", 0.54, 0.1)],
    },
    "abysspact_vesper": {
        "a":             [("abysspact_vesper_sfx_wisp_launch", 0.44, 0.0)],
        "a_hit":         [("abysspact_vesper_sfx_wisp_hit", 0.48, 0.0)],
        "q_link":        [("abysspact_vesper_sfx_guide_link", 0.52, 0.0)],
        "q_heal":        [("abysspact_vesper_sfx_guide_heal", 0.48, 0.0)],
        "warm_shield":   [("abysspact_vesper_sfx_warm_shield", 0.54, 0.0)],
        "w_launch":      [("abysspact_vesper_sfx_startle_launch", 0.58, 0.0)],
        "w_fade":        [("abysspact_vesper_sfx_startle_fade", 0.52, 0.0)],
        "r_pointer":     [("abysspact_vesper_sfx_tablet_pointer", 0.58, 0.0)],
        "return_pillar": [("abysspact_vesper_sfx_return_pillar", 0.68, 0.0)],
        "soul_form":     [("abysspact_vesper_sfx_soul_form", 0.58, 0.0)],
        "rebirth_ring":  [("abysspact_vesper_sfx_rebirth_ring", 0.66, 0.0)],
        "candle_out":    [("abysspact_vesper_sfx_candle_out", 0.52, 0.0)],
        "v_start":       [("abysspact_vesper_vo_start", 0.85, 0.0)],
        "v_ult":         [("abysspact_vesper_vo_ult", 0.90, 0.0)],
        "v_kill":        [("abysspact_vesper_vo_kill", 0.85, 0.0)],
        "v_respawn":     [("abysspact_vesper_vo_respawn", 0.85, 0.0)],
        "v_dead":        [("abysspact_vesper_vo_dead", 0.85, 0.0),
                          ("abysspact_vesper_sfx_candle_out", 0.54, 0.1)],
    },
    # --- Batch 3 ---
    "abysspact_carapace": {
        "a":            [("abysspact_carapace_sfx_cross_cut", 0.48, 0.0)],
        "a_hit":        [("abysspact_carapace_sfx_impact", 0.50, 0.0)],
        "q_thrust":     [("abysspact_carapace_sfx_thrust", 0.56, 0.0)],
        "q_dive":       [("abysspact_carapace_sfx_dive", 0.60, 0.0)],
        "w_resonate":   [("abysspact_carapace_sfx_resonate", 0.58, 0.0)],
        "molt_crack":   [("abysspact_carapace_sfx_molt_crack", 0.64, 0.0)],
        "molt_rise":    [("abysspact_carapace_sfx_molt_rise", 0.62, 0.0)],
        "shell_rattle": [("abysspact_carapace_sfx_shell_rattle", 0.56, 0.0)],
        "shell_burst":  [("abysspact_carapace_sfx_shell_burst", 0.68, 0.0)],
        "v_start":      [("abysspact_carapace_vo_start", 0.85, 0.0)],
        "v_ult":        [("abysspact_carapace_vo_ult", 0.90, 0.0)],
        "v_kill":       [("abysspact_carapace_vo_kill", 0.85, 0.0)],
        "v_respawn":    [("abysspact_carapace_vo_respawn", 0.85, 0.0)],
        "v_dead":       [("abysspact_carapace_vo_dead", 0.85, 0.0),
                         ("abysspact_carapace_sfx_death", 0.55, 0.1)],
    },
    "abysspact_leech": {
        "a":           [("abysspact_leech_sfx_claw", 0.46, 0.0)],
        "a_hit":       [("abysspact_leech_sfx_claw_hit", 0.50, 0.0)],
        "q_lunge":     [("abysspact_leech_sfx_lunge", 0.56, 0.0)],
        "q_attach":    [("abysspact_leech_sfx_attach", 0.58, 0.0)],
        "w_bite":      [("abysspact_leech_sfx_hood_mouth", 0.56, 0.0)],
        "w_venom":     [("abysspact_leech_sfx_venom", 0.58, 0.0)],
        "r_lunge":     [("abysspact_leech_sfx_leech_lunge", 0.62, 0.0)],
        "r_cling":     [("abysspact_leech_sfx_leech_cling", 0.50, 0.0)],
        "drain":       [("abysspact_leech_sfx_drain", 0.48, 0.0)],
        "jump":        [("abysspact_leech_sfx_detach", 0.56, 0.0)],
        "shared_pain": [("abysspact_leech_sfx_share_hit", 0.52, 0.0)],
        "split":       [("abysspact_leech_sfx_split", 0.66, 0.0)],
        "rejoin":      [("abysspact_leech_sfx_merge", 0.64, 0.0)],
        "v_start":     [("abysspact_leech_vo_start", 0.85, 0.0)],
        "v_ult":       [("abysspact_leech_vo_ult", 0.90, 0.0)],
        "v_kill":      [("abysspact_leech_vo_kill", 0.85, 0.0)],
        "v_respawn":   [("abysspact_leech_vo_respawn", 0.85, 0.0)],
        "v_dead":      [("abysspact_leech_vo_dead", 0.85, 0.0),
                        ("abysspact_leech_sfx_death", 0.54, 0.1)],
    },
    "abysspact_noctua": {
        "a":           [("abysspact_noctua_sfx_moth_launch", 0.44, 0.0)],
        "a_hit":       [("abysspact_noctua_sfx_moth_flap", 0.46, 0.0)],
        "q_swarm":     [("abysspact_noctua_sfx_swarm_cast", 0.56, 0.0)],
        "scale_mark":  [("abysspact_noctua_sfx_scale_mark", 0.46, 0.0)],
        "w_close":     [("abysspact_noctua_sfx_cocoon_close", 0.58, 0.0)],
        "w_break":     [("abysspact_noctua_sfx_cocoon_break", 0.56, 0.0)],
        "disperse":    [("abysspact_noctua_sfx_disperse", 0.60, 0.0)],
        "reform":      [("abysspact_noctua_sfx_reform", 0.58, 0.0)],
        "storm_start": [("abysspact_noctua_sfx_storm_start", 0.68, 0.0)],
        "dust_shock":  [("abysspact_noctua_sfx_dust_ring", 0.66, 0.0)],
        "v_start":     [("abysspact_noctua_vo_start", 0.85, 0.0)],
        "v_ult":       [("abysspact_noctua_vo_ult", 0.90, 0.0)],
        "v_kill":      [("abysspact_noctua_vo_kill", 0.85, 0.0)],
        "v_respawn":   [("abysspact_noctua_vo_respawn", 0.85, 0.0)],
        "v_dead":      [("abysspact_noctua_vo_dead", 0.85, 0.0),
                        ("abysspact_noctua_sfx_death", 0.54, 0.1)],
    },
    "abysspact_anchor": {
        "a_chain":      [("abysspact_anchor_sfx_chain_launch", 0.46, 0.0)],
        "a_siege":      [("abysspact_anchor_sfx_siege_shot", 0.58, 0.0)],
        "a_water":      [("abysspact_anchor_sfx_water_hit", 0.50, 0.0)],
        "q_sweep":      [("abysspact_anchor_sfx_chain_sweep", 0.60, 0.0)],
        "plant":        [("abysspact_anchor_sfx_anchor_plant", 0.64, 0.0)],
        "raise":        [("abysspact_anchor_sfx_anchor_raise", 0.56, 0.0)],
        "r_fire":       [("abysspact_anchor_sfx_salvo_fire", 0.62, 0.0)],
        "r_impact":     [("abysspact_anchor_sfx_salvo_impact", 0.66, 0.0)],
        "v_start":      [("abysspact_anchor_vo_start", 0.85, 0.0)],
        "v_ult":        [("abysspact_anchor_vo_ult", 0.90, 0.0)],
        "v_kill":       [("abysspact_anchor_vo_kill", 0.85, 0.0)],
        "v_respawn":    [("abysspact_anchor_vo_respawn", 0.85, 0.0)],
        "v_dead":       [("abysspact_anchor_vo_dead", 0.85, 0.0),
                         ("abysspact_anchor_sfx_death_sink", 0.56, 0.1)],
    },
    "abysspact_hourglass": {
        "a":           [("abysspact_hourglass_sfx_spark_launch", 0.44, 0.0)],
        "a_hit":       [("abysspact_hourglass_sfx_spark_hit", 0.46, 0.0)],
        "q_mark":      [("abysspact_hourglass_sfx_mark", 0.56, 0.0)],
        "w_stop":      [("abysspact_hourglass_sfx_stop_gear", 0.60, 0.0)],
        "flip":        [("abysspact_hourglass_sfx_glass_flip", 0.68, 0.0)],
        "rewind_snap": [("abysspact_hourglass_sfx_rewind", 0.62, 0.0)],
        "age_tick":    [("abysspact_hourglass_sfx_age_change", 0.50, 0.0)],
        "v_start":     [("abysspact_hourglass_vo_start", 0.85, 0.0)],
        "v_ult":       [("abysspact_hourglass_vo_ult", 0.90, 0.0)],
        "v_kill":      [("abysspact_hourglass_vo_kill", 0.85, 0.0)],
        "v_respawn":   [("abysspact_hourglass_vo_respawn", 0.85, 0.0)],
        "v_dead":      [("abysspact_hourglass_vo_dead", 0.85, 0.0),
                        ("abysspact_hourglass_sfx_death", 0.54, 0.1)],
    },
}


def build_i18n():
    P = B.PARAMS
    po = P["oathbreaker"]
    pf = P["faceless"]
    pw = P["whisperer"]
    pb = P["bonebow"]
    pc = P["corvus"]
    pbm = P["bloodmoon"]
    pu = P["undertaker"]
    pe = P["effigy"]
    ps = P["sevenfold"]
    pv = P["vesper"]
    pca = P["carapace"]
    pl = P["leech"]
    pn = P["noctua"]
    pa = P["anchor"]
    ph = P["hourglass"]

    desc = {"zh-hans": {}, "zh-hant": {}, "en": {}, "ja": {}, "ko": {}}
    skn = {"zh-hans": {}, "zh-hant": {}, "en": {}, "ja": {}, "ko": {}}

    def put(cid, lang, name, atk, s1, s2, ult, n1, n2, nu):
        desc[lang][cid] = {"name": name, "attack": atk, "skill": s1, "skill2": s2, "ult": ult}
        skn[lang][cid] = {"skill1": n1, "skill2": n2, "ult": nu}

    # --- 1. 断誓 Oathbreaker ---
    put("abysspact_oathbreaker", "zh-hans", "断誓",
        f"断剑劈砍造成{ADi}{O}100%{E}物理伤害。{O}血誓{E}：放技能烧{A}6%{E}当前生命，每损{A}10%{E}生命攻击+{A}4%{E}、攻速+{A}5%{E}。",
        f"横扫黑火月牙造成{ad(po['q_dmg'], po['q_ad'])}物理伤害并{R}减速{po['q_slow']}%{E}；命中英雄回血，斩中被链目标追加伤害。",
        f"甩出誓链勾中首个敌方英雄拽至身前，造成{ad(po['w_dmg'], po['w_ad'])}物理伤害并{R}定身{secs(po['w_bind'])}秒{E}。",
        f"盔甲裂开{A}{secs(po['r_t'])}秒{E}内不会阵亡，吸血{A}{po['r_vamp']}%{E}、普攻附带黑火；期间参与击杀回{A}25%{E}血，否则烧{A}15%{E}当前血。",
        "黑焰斩", "誓链", "断誓")
    put("abysspact_oathbreaker", "zh-hant", "斷誓",
        f"斷劍劈砍造成{ADi}{O}100%{E}物理傷害。{O}血誓{E}：放技能燒{A}6%{E}當前生命，每損{A}10%{E}生命攻擊+{A}4%{E}、攻速+{A}5%{E}。",
        f"橫掃黑火月牙造成{ad(po['q_dmg'], po['q_ad'])}物理傷害並{R}減速{po['q_slow']}%{E}；命中英雄回血，斬中被鏈目標追加傷害。",
        f"甩出誓鏈勾中首個敵方英雄拽至身前，造成{ad(po['w_dmg'], po['w_ad'])}物理傷害並{R}定身{secs(po['w_bind'])}秒{E}。",
        f"盔甲裂開{A}{secs(po['r_t'])}秒{E}內不會陣亡，吸血{A}{po['r_vamp']}%{E}、普攻附帶黑火；期間參與擊殺回{A}25%{E}血，否則燒{A}15%{E}當前血。",
        "黑焰斬", "誓鏈", "斷誓")
    put("abysspact_oathbreaker", "en", "Oathbreaker",
        f"Broken greatsword strike for {ADi}{O}100%{E} physical damage. {O}Blood Oath{E}: skills burn {A}6%{E} current HP; gain {A}+4%{E} AD and {A}+5%{E} AS per {A}10%{E} missing HP.",
        f"Sweep a black-flame crescent for {ad(po['q_dmg'], po['q_ad'])} physical damage and {R}{po['q_slow']}% slow{E}; heals on champion hits and deals bonus damage to chained foes.",
        f"Hurl a broken oath chain that hooks the first enemy champion, pulling them in for {ad(po['w_dmg'], po['w_ad'])} physical damage and {R}{secs(po['w_bind'])}s bind{E}.",
        f"Refuse death for {A}{secs(po['r_t'])}s{E} with {A}{po['r_vamp']}%{E} vamp and bonus black-flame hits. Takedown heals {A}25%{E} max HP at end; otherwise burn {A}15%{E} current HP.",
        "Blackflame Cleave", "Oath Chain", "Broken Oath")
    put("abysspact_oathbreaker", "ja", "断誓",
        f"断剣で{ADi}{O}100%{E}物理ダメージ。{O}血誓{E}：スキルで現在HP{A}6%{E}消費、減少HP{A}10%{E}毎に攻撃+{A}4%{E}・攻撃速度+{A}5%{E}。",
        f"黒炎の斬撃で{ad(po['q_dmg'], po['q_ad'])}物理ダメージと{R}{po['q_slow']}%スロウ{E}。英雄命中で回復、鎖対象に追加ダメージ。",
        f"誓いの鎖で最初の敵英雄を引き寄せ、{ad(po['w_dmg'], po['w_ad'])}物理ダメージと{R}{secs(po['w_bind'])}秒束縛{E}。",
        f"{A}{secs(po['r_t'])}秒{E}不死と吸血{A}{po['r_vamp']}%{E}、通常攻撃に黒炎付与。関与で終了時{A}25%{E}回復、未達成で現在HP{A}15%{E}消費。",
        "黒炎斬", "誓鎖", "断誓")
    put("abysspact_oathbreaker", "ko", "단서",
        f"부러진 대검으로 {ADi}{O}100%{E} 물리 피해. {O}혈서{E}: 스킬 사용 시 현재 체력 {A}6%{E} 소모, 잃은 체력 {A}10%{E}당 공격력+{A}4%{E}, 공속+{A}5%{E}.",
        f"검은 불꽃을 휘둘러 {ad(po['q_dmg'], po['q_ad'])} 물리 피해와 {R}{po['q_slow']}% 둔화{E}. 챔피언 적중 시 회복, 사슬 표적 추가 피해.",
        f"서약의 사슬로 첫 적 챔피언을 끌어당겨 {ad(po['w_dmg'], po['w_ad'])} 물리 피해와 {R}{secs(po['w_bind'])}초 속박{E}.",
        f"{A}{secs(po['r_t'])}초{E} 불사 및 흡혈 {A}{po['r_vamp']}%{E}, 기본 공격 흑염 추가. 처치 관여 시 최대 체력 {A}25%{E} 회복, 실패 시 현재 체력 {A}15%{E} 소모.",
        "흑염참", "서약 사슬", "단서")

    # --- 2. 无面 Faceless ---
    put("abysspact_faceless", "zh-hans", "无面",
        f"指刃划击造成{ADi}{O}100%{E}物理伤害。{O}夺面{E}：参与击杀英雄后戴上其面孔{A}10秒{E}，化身为目标并借用其攻击方式与强化爆发。",
        f"化作黑影穿过目标冲至其身后，对路径敌人造成{ad(pf['q_dmg'], pf['q_ad'])}物理伤害并{R}减速{pf['q_slow']}%{E}。",
        f"遁入黑雾{A}隐身{secs(pf['w_inv'])}秒{E}并提速；现身后的首击令目标直面空脸，追加伤害并{R}恐惧{secs(pf['w_fear'])}秒{E}。",
        f"按住敌方英雄撕下面孔造成{ad(pf['r_dmg'], pf['r_ad'])}物理伤害；目标生命低于{A}25%{E}时直接真实斩杀并立刻夺面。",
        "割影", "无相", "撕面")
    put("abysspact_faceless", "zh-hant", "無面",
        f"指刃劃擊造成{ADi}{O}100%{E}物理傷害。{O}奪面{E}：參與擊殺英雄後戴上其面孔{A}10秒{E}，化身為目標並借用其攻擊方式與強化爆發。",
        f"化作黑影穿過目標衝至其身後，對路徑敵人造成{ad(pf['q_dmg'], pf['q_ad'])}物理傷害並{R}減速{pf['q_slow']}%{E}。",
        f"遁入黑霧{A}隱身{secs(pf['w_inv'])}秒{E}並提速；現身後的首擊令目標直面空臉，追加傷害並{R}恐懼{secs(pf['w_fear'])}秒{E}。",
        f"按住敵方英雄撕下面孔造成{ad(pf['r_dmg'], pf['r_ad'])}物理傷害；目標生命低於{A}25%{E}時直接真實斬殺並立刻奪面。",
        "割影", "無相", "撕面")
    put("abysspact_faceless", "en", "Faceless",
        f"Claw slash for {ADi}{O}100%{E} physical damage. {O}Face Steal{E}: takedowns let him wear the victim's face for {A}10s{E}, assuming their form with boosted combat power.",
        f"Turn to shadow and dash through enemies for {ad(pf['q_dmg'], pf['q_ad'])} physical damage and a {R}{pf['q_slow']}% slow{E}.",
        f"Fade into dark mist, gaining {A}{secs(pf['w_inv'])}s stealth{E} and speed. His first strike out of stealth deals bonus damage and {R}fears for {secs(pf['w_fear'])}s{E}.",
        f"Grasp an enemy champion and rip off their face for {ad(pf['r_dmg'], pf['r_ad'])} physical damage; targets at or below {A}25%{E} HP are executed immediately and stolen.",
        "Shadow Slice", "Formless", "Face Rip")
    put("abysspact_faceless", "ja", "無面",
        f"指刃で{ADi}{O}100%{E}物理ダメージ。{O}奪面{E}：英雄撃破関与で{A}10秒{E}相手の姿に変身し、攻撃特性と強化を得る。",
        f"影となり敵を突き抜けて{ad(pf['q_dmg'], pf['q_ad'])}物理ダメージと{R}{pf['q_slow']}%スロウ{E}。",
        f"黒霧に{A}{secs(pf['w_inv'])}秒隠密{E}し加速。初撃に追加ダメージと{R}{secs(pf['w_fear'])}秒恐怖{E}。",
        f"敵英雄の顔を剥ぎ{ad(pf['r_dmg'], pf['r_ad'])}物理ダメージ。HP{A}25%{E}以下なら即座に確定処刑し奪面する。",
        "影割", "無相", "面剥ぎ")
    put("abysspact_faceless", "ko", "무면",
        f"손톱 칼날로 {ADi}{O}100%{E} 물리 피해. {O}탈면{E}: 적 챔피언 처치 관여 시 {A}10초{E}간 대상의 얼굴과 모습을 빼앗아 변신.",
        f"그림자가 되어 적을 관통하며 {ad(pf['q_dmg'], pf['q_ad'])} 물리 피해와 {R}{pf['q_slow']}% 둔화{E}.",
        f"검은 안개에 {A}{secs(pf['w_inv'])}초 은신{E} 및 가속. 은신 해제 첫 타격은 추가 피해와 {R}{secs(pf['w_fear'])}초 공포{E}.",
        f"적 챔피언의 얼굴을 찢어 {ad(pf['r_dmg'], pf['r_ad'])} 물리 피해. 체력 {A}25%{E} 이하는 즉시 고정 피해 처형 후 탈면.",
        "그림자 베기", "무상", "면박")

    # --- 3. 呓语 Whisperer ---
    put("abysspact_whisperer", "zh-hans", "呓语",
        f"弹射念珠造成{ADi}{O}100%{E}物理伤害。{O}疯狂{E}：技能叠加疯狂，满{A}3层{E}时{R}恐惧1.5秒{E}并爆开魔法伤害波及附近友军且继续传染。",
        f"推出直线穿透的紫色低语，对路径敌人造成{ap(pw['q_dmg'], pw['q_ap'])}魔法伤害并叠加{A}1层{E}疯狂。",
        f"在目标处睁开巨眼持续{A}{secs(pw['w_t'])}秒{E}，每秒造成{ap(pw['w_dmg'], pw['w_ap'])}魔法伤害、{R}减速{pw['w_slow']}%{E}并叠{A}1层{E}疯狂。",
        f"令目标地面裂开众口齐诵，造成{ap(pw['r_dmg'], pw['r_ap'])}魔法伤害，范围内敌人直接叠满{A}3层{E}疯狂当场连锁发狂。",
        "低语", "睁眼", "众口")
    put("abysspact_whisperer", "zh-hant", "囈語",
        f"彈射念珠造成{ADi}{O}100%{E}物理傷害。{O}瘋狂{E}：技能疊加瘋狂，滿{A}3層{E}時{R}恐懼1.5秒{E}並爆開魔法傷害波及附近友軍且繼續傳染。",
        f"推出直線穿透的紫色低語，對路徑敵人造成{ap(pw['q_dmg'], pw['q_ap'])}魔法傷害並疊加{A}1層{E}瘋狂。",
        f"在目標處睜開巨眼持續{A}{secs(pw['w_t'])}秒{E}，每秒造成{ap(pw['w_dmg'], pw['w_ap'])}魔法傷害、{R}減速{pw['w_slow']}%{E}並疊{A}1層{E}瘋狂。",
        f"令目標地面裂開眾口齊誦，造成{ap(pw['r_dmg'], pw['r_ap'])}魔法傷害，範圍內敵人直接疊滿{A}3層{E}瘋狂當場連鎖發狂。",
        "低語", "睜眼", "眾口")
    put("abysspact_whisperer", "en", "Whisperer",
        f"Flick a prayer bead for {ADi}{O}100%{E} physical damage. {O}Madness{E}: skills stack Madness; at {A}3 stacks{E} foes suffer {R}1.5s fear{E}, blast nearby allies for magic damage, and spread +1 stack.",
        f"Send a piercing purple whisper dealing {ap(pw['q_dmg'], pw['q_ap'])} magic damage and adding {A}1 Madness{E} stack.",
        f"Open a giant eye on the ground for {A}{secs(pw['w_t'])}s{E}, dealing {ap(pw['w_dmg'], pw['w_ap'])} magic damage/s, {R}{pw['w_slow']}% slow{E}, and {A}+1 Madness/s{E}.",
        f"Split the earth with chanting mouths for {ap(pw['r_dmg'], pw['r_ap'])} magic damage, instantly filling {A}3 Madness{E} on all foes inside to trigger chain eruptions.",
        "Whisper", "Open Eye", "Chorus of Mouths")
    put("abysspact_whisperer", "ja", "囈語",
        f"数珠を飛ばし{ADi}{O}100%{E}物理ダメージ。{O}狂気{E}：スキルで蓄積、{A}3層{E}で{R}1.5秒恐怖{E}し周囲の味方に魔法爆発＆狂気連鎖。",
        f"貫通する紫の囁きを放ち{ap(pw['q_dmg'], pw['q_ap'])}魔法ダメージと狂気{A}+1層{E}。",
        f"地面に巨眼を開き{A}{secs(pw['w_t'])}秒{E}間、毎秒{ap(pw['w_dmg'], pw['w_ap'])}魔法ダメージ、{R}{pw['w_slow']}%スロウ{E}、狂気{A}+1層{E}。",
        f"無数の口が裂け{ap(pw['r_dmg'], pw['r_ap'])}魔法ダメージを与え、範囲内の敵を即座に狂気{A}3層{E}にして連鎖発狂させる。",
        "低語", "開眼", "衆口")
    put("abysspact_whisperer", "ko", "잠꼬대",
        f"염주를 날려 {ADi}{O}100%{E} 물리 피해. {O}광기{E}: 스킬 적중 시 중첩, {A}3중첩{E} 시 {R}1.5초 공포{E}와 함께 주변 아군에게 마법 폭발 및 연쇄 전파.",
        f"관통하는 보라색 속삭임으로 {ap(pw['q_dmg'], pw['q_ap'])} 마법 피해와 광기 {A}1중첩{E}.",
        f"대상에 거대한 눈을 {A}{secs(pw['w_t'])}초{E}간 열어 매초 {ap(pw['w_dmg'], pw['w_ap'])} 마법 피해, {R}{pw['w_slow']}% 둔화{E}, 광기 {A}1중첩{E}.",
        f"지면에 수많은 입을 열어 {ap(pw['r_dmg'], pw['r_ap'])} 마법 피해와 동시에 모든 적에게 광기 {A}3중첩{E}을 채워 연쇄 폭주.",
        "속삭임", "개안", "중구")

    # --- 4. 骸弦 Bonebow ---
    put("abysspact_bonebow", "zh-hans", "骸弦",
        f"骨箭射击造成{ADi}{O}100%{E}物理伤害。{O}亡兵{E}：每第{A}4箭{E}在目标旁拉起1名骷髅兵作战{A}6秒{E}（继承{A}30%{E}攻击，常规上限{A}3名{E}）。",
        f"射出穿透骨箭造成{ad(pb['q_dmg'], pb['q_ad'])}物理伤害；每命中一名敌方英雄，就在其脚下拉起1名骷髅兵。",
        f"令场上所有骷髅兵冲向目标并自爆，每名造成{ad(40, 50)}范围物理伤害并{R}减速{pb['w_slow']}%{E}。",
        f"朝天射箭降下骨箭雨造成{ad(pb['r_dmg'], pb['r_ad'])}物理伤害并减速，同时爬出{A}5名{E}骷髅兵作战{A}8秒{E}（不占上限）。",
        "穿骨", "葬礼", "亡军")
    put("abysspact_bonebow", "zh-hant", "骸弦",
        f"骨箭射擊造成{ADi}{O}100%{E}物理傷害。{O}亡兵{E}：每第{A}4箭{E}在目標旁拉起1名骷髏兵作戰{A}6秒{E}（繼承{A}30%{E}攻擊，常規上限{A}3名{E}）。",
        f"射出穿透骨箭造成{ad(pb['q_dmg'], pb['q_ad'])}物理傷害；每命中一名敵方英雄，就在其腳下拉起1名骷髏兵。",
        f"令場上所有骷髏兵衝向目標並自爆，每名造成{ad(40, 50)}範圍物理傷害並{R}減速{pb['w_slow']}%{E}。",
        f"朝天射箭降下骨箭雨造成{ad(pb['r_dmg'], pb['r_ad'])}物理傷害並減速，同時爬出{A}5名{E}骷髏兵作戰{A}8秒{E}（不佔上限）。",
        "穿骨", "葬禮", "亡軍")
    put("abysspact_bonebow", "en", "Bonebow",
        f"Bone arrow for {ADi}{O}100%{E} physical damage. {O}Risen Dead{E}: every {A}4th arrow{E} raises a skeleton ({A}30%{E} AD, {A}6s{E}, cap {A}3{E}) beside the target.",
        f"Fire a piercing bone arrow for {ad(pb['q_dmg'], pb['q_ad'])} physical damage, raising a skeleton beside every enemy champion hit.",
        f"Command all living skeletons to rush her target and detonate for {ad(40, 50)} AoE physical damage each plus {R}{pb['w_slow']}% slow{E}.",
        f"Rain bone arrows for {ad(pb['r_dmg'], pb['r_ad'])} AoE physical damage and raise {A}5 uncapped skeletons{E} for {A}8s{E}.",
        "Bone Piercer", "Funeral", "Risen Army")
    put("abysspact_bonebow", "ja", "骸弦",
        f"骨矢で{ADi}{O}100%{E}物理ダメージ。{O}亡兵{E}：{A}4射目{E}毎に骸骨兵を召喚（攻撃{A}30%{E}、{A}6秒{E}、上限{A}3体{E}）。",
        f"貫通する骨矢で{ad(pb['q_dmg'], pb['q_ad'])}物理ダメージ。命中した敵英雄ごとに足元へ骸骨兵を召喚。",
        f"全骸骨兵を目標へ突撃自爆させ、各{ad(40, 50)}範囲物理ダメージと{R}{pb['w_slow']}%スロウ{E}。",
        f"骨矢の雨で{ad(pb['r_dmg'], pb['r_ad'])}物理ダメージを与え、上限外の骸骨兵{A}5体{E}を{A}8秒{E}召喚する。",
        "穿骨", "葬礼", "亡軍")
    put("abysspact_bonebow", "ko", "해현",
        f"뼈화살로 {ADi}{O}100%{E} 물리 피해. {O}망병{E}: {A}4발{E}마다 대상 옆에 해골병 소환(공격력 {A}30%{E}, {A}6초{E}, 최대 {A}3기{E}).",
        f"관통 뼈화살로 {ad(pb['q_dmg'], pb['q_ad'])} 물리 피해. 적중한 적 챔피언마다 해골병 1기 소환.",
        f"모든 해골병을 표적으로 돌진 자폭시켜 기당 {ad(40, 50)} 범위 물리 피해와 {R}{pb['w_slow']}% 둔화{E}.",
        f"뼈화살 비로 {ad(pb['r_dmg'], pb['r_ad'])} 범위 물리 피해와 함께 상한 외 해골병 {A}5기{E}를 {A}8초{E} 소환.",
        "천골", "장례", "망군")

    # --- 5. 鸦医 Corvus ---
    put("abysspact_corvus", "zh-hans", "鸦医",
        f"投掷药瓶造成{ADi}{O}100%{E}物理伤害。{O}传染{E}：技能种下{A}4秒{E}疫病（每秒{A}2%{E}最大血伤）并在敌间传染；队友靠近病人每秒回{A}1%–3%{E}血。",
        f"砸出大瘴气瓶，对范围内敌人造成{ap(pc['q_dmg'], pc['q_ap'])}魔法伤害、{R}减速{pc['q_slow']}%{E}并全部染上疫病。",
        f"派出肩头渡鸦守护队友{A}{secs(pc['w_t'])}秒{E}：赋予{S}{pc['w_sh']}{E}+{APi}{S}{pc['w_sh_ap']}%{E}护盾，渡鸦每秒啄击附近敌人并传染疫病。",
        f"划出持续{A}{secs(pc['r_t'])}秒{E}的隔离区：落地造成{ap(pc['r_init_dmg'], pc['r_init_ap'])}法伤并{R}眩晕{secs(pc['r_stun'])}秒{E}，圈内敌人持续染病减速，队友持续回血。",
        "瘴瓶", "渡鸦", "隔离区")
    put("abysspact_corvus", "zh-hant", "鴉醫",
        f"投擲藥瓶造成{ADi}{O}100%{E}物理傷害。{O}傳染{E}：技能種下{A}4秒{E}疫病（每秒{A}2%{E}最大血傷）並在敵間傳染；隊友靠近病人每秒回{A}1%–3%{E}血。",
        f"砸出大瘴氣瓶，對範圍內敵人造成{ap(pc['q_dmg'], pc['q_ap'])}魔法傷害、{R}減速{pc['q_slow']}%{E}並全部染上疫病。",
        f"派出肩頭渡鴉守護隊友{A}{secs(pc['w_t'])}秒{E}：賦予{S}{pc['w_sh']}{E}+{APi}{S}{pc['w_sh_ap']}%{E}護盾，渡鴉每秒啄擊附近敵人並傳染疫病。",
        f"劃出持續{A}{secs(pc['r_t'])}秒{E}的隔離區：落地造成{ap(pc['r_init_dmg'], pc['r_init_ap'])}法傷並{R}眩暈{secs(pc['r_stun'])}秒{E}，圈內敵人持續染病減速，隊友持續回血。",
        "瘴瓶", "渡鴉", "隔離區")
    put("abysspact_corvus", "en", "Corvus",
        f"Toss a vial for {ADi}{O}100%{E} physical damage. {O}Contagion{E}: skills inflict {A}4s Plague{E} ({A}2%{E} max HP/s) that jumps between foes; allies near sick foes heal {A}1–3%{E} max HP/s.",
        f"Lob a miasma flask for {ap(pc['q_dmg'], pc['q_ap'])} AoE magic damage, {R}{pc['q_slow']}% slow{E}, and Plague on all foes hit.",
        f"Send his raven to perch on an ally for {A}{secs(pc['w_t'])}s{E}, granting a {S}{pc['w_sh']}{E}+{APi}{S}{pc['w_sh_ap']}%{E} shield while pecking nearby enemies to spread Plague.",
        f"Draw a {A}{secs(pc['r_t'])}s{E} Quarantine zone: bursts for {ap(pc['r_init_dmg'], pc['r_init_ap'])} magic damage with {R}{secs(pc['r_stun'])}s stun{E}, plaguing & slowing foes while healing allies inside.",
        "Miasma Flask", "Plague Raven", "Quarantine")
    put("abysspact_corvus", "ja", "鴉医",
        f"薬瓶を投げ{ADi}{O}100%{E}物理ダメージ。{O}伝染{E}：スキルで{A}4秒{E}疫病（毎秒最大HP{A}2%{E}）を拡散し、病敵近くの味方を毎秒{A}1–3%{E}回復。",
        f"瘴気瓶を投げ範囲に{ap(pc['q_dmg'], pc['q_ap'])}魔法ダメージ、{R}{pc['q_slow']}%スロウ{E}と疫病を付与。",
        f"渡鴉を味方の肩に{A}{secs(pc['w_t'])}秒{E}送り{S}{pc['w_sh']}{E}+{APi}{S}{pc['w_sh_ap']}%{E}シールド付与。毎秒周囲の敵を啄み疫病拡散。",
        f"{A}{secs(pc['r_t'])}秒{E}の隔離区を展開：着弾で{ap(pc['r_init_dmg'], pc['r_init_ap'])}魔法ダメージと{R}{secs(pc['r_stun'])}秒スタン{E}。圏内の敵を疫病減速、味方を回復。",
        "瘴瓶", "渡鴉", "隔離区")
    put("abysspact_corvus", "ko", "까마귀 의사",
        f"약병을 던져 {ADi}{O}100%{E} 물리 피해. {O}전염{E}: 스킬로 {A}4초{E} 역병(초당 최대체력 {A}2%{E})을 퍼뜨리며 감염된 적 근처 아군 초당 {A}1~3%{E} 회복.",
        f"독기 병을 던져 범위에 {ap(pc['q_dmg'], pc['q_ap'])} 마법 피해, {R}{pc['q_slow']}% 둔화{E} 및 역병 감염.",
        f"어깨의 까마귀를 아군에게 {A}{secs(pc['w_t'])}초{E} 보내 {S}{pc['w_sh']}{E}+{APi}{S}{pc['w_sh_ap']}%{E} 보호막 부여. 매초 주변 적을 쪼아 역병 감염.",
        f"{A}{secs(pc['r_t'])}초{E} 격리 구역 선포: {ap(pc['r_init_dmg'], pc['r_init_ap'])} 마법 피해와 {R}{secs(pc['r_stun'])}초 기절{E}. 구역 내 적은 역병·둔화, 아군은 지속 회복.",
        "독기 병", "까마귀", "격리 구역")

    # --- 6. 血月 Bloodmoon ---
    put("abysspact_bloodmoon", "zh-hans", "血月",
        f"人形远程银弩、狼形近战撕咬造成{ADi}{O}100%{E}物理伤害。{O}月相{E}：狼形攻速+{A}{pbm['wolf_as']}%{E}、吸血+{A}{pbm['wolf_vamp']}%{E}。",
        f"人形连射3支穿透银箭各{ad(pbm['q_h_dmg'], pbm['q_h_ad'])}并{R}减速{pbm['q_h_slow']}%{E}；狼形扑杀造成{ad(pbm['q_w_dmg'], pbm['q_w_ad'])}并回血。",
        f"随时切换人狼形态：人变狼长嚎令周围{R}减速{pbm['w_slow']}%{E}；狼变人向后翻滚拉开距离。",
        f"血月升起化身巨狼{A}{secs(pbm['r_t'])}秒{E}：减伤{A}{pbm['r_dr']}%{E}、普攻顺劈周围敌人，长嚎{R}恐惧{secs(pbm['r_fear'])}秒{E}。",
        "银矢/扑杀", "变身", "血月")
    put("abysspact_bloodmoon", "zh-hant", "血月",
        f"人形遠程銀弩、狼形近戰撕咬造成{ADi}{O}100%{E}物理傷害。{O}月相{E}：狼形攻速+{A}{pbm['wolf_as']}%{E}、吸血+{A}{pbm['wolf_vamp']}%{E}。",
        f"人形連射3支穿透銀箭各{ad(pbm['q_h_dmg'], pbm['q_h_ad'])}並{R}減速{pbm['q_h_slow']}%{E}；狼形撲殺造成{ad(pbm['q_w_dmg'], pbm['q_w_ad'])}並回血。",
        f"隨時切換人狼形態：人變狼長嚎令周圍{R}減速{pbm['w_slow']}%{E}；狼變人向後翻滾拉開距離。",
        f"血月升起化身巨狼{A}{secs(pbm['r_t'])}秒{E}：減傷{A}{pbm['r_dr']}%{E}、普攻順劈周圍敵人，長嚎{R}恐懼{secs(pbm['r_fear'])}秒{E}。",
        "銀矢/撲殺", "變身", "血月")
    put("abysspact_bloodmoon", "en", "Bloodmoon",
        f"Ranged silver crossbow as human, melee claws as wolf for {ADi}{O}100%{E} physical damage. {O}Moon Phase{E}: wolf gains {A}+{pbm['wolf_as']}%{E} AS and {A}{pbm['wolf_vamp']}%{E} vamp.",
        f"Human: 3 piercing silver bolts ({ad(pbm['q_h_dmg'], pbm['q_h_ad'])}, {R}{pbm['q_h_slow']}% slow{E}). Wolf: pounce for {ad(pbm['q_w_dmg'], pbm['q_w_ad'])} and heal.",
        f"Shift between human and wolf: wolf shift slows nearby foes by {R}{pbm['w_slow']}%{E}; human shift tumbles backward.",
        f"Rise as a giant wolf for {A}{secs(pbm['r_t'])}s{E}: {A}{pbm['r_dr']}%{E} damage reduction, cleaving autos, and a howl that {R}fears for {secs(pbm['r_fear'])}s{E}.",
        "Silver / Pounce", "Shift", "Blood Moon")
    put("abysspact_bloodmoon", "ja", "血月",
        f"人形態は遠隔銀弩、狼形態は近接爪で{ADi}{O}100%{E}物理。{O}月相{E}：狼形態は攻撃速度+{A}{pbm['wolf_as']}%{E}・吸血{A}{pbm['wolf_vamp']}%{E}。",
        f"人：貫通銀矢3連射（各{ad(pbm['q_h_dmg'], pbm['q_h_ad'])}、{R}{pbm['q_h_slow']}%スロウ{E}）。狼：飛び掛かり{ad(pbm['q_w_dmg'], pbm['q_w_ad'])}＋回復。",
        f"人狼形態を切替：狼化で周囲を{R}{pbm['w_slow']}%スロウ{E}、人化で後方へ前転離脱。",
        f"{A}{secs(pbm['r_t'])}秒{E}巨狼化：被ダメ-{A}{pbm['r_dr']}%{E}、通常攻撃が周囲薙ぎ払い、咆哮で{R}{secs(pbm['r_fear'])}秒恐怖{E}。",
        "銀矢/撲殺", "変身", "血月")
    put("abysspact_bloodmoon", "ko", "혈월",
        f"인간 원거리 석궁·늑대 근접 할퀴기로 {ADi}{O}100%{E} 물리 피해. {O}월상{E}: 늑대 형태 공속+{A}{pbm['wolf_as']}%{E}, 흡혈 {A}{pbm['wolf_vamp']}%{E}.",
        f"인간: 관통 은화살 3연사(발당 {ad(pbm['q_h_dmg'], pbm['q_h_ad'])}, {R}{pbm['q_h_slow']}% 둔화{E}). 늑대: 덮치기 {ad(pbm['q_w_dmg'], pbm['q_w_ad'])} 및 회복.",
        f"인간과 늑대 형태 전환: 늑대 변신 시 주변 {R}{pbm['w_slow']}% 둔화{E}, 인간 복귀 시 뒤로 구르기.",
        f"{A}{secs(pbm['r_t'])}초{E} 거대 늑대 변신: 피해 감소 {A}{pbm['r_dr']}%{E}, 기본 공격 광역 베기, 포효로 {R}{secs(pbm['r_fear'])}초 공포{E}.",
        "은화살/덮치기", "변신", "혈월")

    # --- 7. 入殓 Undertaker ---
    put("abysspact_undertaker", "zh-hans", "入殓",
        f"挥棺撞击造成{ADi}{O}100%{E}物理伤害。{O}棺盾{E}：常驻普攻减伤{A}15%{E}；每{A}8秒{E}获得一层令下次技能伤害-{A}30%{E}的护盾。",
        f"抡棺前砸造成{O}{pu['q_dmg']}{E}+{A}{pu['q_hp']}%最大生命{E}物理伤害并{R}击飞{secs(pu['q_air'])}秒{E}。",
        f"铁链甩出棺材钉地并将自己拽至目标身旁；棺材矗立{A}{secs(pu['w_t'])}秒{E}，周围敌人{R}减速{pu['w_slow']}%{E}。",
        f"将敌方英雄装进棺材扛走{A}{secs(pu['r_carry_t'])}秒{E}（自身移速+{A}{pu['r_ms']}%{E}），随后猛摔造成{O}{pu['r_slam_dmg']}{E}+{A}{pu['r_slam_thp']}%目标最大生命{E}伤害并{R}眩晕{secs(pu['r_stun'])}秒{E}。",
        "落葬", "送行", "入殓")
    put("abysspact_undertaker", "zh-hant", "入殮",
        f"揮棺撞擊造成{ADi}{O}100%{E}物理傷害。{O}棺盾{E}：常駐普攻減傷{A}15%{E}；每{A}8秒{E}獲得一層令下次技能傷害-{A}30%{E}的護盾。",
        f"掄棺前砸造成{O}{pu['q_dmg']}{E}+{A}{pu['q_hp']}%最大生命{E}物理傷害並{R}擊飛{secs(pu['q_air'])}秒{E}。",
        f"鐵鏈甩出棺材釘地並將自己拽至目標身旁；棺材矗立{A}{secs(pu['w_t'])}秒{E}，周圍敵人{R}減速{pu['w_slow']}%{E}。",
        f"將敵方英雄裝進棺材扛走{A}{secs(pu['r_carry_t'])}秒{E}（自身移速+{A}{pu['r_ms']}%{E}），隨後猛摔造成{O}{pu['r_slam_dmg']}{E}+{A}{pu['r_slam_thp']}%目標最大生命{E}傷害並{R}眩暈{secs(pu['r_stun'])}秒{E}。",
        "落葬", "送行", "入殮")
    put("abysspact_undertaker", "en", "Undertaker",
        f"Coffin slam for {ADi}{O}100%{E} physical damage. {O}Coffin Shield{E}: {A}-15%{E} basic attack damage; every {A}8s{E}, reduce the next skill hit by {A}30%{E}.",
        f"Smash his coffin forward for {O}{pu['q_dmg']}{E}+{A}{pu['q_hp']}% max HP{E} physical damage and {R}{secs(pu['q_air'])}s knockup{E}.",
        f"Hurl his chained coffin and pull himself to the target; the planted coffin stands {A}{secs(pu['w_t'])}s{E}, {R}slowing by {pu['w_slow']}%{E}.",
        f"Stuff an enemy champion into his coffin and haul them {A}{secs(pu['r_carry_t'])}s{E} ({A}+{pu['r_ms']}%{E} MS), then slam for {O}{pu['r_slam_dmg']}{E}+{A}{pu['r_slam_thp']}% target max HP{E} and {R}{secs(pu['r_stun'])}s stun{E}.",
        "Burial Slam", "Pallbearer", "Enshroud")
    put("abysspact_undertaker", "ja", "入棺",
        f"棺で殴り{ADi}{O}100%{E}物理。{O}棺盾{E}：通常攻撃被ダメ-{A}15%{E}、{A}8秒{E}毎に次スキル被ダメ-{A}30%{E}。",
        f"棺を叩きつけ{O}{pu['q_dmg']}{E}+{A}最大HP{pu['q_hp']}%{E}物理と{R}{secs(pu['q_air'])}秒ノックアップ{E}。",
        f"鎖付き棺を投げ自身を引き寄せ、{A}{secs(pu['w_t'])}秒{E}立つ棺の周囲を{R}{pu['w_slow']}%スロウ{E}。",
        f"敵英雄を棺に詰め{A}{secs(pu['r_carry_t'])}秒{E}担いで運び（移動+{A}{pu['r_ms']}%{E}）、叩きつけ{O}{pu['r_slam_dmg']}{E}+{A}対象最大HP{pu['r_slam_thp']}%{E}と{R}{secs(pu['r_stun'])}秒スタン{E}。",
        "落葬", "送行", "入棺")
    put("abysspact_undertaker", "ko", "입관",
        f"관으로 들이받아 {ADi}{O}100%{E} 물리 피해. {O}관 방패{E}: 기본 공격 피해 -{A}15%{E}, {A}8초{E}마다 다음 스킬 피해 -{A}30%{E}.",
        f"관을 내려찍어 {O}{pu['q_dmg']}{E}+{A}최대체력 {pu['q_hp']}%{E} 물리 피해와 {R}{secs(pu['q_air'])}초 에어본{E}.",
        f"쇠사슬 관을 던져 자신을 끌어당기며, {A}{secs(pu['w_t'])}초{E}간 꽂힌 관 주변 적 {R}{pu['w_slow']}% 둔화{E}.",
        f"적 챔피언을 관에 가둬 {A}{secs(pu['r_carry_t'])}초{E}간 메고 이동(이속+{A}{pu['r_ms']}%{E}) 후 내려찍어 {O}{pu['r_slam_dmg']}{E}+{A}대상 최대체력 {pu['r_slam_thp']}%{E} 피해 및 {R}{secs(pu['r_stun'])}초 기절{E}.",
        "낙장", "송행", "입관")

    # --- 8. 替身 Effigy ---
    put("abysspact_effigy", "zh-hans", "替身",
        f"布偶甩出飞针造成{ADi}{O}100%{E}物理伤害。{O}扎针{E}：技能命中插入1根银针（最多{A}3根{E}，留{A}5秒{E}），供大招一次拔出。",
        f"扇形甩出银针雨造成{ap(pe['q_dmg'], pe['q_ap'])}魔法伤害、{R}减速{pe['q_slow']}%{E}并扎针；中心穿刺针追加伤害与针数。",
        f"红线连接目标与附近另一名敌方英雄{A}{secs(pe['w_t'])}秒{E}：任一受伤另一人同受{A}40%{E}；拉开过远崩断双双{R}眩晕1秒{E}并受{ap(80, 50)}法伤。",
        f"猛扯大范围内所有敌人身上的银针，每根造成{ap(90, 45)}魔法伤害并{R}减速{pe['r_slow']}%{E}（3根满针爆发极高）。",
        "缝", "同命线", "拆线")
    put("abysspact_effigy", "zh-hant", "替身",
        f"布偶甩出飛針造成{ADi}{O}100%{E}物理傷害。{O}扎針{E}：技能命中插入1根銀針（最多{A}3根{E}，留{A}5秒{E}），供大招一次拔出。",
        f"扇形甩出銀針雨造成{ap(pe['q_dmg'], pe['q_ap'])}魔法傷害、{R}減速{pe['q_slow']}%{E}並扎針；中心穿刺針追加傷害與針數。",
        f"紅線連接目標與附近另一名敵方英雄{A}{secs(pe['w_t'])}秒{E}：任一受傷另一人同受{A}40%{E}；拉開過遠崩斷雙雙{R}眩暈1秒{E}並受{ap(80, 50)}法傷。",
        f"猛扯大範圍內所有敵人身上的銀針，每根造成{ap(90, 45)}魔法傷害並{R}減速{pe['r_slow']}%{E}（3根滿針爆發極高）。",
        "縫", "同命線", "拆線")
    put("abysspact_effigy", "en", "Effigy",
        f"Doll tosses a silver needle for {ADi}{O}100%{E} physical damage. {O}Pinned{E}: skills embed up to {A}3 needles{E} ({A}5s{E}) for her ult to rip out.",
        f"Fan silver needles for {ap(pe['q_dmg'], pe['q_ap'])} magic damage, {R}{pe['q_slow']}% slow{E}, and a needle; center needle pierces for extra damage.",
        f"Bind two enemy champions with red thread for {A}{secs(pe['w_t'])}s{E}: {A}40%{E} damage is shared; pulling apart snaps it for {R}1s double stun{E} and {ap(80, 50)} magic damage.",
        f"Yank all embedded needles in range, dealing {ap(90, 45)} magic damage per needle and a {R}{pe['r_slow']}% slow{E}.",
        "Stitch", "Fate Thread", "Unpick")
    put("abysspact_effigy", "ja", "身代わり",
        f"人形が針を投げ{ADi}{O}100%{E}物理。{O}針刺し{E}：スキル命中で銀針を最大{A}3本{E}（{A}5秒{E}）刺し、必殺で一斉引き抜き。",
        f"扇状に針を放ち{ap(pe['q_dmg'], pe['q_ap'])}魔法ダメージと{R}{pe['q_slow']}%スロウ{E}・針付与。中央針は貫通追撃。",
        f"敵英雄2人を赤い糸で{A}{secs(pe['w_t'])}秒{E}結び被ダメ{A}40%{E}共有。離れすぎると切れ両者{R}1秒スタン{E}＋{ap(80, 50)}魔法。",
        f"広範囲の針を一気に引き抜き、1本につき{ap(90, 45)}魔法ダメージと{R}{pe['r_slow']}%スロウ{E}。",
        "縫合", "同命糸", "解糸")
    put("abysspact_effigy", "ko", "대신",
        f"인형이 바늘을 던져 {ADi}{O}100%{E} 물리 피해. {O}바늘꽂기{E}: 스킬 적중 시 최대 {A}3개{E}({A}5초{E}) 꽂아 궁극기로 한 번에 뽑음.",
        f"부채꼴 바늘비로 {ap(pe['q_dmg'], pe['q_ap'])} 마법 피해, {R}{pe['q_slow']}% 둔화{E} 및 바늘 부여. 중앙 관통 바늘 추가 피해.",
        f"적 챔피언 둘을 붉은 실로 {A}{secs(pe['w_t'])}초{E} 연결해 피해 {A}40%{E} 공유. 멀어져 끊어지면 둘 다 {R}1초 기절{E} 및 {ap(80, 50)} 마법 피해.",
        f"광범위 모든 바늘을 잡아당겨 개당 {ap(90, 45)} 마법 피해와 {R}{pe['r_slow']}% 둔화{E}.",
        "바느질", "동명실", "실뜯기")

    # --- 9. 七弹 Sevenfold ---
    put("abysspact_sevenfold", "zh-hans", "七弹",
        f"魔弹枪射击造成{ADi}{O}100%{E}物理伤害。{O}第七颗{E}：7发一轮，第7发拐弯必中随机敌方英雄造成{ad(ps['p_true_dmg'], ps['p_true_ad'])}真实伤害，自损{A}8%{E}当前血并装弹1.2秒。",
        f"连开三枪每发{ad(ps['q_dmg'], ps['q_ad'])}物理伤害，消耗3发弹仓更快逼出第七颗魔弹。",
        f"向后翻滚拉开距离，立刻装满弹仓并将下一发直接置为第七颗深渊魔弹。",
        f"前方扇形连开七枪：前6发各自寻敌造成{ad(ps['r_dmg'], ps['r_ad'])}物理伤害，第7发必为深渊拐弯真伤魔弹。",
        "连发", "装弹", "七发齐射")
    put("abysspact_sevenfold", "zh-hant", "七彈",
        f"魔彈槍射擊造成{ADi}{O}100%{E}物理傷害。{O}第七顆{E}：7發一輪，第7發拐彎必中隨機敵方英雄造成{ad(ps['p_true_dmg'], ps['p_true_ad'])}真實傷害，自損{A}8%{E}當前血並裝彈1.2秒。",
        f"連開三槍每發{ad(ps['q_dmg'], ps['q_ad'])}物理傷害，消耗3發彈倉更快逼出第七顆魔彈。",
        f"向後翻滾拉開距離，立刻裝滿彈倉並將下一發直接置為第七顆深淵魔彈。",
        f"前方扇形連開七槍：前6發各自尋敵造成{ad(ps['r_dmg'], ps['r_ad'])}物理傷害，第7發必為深淵拐彎真傷魔彈。",
        "連發", "裝彈", "七發齊射")
    put("abysspact_sevenfold", "en", "Sevenfold",
        f"Freeshooter rifle for {ADi}{O}100%{E} physical damage. {O}7th Bullet{E}: every 7th round curves into a random enemy champion for {ad(ps['p_true_dmg'], ps['p_true_ad'])} true damage, burning {A}8%{E} current HP then reloading 1.2s.",
        f"Fire three rapid shots ({ad(ps['q_dmg'], ps['q_ad'])} physical each), spending 3 rounds toward the 7th bullet.",
        f"Tumble backward and immediately chamber the 7th Abyss Bullet as his very next shot.",
        f"Unleash a 7-shot salvo: 6 tracking rounds ({ad(ps['r_dmg'], ps['r_ad'])} physical each) capped by a guaranteed 7th Abyss Bullet.",
        "Triple Volley", "Chamber", "Sevenfold Salvo")
    put("abysspact_sevenfold", "ja", "七弾",
        f"魔弾銃で{ADi}{O}100%{E}物理。{O}七発目{E}：7発毎の最終弾がランダムな敵英雄へ曲がり必中し{ad(ps['p_true_dmg'], ps['p_true_ad'])}確定ダメージ、現在HP{A}8%{E}消費後1.2秒装填。",
        f"3連射（各{ad(ps['q_dmg'], ps['q_ad'])}物理）。弾を3発消費し七発目を早める。",
        f"後方へ前転離脱し、次の一発を即座に七発目の深淵魔弾へ装填する。",
        f"前方へ7連射：6発が敵を追尾（各{ad(ps['r_dmg'], ps['r_ad'])}物理）、7発目は必ず深淵魔弾となる。",
        "連発", "装填", "七発斉射")
    put("abysspact_sevenfold", "ko", "칠탄",
        f"마탄총 사격 {ADi}{O}100%{E} 물리 피해. {O}일곱 번째 탄환{E}: 7발째는 무작위 적 챔피언에게 휘어져 {ad(ps['p_true_dmg'], ps['p_true_ad'])} 고정 피해, 현재 체력 {A}8%{E} 소모 후 1.2초 재장전.",
        f"3연발 사격(발당 {ad(ps['q_dmg'], ps['q_ad'])} 물리), 탄환 3발 소모로 일곱 번째 탄환 가속.",
        f"뒤로 구르며 즉시 다음 한 발을 일곱 번째 심연 마탄으로 장전.",
        f"전방 7연사: 앞 6발은 적을 추적해 각 {ad(ps['r_dmg'], ps['r_ad'])} 물리 피해, 7발째는 심연 마탄 발사.",
        "연발", "장전", "칠발 일제사격")

    # --- 10. 烛灵 Vesper ---
    put("abysspact_vesper", "zh-hans", "烛灵",
        f"放出鬼火造成{ADi}{O}100%{E}物理伤害。{O}烛冠{E}：周围每阵亡1名英雄点亮1支蜡烛（上限{A}5支{E}），每支使治疗与护盾+{A}10%{E}。",
        f"鬼火连结友军{A}{secs(pv['q_t'])}秒{E}：移速+{A}{pv['q_ms']}%{E}、每秒回复{ap(pv['q_heal'], pv['q_heal_ap'])}，结束赋予{S}{pv['q_sh']}{E}+{APi}{S}{pv['q_sh_ap']}%{E}护盾。",
        f"放出尖叫亡魂直线穿透，造成{ap(pv['w_dmg'], pv['w_ap'])}魔法伤害并{R}恐惧{secs(pv['w_fear'])}秒{E}。",
        f"唤回10秒内阵亡队友化身魂体再战{A}8秒{E}（减伤50%禁疗），期间己方拿到击杀即{A}真复活{E}；无阵亡队友则全体加盾。",
        "引路", "惊魂", "回魂")
    put("abysspact_vesper", "zh-hant", "燭靈",
        f"放出鬼火造成{ADi}{O}100%{E}物理傷害。{O}燭冠{E}：周圍每陣亡1名英雄點亮1支蠟燭（上限{A}5支{E}），每支使治療與護盾+{A}10%{E}。",
        f"鬼火連結友軍{A}{secs(pv['q_t'])}秒{E}：移速+{A}{pv['q_ms']}%{E}、每秒回復{ap(pv['q_heal'], pv['q_heal_ap'])}，結束賦予{S}{pv['q_sh']}{E}+{APi}{S}{pv['q_sh_ap']}%{E}護盾。",
        f"放出尖叫亡魂直線穿透，造成{ap(pv['w_dmg'], pv['w_ap'])}魔法傷害並{R}恐懼{secs(pv['w_fear'])}秒{E}。",
        f"喚回10秒內陣亡隊友化身魂體再戰{A}8秒{E}（減傷50%禁療），期間己方拿到擊殺即{A}真復活{E}；無陣亡隊友則全體加盾。",
        "引路", "驚魂", "回魂")
    put("abysspact_vesper", "en", "Vesper",
        f"Launch a spirit wisp for {ADi}{O}100%{E} physical damage. {O}Candle Crown{E}: each nearby champion death lights a candle (max {A}5{E}), boosting heals & shields by {A}+10%{E} each.",
        f"Link a wisp to an ally for {A}{secs(pv['q_t'])}s{E}: {A}+{pv['q_ms']}%{E} MS, {ap(pv['q_heal'], pv['q_heal_ap'])} heal/s, ending with a {S}{pv['q_sh']}{E}+{APi}{S}{pv['q_sh_ap']}%{E} shield.",
        f"Send a screaming wraith forward in a line for {ap(pv['w_dmg'], pv['w_ap'])} magic damage and {R}{secs(pv['w_fear'])}s fear{E}.",
        f"Recall a recently fallen ally in Spirit Form for {A}8s{E} (50% DR, no healing); any team kill grants {A}true revival{E}. Otherwise shields all nearby allies.",
        "Soul Guide", "Wraith Shriek", "Soul Recall")
    put("abysspact_vesper", "ja", "燭霊",
        f"鬼火を飛ばし{ADi}{O}100%{E}物理。{O}燭冠{E}：周囲の英雄死亡毎に蝋燭を点灯（最大{A}5本{E}）、1本につき回復・シールド+{A}10%{E}。",
        f"鬼火で味方を{A}{secs(pv['q_t'])}秒{E}結び移動+{A}{pv['q_ms']}%{E}、毎秒{ap(pv['q_heal'], pv['q_heal_ap'])}回復、終了時{S}{pv['q_sh']}{E}+{APi}{S}{pv['q_sh_ap']}%{E}シールド。",
        f"叫ぶ亡霊が直線貫通し{ap(pv['w_dmg'], pv['w_ap'])}魔法ダメージと{R}{secs(pv['w_fear'])}秒恐怖{E}。",
        f"10秒内に倒れた味方を魂体で{A}8秒{E}蘇生（被ダメ半減・回復不可）、味方の撃破で{A}真復活{E}。該当なし時は周囲の味方へシールド。",
        "引導", "驚魂", "回魂")
    put("abysspact_vesper", "ko", "촉령",
        f"도깨비불로 {ADi}{O}100%{E} 물리 피해. {O}촛불 왕관{E}: 주변 챔피언 사망 시 촛불 점등(최대 {A}5개{E}), 개당 치유·보호막 +{A}10%{E}.",
        f"아군에게 {A}{secs(pv['q_t'])}초{E} 연결해 이속+{A}{pv['q_ms']}%{E}, 매초 {ap(pv['q_heal'], pv['q_heal_ap'])} 회복, 종료 시 {S}{pv['q_sh']}{E}+{APi}{S}{pv['q_sh_ap']}%{E} 보호막.",
        f"비명 지르는 망령이 직선 관통하며 {ap(pv['w_dmg'], pv['w_ap'])} 마법 피해와 {R}{secs(pv['w_fear'])}초 공포{E}.",
        f"10초 내 전사한 아군을 영혼체로 {A}8초{E} 소환(피해 반감·치유 불가), 팀 킬 시 {A}완전 부활{E}. 대상 없으면 주변 아군 보호막.",
        "인도", "경혼", "회혼")

    # --- 11. 蜕甲 Carapace ---
    put("abysspact_carapace", "zh-hans", "蜕甲",
        f"虫刃交叉斩击造成{ADi}{O}100%{E}物理伤害。{O}蜕壳{E}：每条命可蜕两次（甲→虫→羽），濒死回{A}40%{E}血并留空壳嘲讽自爆，最大血渐减而攻速移速大涨。",
        f"前冲刺螯造成{ad(pca['q_dmg'], pca['q_ad'])}物理伤害并{R}减速{pca['q_slow']}%{E}；第三形态「羽」变为远距离飞扑。",
        f"敲响甲壳震伤周围敌人{ad(pca['w_dmg'], pca['w_ad'])}，命中敌方英雄时回复自身生命。",
        f"立即主动蜕壳炸开旧甲，对周围造成{ad(pca['r_dmg'], pca['r_ad'])}伤害并{R}击飞{secs(pca['r_air'])}秒{E}、获得{A}4秒+{pca['r_as']}%{E}攻速；第三形态改为长距飞扑击飞。",
        "刺螯", "甲鸣", "羽化")
    put("abysspact_carapace", "zh-hant", "蛻甲",
        f"蟲刃交叉斬擊造成{ADi}{O}100%{E}物理傷害。{O}蛻殼{E}：每條命可蛻兩次（甲→蟲→羽），瀕死回{A}40%{E}血並留空殼嘲諷自爆，最大血漸減而攻速移速大漲。",
        f"前衝刺螯造成{ad(pca['q_dmg'], pca['q_ad'])}物理傷害並{R}減速{pca['q_slow']}%{E}；第三形態「羽」變為遠距離飛撲。",
        f"敲響甲殼震傷周圍敵人{ad(pca['w_dmg'], pca['w_ad'])}，命中敵方英雄時回復自身生命。",
        f"立即主動蛻殼炸開舊甲，對周圍造成{ad(pca['r_dmg'], pca['r_ad'])}傷害並{R}擊飛{secs(pca['r_air'])}秒{E}、獲得{A}4秒+{pca['r_as']}%{E}攻速；第三形態改為長距飛撲擊飛。",
        "刺螯", "甲鳴", "羽化")
    put("abysspact_carapace", "en", "Carapace",
        f"Scythe slash for {ADi}{O}100%{E} physical damage. {O}Molt{E}: cheats death twice per life (Armor -> Bug -> Winged), healing to {A}40%{E} HP while leaving a taunting bomb shell; loses max HP for AS & MS.",
        f"Lunge forward for {ad(pca['q_dmg'], pca['q_ad'])} physical damage and {R}{pca['q_slow']}% slow{E}; becomes a long winged dive in Form 3.",
        f"Strike his shell to shock nearby foes for {ad(pca['w_dmg'], pca['w_ad'])} physical damage, healing on champion hits.",
        f"Actively molt to shatter his shell for {ad(pca['r_dmg'], pca['r_ad'])} AoE damage, {R}{secs(pca['r_air'])}s knockup{E}, and {A}+{pca['r_as']}% AS{E} for 4s; Form 3 dives from afar.",
        "Chelicera", "Carapace Ring", "Ecdysis")
    put("abysspact_carapace", "ja", "蛻甲",
        f"虫刃で{ADi}{O}100%{E}物理。{O}脱皮{E}：1命で2回脱皮（甲→虫→羽）、致死時にHP{A}40%{E}回復し挑発自爆する空殻を残す。最大HP低下の代償に速度激増。",
        f"突進し{ad(pca['q_dmg'], pca['q_ad'])}物理と{R}{pca['q_slow']}%スロウ{E}。第3形態では長距離飛び掛かりへ変化。",
        f"甲殻を鳴らし周囲へ{ad(pca['w_dmg'], pca['w_ad'])}物理、英雄命中で自己回復。",
        f"即座に脱皮爆発し周囲に{ad(pca['r_dmg'], pca['r_ad'])}物理と{R}{secs(pca['r_air'])}秒ノックアップ{E}、4秒間攻撃速度+{A}{pca['r_as']}%{E}。第3形態は遠距離急襲。",
        "刺螯", "甲鳴", "羽化")
    put("abysspact_carapace", "ko", "탈갑",
        f"벌레 칼날로 {ADi}{O}100%{E} 물리 피해. {O}탈피{E}: 목숨당 2회 탈피(갑→충→우), 치명타 시 체력 {A}40%{E} 회복하며 도발 자폭 빈 껍질 생성. 최대 체력 감소 대신 공속·이속 급증.",
        f"돌진해 {ad(pca['q_dmg'], pca['q_ad'])} 물리 피해와 {R}{pca['q_slow']}% 둔화{E}. 3형태에서는 장거리 도약.",
        f"갑각을 울려 주변에 {ad(pca['w_dmg'], pca['w_ad'])} 물리 피해 및 챔피언 적중 시 자가 치유.",
        f"즉시 탈피 폭발로 {ad(pca['r_dmg'], pca['r_ad'])} 광역 피해, {R}{secs(pca['r_air'])}초 에어본{E}, 4초간 공속+{A}{pca['r_as']}%{E}. 3형태는 원거리 강습.",
        "집게 찌르기", "갑각 울림", "우화")

    # --- 12. 附骨 Leech ---
    put("abysspact_leech", "zh-hans", "附骨",
        f"钩爪撕挠造成{ADi}{O}100%{E}物理伤害。{O}附骨之疽{E}：寄生宿主期间不可选中并持续吸取最大生命治己，但宿主挨打时自身同步承受{A}25%{E}伤害。",
        f"扑向目标造成{ap(pl['q_dmg'], pl['q_ap'])}法伤并附着敌方英雄背上{A}3秒{E}减速吸血；宿主阵亡自动跳向下一名敌方英雄。",
        f"向目标注入深渊毒液造成{ap(pl['w_dmg'], pl['w_ap'])}法伤并{R}沉默{secs(pl['w_sil'])}秒{E}；附着期间对宿主沉默延长至{R}{secs(pl['w_sil_att'])}秒{E}。",
        f"裂成{A}5只{E}小水蛭扑向周围敌方英雄群吸{A}3秒{E}（不可选中、每宿主分担10%伤害），结束后聚回本体并回复全部所吸血量。",
        "扑附", "蚀髓", "万蛭")
    put("abysspact_leech", "zh-hant", "附骨",
        f"鉤爪撕撓造成{ADi}{O}100%{E}物理傷害。{O}附骨之疽{E}：寄生宿主期間不可選中並持續吸取最大生命治己，但宿主挨打時自身同步承受{A}25%{E}傷害。",
        f"撲向目標造成{ap(pl['q_dmg'], pl['q_ap'])}法傷並附著敵方英雄背上{A}3秒{E}減速吸血；宿主陣亡自動跳向下一名敵方英雄。",
        f"向目標注入深淵毒液造成{ap(pl['w_dmg'], pl['w_ap'])}法傷並{R}沉默{secs(pl['w_sil'])}秒{E}；附著期間對宿主沉默延長至{R}{secs(pl['w_sil_att'])}秒{E}。",
        f"裂成{A}5隻{E}小水蛭撲向周圍敵方英雄群吸{A}3秒{E}（不可選中、每宿主分擔10%傷害），結束後聚回本體並回復全部所吸血量。",
        "撲附", "蝕髓", "萬蛭")
    put("abysspact_leech", "en", "Leech",
        f"Hook claw for {ADi}{O}100%{E} physical damage. {O}Bone Parasite{E}: while clinging to an enemy he is untargetable and drains max HP to heal, but suffers {A}25%{E} of damage dealt to his host.",
        f"Pounce for {ap(pl['q_dmg'], pl['q_ap'])} magic damage and cling to an enemy champion for {A}3s{E}, slowing & draining; jumps to a nearby foe if host dies.",
        f"Inject marrow venom for {ap(pl['w_dmg'], pl['w_ap'])} magic damage and {R}{secs(pl['w_sil'])}s silence{E} ({R}{secs(pl['w_sil_att'])}s{E} while attached).",
        f"Split into {A}5 mini-leeches{E} draining enemy champions for {A}3s{E} while untargetable (10% shared pain each), then reform and heal for all drained HP.",
        "Latch", "Marrow Bite", "Swarm of Five")
    put("abysspact_leech", "ja", "附骨",
        f"鉤爪で{ADi}{O}100%{E}物理。{O}附骨の疽{E}：宿主に寄生中は対象指定不可で最大HPを吸収回復するが、宿主の被ダメ{A}25%{E}を自身も受ける。",
        f"飛び付き{ap(pl['q_dmg'], pl['q_ap'])}魔法＋敵英雄の背中へ{A}3秒{E}寄生し減速吸収。宿主撃破で次の敵へ跳躍。",
        f"毒を注入し{ap(pl['w_dmg'], pl['w_ap'])}魔法と{R}{secs(pl['w_sil'])}秒沈黙{E}（寄生中は{R}{secs(pl['w_sil_att'])}秒{E}）。",
        f"{A}5匹{E}の小蛭に分裂し敵英雄へ{A}3秒{E}群がり吸収（各被ダメ10%共有）、合体時に吸収量を全回復。",
        "撲附", "蝕髄", "万蛭")
    put("abysspact_leech", "ko", "부골",
        f"갈고리 발톱으로 {ADi}{O}100%{E} 물리 피해. {O}부골지저{E}: 숙주 기생 중 대상 지정 불가 및 최대 체력 흡혈, 단 숙주 피해의 {A}25%{E}를 함께 받음.",
        f"덮쳐 {ap(pl['q_dmg'], pl['q_ap'])} 마법 피해 후 적 챔피언 등에 {A}3초{E} 기생(둔화·흡혈). 숙주 사망 시 인접 적에게 도약.",
        f"독을 주입해 {ap(pl['w_dmg'], pl['w_ap'])} 마법 피해와 {R}{secs(pl['w_sil'])}초 침묵{E}(기생 중 {R}{secs(pl['w_sil_att'])}초{E}).",
        f"{A}5마리{E} 작은 거머리로 분열해 {A}3초{E}간 적 챔피언들을 흡혈(숙주당 10% 피해 공유) 후 합체하며 총 흡혈량 회복.",
        "기생 도약", "골수 침식", "만질")

    # --- 13. 千蛾 Noctua ---
    put("abysspact_noctua", "zh-hans", "千蛾",
        f"飞蛾扑火造成{ADi}{O}100%{E}物理伤害。{O}散身{E}：1秒受创超{A}12%{E}最大血时碎成蛾群不可选中并瞬移撤离，聚身后{R}1.25秒{E}无法放技能。",
        f"放出{A}6只{E}飞蛾自动寻敌各造成{ap(pn['q_dmg'], pn['q_ap'])}魔法伤害并叠加鳞粉（每层减速10%，上限3层）。",
        f"飞蛾裹住敌方英雄结茧{R}眩晕{secs(pn['w_stun'])}秒{E}并造成法伤；破茧飞回时治疗自身。",
        f"整个人化作{A}3.5秒{E}不可选中蛾群风暴持续灼烧并叠鳞粉，结束聚身时爆开鳞粉令周围敌人{R}沉默{secs(pn['r_sil'])}秒{E}。",
        "蛾群", "织茧", "万蛾")
    put("abysspact_noctua", "zh-hant", "千蛾",
        f"飛蛾撲火造成{ADi}{O}100%{E}物理傷害。{O}散身{E}：1秒受創超{A}12%{E}最大血時碎成蛾群不可選中並瞬移撤離，聚身後{R}1.25秒{E}無法放技能。",
        f"放出{A}6隻{E}飛蛾自動尋敵各造成{ap(pn['q_dmg'], pn['q_ap'])}魔法傷害並疊加鱗粉（每層減速10%，上限3層）。",
        f"飛蛾裹住敵方英雄結繭{R}眩暈{secs(pn['w_stun'])}秒{E}並造成法傷；破繭飛回時治療自身。",
        f"整個人化作{A}3.5秒{E}不可選中蛾群風暴持續灼燒並疊鱗粉，結束聚身時爆開鱗粉令周圍敵人{R}沉默{secs(pn['r_sil'])}秒{E}。",
        "蛾群", "織繭", "萬蛾")
    put("abysspact_noctua", "en", "Noctua",
        f"Send a fluttering moth for {ADi}{O}100%{E} physical damage. {O}Scatter{E}: taking >{A}12%{E} max HP in 1s scatters her untargetably away (12s CD), silencing her skills for {R}1.25s{E} on reform.",
        f"Release {A}6 homing moths{E} for {ap(pn['q_dmg'], pn['q_ap'])} magic damage each, stacking Scales (-10% MS per stack, up to 3).",
        f"Wrap an enemy champion in a moth cocoon for {R}{secs(pn['w_stun'])}s stun{E}; moths return on break to heal her.",
        f"Become an untargetable moth storm for {A}3.5s{E} scorching and scaling foes, then reform in a dust shockwave that {R}silences for {secs(pn['r_sil'])}s{E}.",
        "Moth Swarm", "Cocoon", "Myriad Storm")
    put("abysspact_noctua", "ja", "千蛾",
        f"飛蛾で{ADi}{O}100%{E}物理。{O}散身{E}：1秒で最大HP{A}12%{E}超の被弾時、対象指定不可の蛾群となり離脱（CD12秒）、再集結後{R}1.25秒{E}スキル不可。",
        f"{A}6匹{E}の蛾を放ち各{ap(pn['q_dmg'], pn['q_ap'])}魔法と鱗粉を蓄積（最大3層、1層10%スロウ）。",
        f"敵英雄を繭で包み{R}{secs(pn['w_stun'])}秒スタン{E}。破繭時に蛾が戻り自己回復。",
        f"{A}3.5秒{E}対象指定不可の蛾嵐となり周囲を継続魔法攻撃＆鱗粉付与、終了時に衝撃波で周囲を{R}{secs(pn['r_sil'])}秒沈黙{E}。",
        "蛾群", "織繭", "万蛾")
    put("abysspact_noctua", "ko", "천아",
        f"나방 공격 {ADi}{O}100%{E} 물리 피해. {O}산신{E}: 1초 내 최대 체력 {A}12%{E} 초과 피해 시 대상 지정 불가로 흩어져 후퇴(12초), 재결합 후 {R}1.25초{E} 스킬 불가.",
        f"나방 {A}6마리{E}를 날려 각 {ap(pn['q_dmg'], pn['q_ap'])} 마법 피해와 인분 중첩(층당 둔화 10%, 최대 3층).",
        f"적 챔피언을 고치로 감싸 {R}{secs(pn['w_stun'])}초 기절{E}, 고치가 깨질 때 나방이 돌아와 회복.",
        f"{A}3.5초{E}간 대상 지정 불가 나방 폭풍이 되어 지속 마법 피해와 인분 부여, 종료 시 광역 {R}{secs(pn['r_sil'])}초 침묵{E}.",
        "나방 떼", "고치 엮기", "만아 폭풍")

    # --- 14. 沉锚 Anchor ---
    put("abysspact_anchor", "zh-hans", "沉锚",
        f"拖锚发射锚链弹（移速+{A}10%{E}）；下锚变炮台射程暴涨至{A}9万{E}、每炮溅射周围{A}60%{E}伤害且{O}压舱{E}免疫击退击飞拉拽。",
        f"抡起铁锚链横扫周围敌人，造成{ad(pa['q_dmg'], pa['q_ad'])}物理伤害并将近身敌人{R}击退{E}（下锚期间也可施放）。",
        f"在拖锚机动与下锚炮台姿态间切换：下锚无法移动但射程与溅射巨幅强化，遇险随时起锚撤离。",
        f"立刻架炮向超远区域连轰{A}6发{E}沉船巨炮，每发造成{ad(pa['r_dmg'], pa['r_ad'])}范围物理伤害并{R}击飞{secs(pa['r_air'])}秒{E}。",
        "横扫", "下锚/起锚", "沉船炮")
    put("abysspact_anchor", "zh-hant", "沉錨",
        f"拖錨發射錨鏈彈（移速+{A}10%{E}）；下錨變砲台射程暴漲至{A}9萬{E}、每砲濺射周圍{A}60%{E}傷害且{O}壓艙{E}免疫擊退擊飛拉拽。",
        f"掄起鐵錨鏈橫掃周圍敵人，造成{ad(pa['q_dmg'], pa['q_ad'])}物理傷害並將近身敵人{R}擊退{E}（下錨期間也可施放）。",
        f"在拖錨機動與下錨砲台姿態間切換：下錨無法移動但射程與濺射巨幅強化，遇險隨時起錨撤離。",
        f"立刻架砲向超遠區域連轟{A}6發{E}沉船巨砲，每發造成{ad(pa['r_dmg'], pa['r_ad'])}範圍物理傷害並{R}擊飛{secs(pa['r_air'])}秒{E}。",
        "橫掃", "下錨/起錨", "沉船砲")
    put("abysspact_anchor", "en", "Anchor",
        f"Drag mode shoots chain bolts ({A}+10%{E} MS); Siege mode anchors for {A}90k range{E}, {A}60%{E} splash shells, and {O}Ballast{E} immunity to displacement.",
        f"Swing her iron anchor chain around herself for {ad(pa['q_dmg'], pa['q_ad'])} physical damage and {R}knockback{E} (castable while anchored).",
        f"Switch between Drag mobility and Siege turret mode (massive range & splash, immobile until raised).",
        f"Plant anchor and fire {A}6 sunken cannon shells{E} across long range, each dealing {ad(pa['r_dmg'], pa['r_ad'])} AoE physical damage and {R}{secs(pa['r_air'])}s knockup{E}.",
        "Chain Sweep", "Drop / Weigh", "Sunken Broadside")
    put("abysspact_anchor", "ja", "沈錨",
        f"牽引時は鎖弾（移動+{A}10%{E}）、投錨時は射程{A}9万{E}の砲台となり周囲{A}60%{E}範囲爆風＋{O}バラスト{E}で強制移動無効。",
        f"鎖を振り回し周囲へ{ad(pa['q_dmg'], pa['q_ad'])}物理と{R}ノックバック{E}（投錨中も使用可）。",
        f"牽引形態と投錨砲台形態を切替。投錨中は移動不可だが射程と範囲火力が劇的に上昇。",
        f"遠距離へ巨砲を{A}6連射{E}し、各弾{ad(pa['r_dmg'], pa['r_ad'])}範囲物理と{R}{secs(pa['r_air'])}秒ノックアップ{E}。",
        "鎖薙ぎ", "投錨/抜錨", "沈船砲")
    put("abysspact_anchor", "ko", "침묘",
        f"견인 시 사슬탄(이속+{A}10%{E}), 투묘 시 사거리 {A}9만{E} 포대로 전환해 주변 {A}60%{E} 광역 폭발 및 {O}평형수{E} 강제 이동 면역.",
        f"닻 사슬을 휘둘러 주변에 {ad(pa['q_dmg'], pa['q_ad'])} 물리 피해와 {R}밀쳐내기{E}(투묘 중 사용 가능).",
        f"기동 견인 태세와 고정 포대 태세를 전환. 투묘 시 이동 불가 대신 사거리·광역 화력 급증.",
        f"초장거리로 거포 {A}6연발{E} 포격, 발당 {ad(pa['r_dmg'], pa['r_ad'])} 광역 물리 피해와 {R}{secs(pa['r_air'])}초 에어본{E}.",
        "사슬 휘두르기", "투묘/양묘", "침선포")

    # --- 15. 返照 Hourglass ---
    put("abysspact_hourglass", "zh-hans", "返照",
        f"弹出流沙光粒造成{ADi}{O}100%{E}物理伤害。{O}老去{E}：放回光+1层、倒流+3层（上限10层，每层最大血-2.5%移速-2%且白发递增），阵亡复活重返年少。",
        f"为友方英雄打上{A}3秒{E}回光印记：到期将血量倒回打印记瞬间（只增不减），期间受致命伤则立刻倒血免死！",
        f"停摆目标区域时间，对范围内敌人造成{ap(ph['w_dmg'], ph['w_ap'])}魔法伤害并{R}眩晕{secs(ph['w_stun'])}秒{E}。",
        f"翻转沙漏灯，令大范围内所有存活友方英雄瞬间倒回{A}3秒前{E}的位置与血量（只增不减，老去+3层）。",
        "回光", "停摆", "倒流")
    put("abysspact_hourglass", "zh-hant", "返照",
        f"彈出流沙光粒造成{ADi}{O}100%{E}物理傷害。{O}老去{E}：放回光+1層、倒流+3層（上限10層，每層最大血-2.5%移速-2%且白髮遞增），陣亡復活重返年少。",
        f"為友方英雄打上{A}3秒{E}回光印記：到期將血量倒回打印記瞬間（只增不減），期間受致命傷則立刻倒血免死！",
        f"停擺目標區域時間，對範圍內敵人造成{ap(ph['w_dmg'], ph['w_ap'])}魔法傷害並{R}眩暈{secs(ph['w_stun'])}秒{E}。",
        f"翻轉沙漏燈，令大範圍內所有存活友方英雄瞬間倒回{A}3秒前{E}的位置與血量（只增不減，老去+3層）。",
        "回光", "停擺", "倒流")
    put("abysspact_hourglass", "en", "Hourglass",
        f"Flick glowing sand for {ADi}{O}100%{E} physical damage. {O}Aging{E}: Q adds 1 stack, R adds 3 (cap 10, -2.5% max HP & -2% MS each, graying/whitening her hair); death restores her youth.",
        f"Mark an ally for {A}3s{E}: rewinds their HP upward to when marked, triggering immediately to save them from lethal damage.",
        f"Halt time in an area for {ap(ph['w_dmg'], ph['w_ap'])} magic damage and {R}{secs(ph['w_stun'])}s stun{E}.",
        f"Invert her hourglass lantern to rewind every living ally in wide range back to their position and HP from {A}3s ago{E} (never reducing HP; +3 Age).",
        "Afterglow", "Stasis Gear", "Turn Back")
    put("abysspact_hourglass", "ja", "返照",
        f"流砂で{ADi}{O}100%{E}物理。{O}老い{E}：回光+1・倒流+3層（最大10、1層毎に最大HP-2.5%・移動-2%・白髪化）、倒れて復活すると若返る。",
        f"味方英雄に{A}3秒{E}の回光印を付与：終了時に印付与時のHPへ巻き戻し（減少なし）、致死時は即座に巻き戻し救命！",
        f"指定範囲の時を止め{ap(ph['w_dmg'], ph['w_ap'])}魔法と{R}{secs(ph['w_stun'])}秒スタン{E}。",
        f"砂時計灯を反転し、広範囲の生存味方全員を{A}3秒前{E}の位置とHPへ巻き戻す（減少なし、老い+3層）。",
        "回光", "停擺", "倒流")
    put("abysspact_hourglass", "ko", "반조",
        f"모래빛 사격 {ADi}{O}100%{E} 물리 피해. {O}노화{E}: 회광+1·역류+3중첩(최대 10, 층당 최대체력-2.5%·이속-2%, 백발화), 사망 부활 시 젊음 회복.",
        f"아군 챔피언에게 {A}3초{E} 회광 표식: 종료 시 표식 시점 체력으로 되돌리며(감소 없음), 치명 피해 시 즉시 되돌려 구출!",
        f"지정 구역 시간을 멈춰 {ap(ph['w_dmg'], ph['w_ap'])} 마법 피해와 {R}{secs(ph['w_stun'])}초 기절{E}.",
        f"모래시계 등을 뒤집어 광범위 생존 아군 전원을 {A}3초 전{E} 위치와 체력으로 되돌림(감소 없음, 노화+3).",
        "회광", "시간 정지", "시간 역류")

    # Verify tooltip length limits strictly!
    bad = []
    for lang in TOOLTIP_MAX:
        for cid, d in desc[lang].items():
            for slot in ("attack", "skill", "skill2", "ult"):
                L = shown_length(d[slot])
                if L > TOOLTIP_MAX[lang]:
                    bad.append(f"{lang}/{cid}.{slot}: {L} > {TOOLTIP_MAX[lang]}")
    if bad:
        sys.exit("TOOLTIP LENGTH EXCEEDED:\n" + "\n".join(bad))

    i18n = {lang: {"description": desc[lang], "skill_name": skn[lang]} for lang in desc}
    save(os.path.join(MOD, "text", "champion.i18n"), i18n)
    print(f"wrote text/champion.i18n (5 langs x 15 heroes, all under TOOLTIP_MAX!)")


def kit_sounds(cid):
    found = set()
    data = json.loads(open(lp(os.path.join(MOD, "champion", f"{cid}.data_champion")), "rb").read().decode("utf-8-sig"))

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") in ("Sfx", "TargetSfx"):
                found.add(o["name"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)
    return found


def dll_sounds(cid, rs_name):
    src = open(lp(os.path.join(REPO, "addons", "abysspact", "src", f"{rs_name}.rs")), encoding="utf-8").read()
    found = set(re.findall(r'play_sfx\("([^"]+)"', src))
    # Voice cues played via Voice controller
    for cue in ("v_start", "v_ult", "v_kill", "v_respawn", "v_dead"):
        found.add(f"{cid}_{cue}")
    return found


def write_sounds_and_overrides():
    rs_map = {
        "abysspact_oathbreaker": "oathbreaker",
        "abysspact_faceless": "faceless",
        "abysspact_whisperer": "whisperer",
        "abysspact_bonebow": "bonebow",
        "abysspact_corvus": "corvus",
        "abysspact_bloodmoon": "bloodmoon",
        "abysspact_undertaker": "undertaker",
        "abysspact_effigy": "effigy",
        "abysspact_sevenfold": "sevenfold",
        "abysspact_vesper": "vesper",
        "abysspact_carapace": "carapace",
        "abysspact_leech": "leech",
        "abysspact_noctua": "noctua",
        "abysspact_anchor": "anchor",
        "abysspact_hourglass": "hourglass",
    }
    ov = {
        "asset/base/text/champion": {"remapping": f"asset/{MOD_ID}/text/champion", "type": "merge"},
        "asset/base/style/champion_view": {"remapping": f"asset/{MOD_ID}/style/champion_view", "type": "merge"},
        # Real summon unit sprite/anim overrides for sim.spawn_unit("abysspact_skeleton", ...)
        "asset/base/aseprite_resources/champions/abysspact_skeleton#sheet": {
            "remapping": f"asset/{MOD_ID}/champions/abysspact_skeleton#sheet", "type": "override"
        },
        "asset/base/aseprite_resources/champions/abysspact_skeleton#anim": {
            "remapping": f"asset/{MOD_ID}/champions/abysspact_skeleton#anim", "type": "override"
        },
    }
    sfx_dir = os.path.join(MOD, "sound", "sfx")
    # Clean stale .sound_info files first
    if os.path.isdir(lp(sfx_dir)):
        for fn in os.listdir(lp(sfx_dir)):
            if fn.endswith(".sound_info"):
                os.remove(lp(os.path.join(sfx_dir, fn)))

    all_sound_keys = set()
    for cid, rs_name in rs_map.items():
        played = kit_sounds(cid) | dll_sounds(cid, rs_name)
        defined = {f"{cid}_{k}": v for k, v in SOUNDS[cid].items()}
        missing = sorted(played - set(defined))
        unused = sorted(set(defined) - played)
        if missing or unused:
            sys.exit(f"SOUND MISMATCH for {cid}: missing={missing}, unused={unused}")
        for ev, plays in defined.items():
            for clip, vol, dly in plays:
                if clip == ev:
                    sys.exit(f"{ev} shares clip name")
                if not os.path.isfile(lp(os.path.join(sfx_dir, clip + ".mp3"))):
                    sys.exit(f"MISSING MP3 CLIP: {clip}.mp3")
                all_sound_keys.add(clip)
            save(os.path.join(sfx_dir, ev + ".sound_info"),
                 {"plays": [{"delay": d, "clip": c, "volume": v} for c, v, d in plays]})
            all_sound_keys.add(ev)

    for key in sorted(all_sound_keys):
        ov[f"asset/base/sound/sfx/{key}"] = {"remapping": f"asset/{MOD_ID}/sound/sfx/{key}", "type": "override"}

    save(os.path.join(MOD, "mod.override_info"), ov)
    print(f"wrote {sum(len(v) for v in SOUNDS.values())} .sound_info files and mod.override_info ({len(ov)} entries)")


def write_champion_view():
    entries = {
        "abysspact_oathbreaker": {"face": {"x": 3, "y": -32}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_faceless":    {"face": {"x": 2, "y": -33}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_whisperer":   {"face": {"x": 2, "y": -34}, "center": {"x": 0, "y": -16}, "banpick_center": {"x": 0, "y": -12}},
        "abysspact_bonebow":     {"face": {"x": 2, "y": -32}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_corvus":      {"face": {"x": 3, "y": -33}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_bloodmoon":   {"face": {"x": 3, "y": -32}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_undertaker":  {"face": {"x": 2, "y": -34}, "center": {"x": 0, "y": -16}, "banpick_center": {"x": 0, "y": -12}},
        "abysspact_effigy":      {"face": {"x": 2, "y": -31}, "center": {"x": 0, "y": -14}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_sevenfold":   {"face": {"x": 3, "y": -33}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_vesper":      {"face": {"x": 2, "y": -33}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_carapace":    {"face": {"x": 2, "y": -32}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_leech":       {"face": {"x": 2, "y": -28}, "center": {"x": 0, "y": -13}, "banpick_center": {"x": 0, "y": -10}},
        "abysspact_noctua":      {"face": {"x": 2, "y": -32}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
        "abysspact_anchor":      {"face": {"x": 2, "y": -33}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -12}},
        "abysspact_hourglass":   {"face": {"x": 2, "y": -32}, "center": {"x": 0, "y": -15}, "banpick_center": {"x": 0, "y": -11}},
    }
    save(os.path.join(MOD, "style", "champion_view.champion_view"), {"entries": entries})
    print("wrote style/champion_view.champion_view")


def write_mod_info():
    desc = (
        "Abyss Pact (渊契) 15-champion dark-fantasy original pack for Teamfight Manager 2 — "
        "Batch 1: Oathbreaker (断誓), Faceless (无面), Whisperer (呓语), Bonebow (骸弦), Corvus (鸦医); "
        "Batch 2: Bloodmoon (血月), Undertaker (入殓), Effigy (替身), Sevenfold (七弹), Vesper (烛灵); "
        "Batch 3: Carapace (蜕甲), Leech (附骨), Noctua (千蛾), Anchor (沉锚), Hourglass (返照). "
        "Powered by abysspact.dll for dense HD PPU frames, multi-form/giant/aging visual swaps, "
        "real summon units, Face-Steal, Spirit Form revival, team 3s rewind, and natural Mandarin voices."
    )
    mi = {
        "author": "BoDUD",
        "contains_code": True,
        "dependencies": [{"mod_id": "base", "version": ">=0.4.11"}],
        "description": desc,
        "last_updated": "2026-11-24",
        "mod_id": MOD_ID,
        "mod_type": "native",
        "name": NAME,
        "version": VERSION,
    }
    save(os.path.join(MOD, "mod.mod_info"), dict(sorted(mi.items())))
    print(f"wrote mod.mod_info ({MOD_ID} {VERSION})")


def main():
    build_i18n()
    write_champion_view()
    write_sounds_and_overrides()
    write_mod_info()
    print("ABYSS PACT PACK SETUP COMPLETE!")


if __name__ == "__main__":
    main()
