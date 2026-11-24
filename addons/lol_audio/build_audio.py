"""Build lol_audio's sounds out of a local League of Legends install.

    python -I addons/lol_audio/build_audio.py --lol "D:\\WeGameApps\\lol" --vgmstream path\\to\\vgmstream-cli.exe
    python -I addons/lol_audio/build_audio.py --lol ... --vgmstream ... --only lol_executed
    python -I addons/lol_audio/build_audio.py --events      # sound events + mod.override_info only

Reads (never writes) the League client and writes into addons/lol_audio/sound/ (git-ignored: audio (c) Riot Games):

- BP: the client's draft music (LeagueClient/Plugins/rcp-fe-lol-champ-select/assets.wad, Ogg files). League stacks
  "intensity layers" on a base layer; here they are mixed into fixed tracks:
  sound/bgm/lol_draft.mp3 = ban phase (base + layer 1) -> the ban-to-pick transition -> pick phase (base + layers 1-2),
  for the game's banpick and banpick2; sound/bgm/lol_draft_final.mp3 = the pick phase with all four layers, for the
  deciding game's banpick_match5_lastgame.
- Match: Summoner's Rift's own in-game music (Map11.wad.client, mus_map11_audio.wpk). The pack holds the Rift's three
  long tracks (about 9, 5 and 4.7 min) plus short layers and stingers; the tracks are the clips of `TRACK_MIN` s or
  more, longest first, written as sound/bgm/lol_rift_music1..3.mp3 for match .. match6 (match4..6 repeat 1..3).
  Media ids change between patches, lengths do not.
- Announcer (Map11.zh_CN.wad.client: the zh_CN client keeps the en_us path but the Chinese clips):
  the spectator ("purple") multi-kill lines over the game's own multi-kill sounds (dual_takedown = double kill,
  triple_takedown, devastation = quadra, annihilation = penta; the game's kill2..kill5 banners), and the lines the
  game has no sound for, which lol_audio.dll plays (see `VOICE`): first blood, executed, ace, shutdown, the spree
  lines (killing spree .. legendary, ours and the enemy's), towers, dragon (the game's Serpen), Baron (Morgard),
  victory / defeat. Each of those clips also gets its sound event (sound/sfx/lol_audio_<name>.sound_info) and both
  remappings in mod.override_info (`write_events`): the game looks both up under asset/base/sound/sfx/.

- Champions' own lines lol_audio.dll plays (`CHAMP`): Rumble's Overheat line (Champions/Rumble.zh_CN.wad.client: like
  the announcer, the zh_CN client keeps the en_us path with the Chinese clips; `Play_vo_Rumble_Spell3DPCast`, a random
  container of three, the variant the user picked), as sound/sfx/lol_rumble_overheat.mp3 + its event.

`--only CLIP ...` builds just those clips (file names without .mp3, e.g. lol_executed) and leaves every other file as
it is: a full run rebuilds everything from the League client as it is now, which a League patch may have changed.

Needs Python 3.9+ with numpy and soundfile (its libsndfile writes the MP3s).
"""
import argparse
import io
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools", "lol"))
from riot import SoundBanks, Wad, parse_wpk  # noqa: E402

SR = 44100
CS = "LeagueClient/Plugins/rcp-fe-lol-champ-select/assets.wad"
CS_DIR = "plugins/rcp-fe-lol-champ-select/global/default/sounds/"
MAPS = "Game/DATA/FINAL/Maps/Shipping/"
RIFT_MUSIC = "assets/sounds/wwise2016/sfx/shared/mus_map11_audio.wpk"
TRACK_MIN = 200.0
VO_BANK = "assets/sounds/wwise2016/vo/en_us/shared/announcer_global_female1_vo_"
DRAFT = ("lol_draft", "lol_draft_final")
RIFT = re.compile(r"lol_rift_music(\d+)")
# League's spree lines, three kills in one life on (lol_audio.dll's SPREES)
SPREES = [("killing_spree", "KillingSpree"), ("rampage", "Rampage"), ("unstoppable", "Unstoppable"),
          ("dominating", "Dominating"), ("godlike", "Godlike"), ("legendary", "Legendary")]
VO_EVENT = "Play_vo_Announcer_"
# clip -> announcer event. Multi-kills: the spectator ("purple") lines. The rest are the lines lol_audio.dll plays
# (sound event lol_audio_<clip without lol_>): "YourTeam" / "EnemyTeam" = the player's view (used when lol_audio knows
# which side is the user's), "Blue" / "Red" / "purple" = the spectator's (team colour / neutral).
VOICE = {
    "lol_double_kill": "Female1_ChampionDoubleKillpurple",
    "lol_triple_kill": "Female1_ChampionTripleKillpurple",
    "lol_quadra_kill": "Female1_ChampionQuadraKillpurple",
    "lol_penta_kill": "Female1_ChampionPentaKillpurple",
    "lol_first_blood": "Female1_FirstBloodHeroYourTeam",  # every first-blood event plays this one clip
    # executed: KillChampion{Turret,Minion}Hero{YourTeam,EnemyTeam} all play this one clip (media 9261738)
    "lol_executed": "Female1_KillChampionTurretHeroYourTeam",
    # 0.2.0: Ace{YourTeam,EnemyTeam} play the same two clips; Shutdown* all the same two
    "lol_ace": "Female1_AceYourTeam",
    "lol_shutdown": "Female1_ShutdownHeroYourTeam",
    # sprees: HeroYourTeam = HeroBlue = HeroRed (a hero's own words), HeroEnemyTeam = the enemy's spree
    **{f"lol_{clip}": f"Female1_{event}HeroYourTeam" for clip, event in SPREES},
    **{f"lol_{clip}_enemy": f"Female1_{event}HeroEnemyTeam" for clip, event in SPREES},
    "lol_turret_ours": "Female1_TurretLostYourTeam",
    "lol_turret_theirs": "Female1_TurretLostEnemyTeam",
    "lol_turret": "Female1_TurretDiepurple",
    # the dragon / baron lines exist only as Blue / Red / purple ("Worm" = Baron Nashor)
    "lol_dragon": "Female1_KillDragonpurple",
    "lol_dragon_blue": "Female1_KillDragonBlue",
    "lol_dragon_red": "Female1_KillDragonRed",
    "lol_baron": "Female1_KillWormpurple",
    "lol_baron_blue": "Female1_KillWormBlue",
    "lol_baron_red": "Female1_KillWormRed",
    "lol_victory": "Global_Female1_OnVictory",
    "lol_defeat": "Global_Female1_OnDefeat",
    "lol_victory_blue": "Female1_VictoryBlue",
    "lol_victory_red": "Female1_VictoryRed",
}
# loudness: the game's own multi-kill sounds sit at about -15 dB RMS (peak -4), its BGM at about -14 dB RMS
VOICE_RMS, VOICE_PEAK = -15.0, -2.0
CHAMP_VOICE_RMS, CHAMP_VOICE_PEAK = -16.5, -2.5  # champion lifecycle VO: clear over battle SFX, under announcer
MUSIC_RMS, MUSIC_PEAK = -15.0, -1.5
RIFT_RMS = -17.0  # the game's match music sits at -14..-17 dB; the Rift's is mixed at about -30 under the game
GAME_DATA_ZH = "LeagueClient/Plugins/rcp-be-lol-game-data/zh_CN-assets.wad"
CHAMP_CUES = ("start", "kill", "dead", "respawn")
SLUG_TO_ALIAS = {"wukong": "monkeyking"}
SLUG_TO_WAD = {
    "aurelionsol": "AurelionSol", "belveth": "Belveth", "chogath": "Chogath", "drmundo": "DrMundo",
    "jarvaniv": "JarvanIV", "kaisa": "Kaisa", "khazix": "Khazix", "kogmaw": "KogMaw",
    "ksante": "KSante", "leblanc": "Leblanc", "leesin": "LeeSin", "masteryi": "MasterYi",
    "missfortune": "MissFortune", "reksai": "RekSai", "tahmkench": "TahmKench",
    "twistedfate": "TwistedFate", "velkoz": "Velkoz", "wukong": "MonkeyKing", "xinzhao": "XinZhao",
}


def read_ogg(wad, name):
    x, sr = sf.read(io.BytesIO(wad.read_path(CS_DIR + name + ".ogg")), always_2d=True)
    return resample(x, sr)


def resample(x, sr):
    if sr == SR:
        return x
    t = np.arange(int(len(x) * SR / sr)) * sr / SR
    return np.stack([np.interp(t, np.arange(len(x)), x[:, c]) for c in range(x.shape[1])], 1)


def mix(*tracks):
    n = max(len(t) for t in tracks)
    out = np.zeros((n, 2))
    for t in tracks:
        out[: len(t)] += t
    return out


def level(x, rms_db, peak_db, limit=False):
    """Scale to `rms_db` (RMS of the non-silent part), never past `peak_db`. With `limit` the gain goes to the RMS
    target and a limiter holds the peaks (League's music has more headroom than the game's own BGM)."""
    m = x.mean(1) if x.ndim > 1 else x
    loud = m[np.abs(m) > 1e-3]
    rms = np.sqrt(np.mean(loud ** 2)) if len(loud) else 1.0
    if limit:
        return limiter(x * 10 ** (rms_db / 20) / rms, 10 ** (peak_db / 20))
    g = min(10 ** (rms_db / 20) / rms, 10 ** (peak_db / 20) / np.abs(x).max())
    return x * g


def limiter(x, ceiling, block=256, width=9):
    """Block gains (ceiling / block peak) -> min over `width` blocks -> mean over `width - 2` blocks -> per sample.
    Every smoothed gain is a mean of minima whose windows all hold its own block and both neighbours, and a sample is
    interpolated between its block's gain and a neighbour's, so no sample passes the ceiling."""
    n = -(-len(x) // block)
    pad = np.zeros((n * block, x.shape[1]))
    pad[: len(x)] = x
    peak = np.abs(pad).reshape(n, block, -1).max((1, 2))
    g = np.minimum(1.0, ceiling / np.maximum(peak, 1e-9))
    gp = np.pad(g, width // 2, mode="edge")
    g = np.lib.stride_tricks.sliding_window_view(gp, width).min(1)
    gp = np.pad(g, width // 2 - 1, mode="edge")
    g = np.lib.stride_tricks.sliding_window_view(gp, width - 2).mean(1)
    centres = np.arange(n) * block + block / 2
    gs = np.interp(np.arange(n * block), centres, g)
    return (pad * gs[:, None])[: len(x)]


def wem(data, vgmstream):
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d, "a.wem"), os.path.join(d, "a.wav")
        with open(src, "wb") as f:
            f.write(data)
        subprocess.run([vgmstream, "-o", dst, src], check=True, capture_output=True)
        x, sr = sf.read(dst, always_2d=True)
    return resample(x, sr)


def trim_tail(x, floor_db=-60.0, fade=0.05):
    """Cut the reverb tail below `floor_db`, with a short fade-out."""
    m = np.abs(x).max(1)
    above = np.nonzero(m > 10 ** (floor_db / 20))[0]
    x = x[: above[-1] + 1].copy() if len(above) else x
    n = min(len(x), int(fade * SR))
    x[-n:] *= np.linspace(1, 0, n)[:, None]
    return x



# champions' own lines lol_audio.dll plays: clip -> (champion, event, variant: the event's media in bank order)
# Rumble's Overheat: Spell3DPCast has three variants (1.48 / 4.56 / 9.72 s); the first is two ~0.5 s words with a pause,
# the same word twice (spectral likeness 0.78; the other clips' parts 0.42 at most): 「警告，警告」 (no zh speech
# recogniser on this PC; the user: 「你自己选语音用哪一段」)
CHAMP = {"lol_rumble_overheat": ("Rumble", "Play_vo_Rumble_Spell3DPCast", 0)}
CHAMPS = "Game/DATA/FINAL/Champions/"


def champ_vo(lol, champion):
    name = champion.lower()
    wad = Wad(os.path.join(lol, CHAMPS, f"{champion}.zh_CN.wad.client"))
    base = f"assets/sounds/wwise2016/vo/en_us/characters/{name}/skins/base/{name}_base_vo_"
    media = parse_wpk(wad.read_path(base + "audio.wpk"))
    return media, SoundBanks([wad.read_path(base + "events.bnk"), wad.read_path(base + "audio.bnk")], media)


# the clips the game plays itself (its own multi-kill events, remapped in mod.override_info by hand)
OWN = {"lol_double_kill": "dual_takedown", "lol_triple_kill": "triple_takedown", "lol_quadra_kill": "devastation",
       "lol_penta_kill": "annihilation"}


def league_slugs():
    """All League champion slugs in league/champion/league_*.data_champion, sorted."""
    champ_dir = os.path.join(HERE, "..", "..", "league", "champion")
    if not os.path.isdir(champ_dir):
        return []
    return sorted(
        f[len("league_"):-len(".data_champion")]
        for f in os.listdir(champ_dir)
        if f.startswith("league_") and f.endswith(".data_champion")
    )


def trim_both(x, floor_db=-55.0, max_s=4.2, fade=0.06):
    """Trim leading and trailing silence, cap duration, and apply a gentle fade-out."""
    m = np.abs(x).max(1)
    above = np.nonzero(m > 10 ** (floor_db / 20))[0]
    if len(above):
        lo = max(0, int(above[0]) - int(0.01 * SR))
        hi = min(len(x), int(above[-1]) + int(0.03 * SR))
        x = x[lo:hi].copy()
    x = x[: int(max_s * SR)].copy()
    n = min(len(x), int(fade * SR))
    if n > 0:
        x[-n:] *= np.linspace(1, 0, n)[:, None]
    return x


def write_events(root=HERE):
    """sound/sfx/lol_audio_<name>.sound_info for each clip lol_audio.dll plays, and the two remappings of each in
    mod.override_info (the event and its clip, both looked up under asset/base/sound/sfx/). Champion lifecycle clips
    point at sound/bgm/ so the game streams them lazily when played instead of preloading all 692 clips at startup."""
    import json
    path = os.path.join(root, "mod.override_info")
    with open(path, encoding="utf-8") as f:
        info = json.load(f)
    sfx_dir = os.path.join(root, "sound", "sfx")
    os.makedirs(sfx_dir, exist_ok=True)
    for clip in list(VOICE) + list(CHAMP):
        if clip in OWN:
            continue
        event = "lol_audio_" + clip[len("lol_"):]
        with open(os.path.join(sfx_dir, event + ".sound_info"), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"plays": [{"delay": 0.0, "clip": clip, "volume": 1.0}]}, separators=(",", ":")) + "\n")
        for name in (event, clip):
            info[f"asset/base/sound/sfx/{name}"] = {"remapping": f"asset/lol_audio/sound/sfx/{name}", "type": "override"}
    for slug in league_slugs():
        for cue in CHAMP_CUES:
            clip = f"lol_ch_{slug}_{cue}"
            event = f"lol_audio_ch_{slug}_{cue}"
            with open(os.path.join(sfx_dir, event + ".sound_info"), "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps({"plays": [{"delay": 0.0, "clip": clip, "volume": 0.95}]}, separators=(",", ":")) + "\n")
            info[f"asset/base/sound/sfx/{event}"] = {"remapping": f"asset/lol_audio/sound/sfx/{event}", "type": "override"}
            info[f"asset/base/sound/sfx/{clip}"] = {"remapping": f"asset/lol_audio/sound/bgm/{clip}", "type": "override"}
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(info, indent=2, ensure_ascii=False) + "\n")


def _pick_vo_media(banks, media, vgmstream, patterns, ev_low, used_ids, min_s=0.45, max_s=5.2):
    """Find the first matching event in priority order and pick a clear, complete spoken variant."""
    for pat in patterns:
        for ev, el in ev_low:
            if not re.search(pat, el) or any(b in el for b in ("chat", "emote", "ping", "shop", "buyitem", "ward", "ally", "enemy")):
                continue
            ids = [m for m in banks.event_media(ev) if m in media and m not in used_ids]
            if not ids:
                continue
            best = None
            best_score = -1e9
            for mid in ids[:6]:
                x = trim_both(wem(media[mid], vgmstream), max_s=max_s)
                dur = len(x) / SR
                if dur < min_s:
                    score = dur * 5.0
                elif dur <= 3.8:
                    score = 10.0 + min(dur, 2.4)
                else:
                    score = 9.5 - (dur - 3.8) * 1.2
                if score > best_score:
                    best_score = score
                    best = (mid, x, ev)
            if best:
                return best
    return None


def build_champion_voices(lol, vgmstream, out_dir, slugs=None):
    """Extract all 173 LoL champions' start / kill / dead / respawn Chinese voice lines into <out_dir>/bgm/."""
    import concurrent.futures
    import json

    slugs = slugs or league_slugs()
    gd_wad = Wad(os.path.join(lol, GAME_DATA_ZH))
    summary = json.loads(gd_wad.read_path("plugins/rcp-be-lol-game-data/global/zh_cn/v1/champion-summary.json").decode("utf-8"))
    alias_to_id = {c["alias"].lower(): c["id"] for c in summary if c.get("id", -1) > 0}

    champs_dir = os.path.join(lol, CHAMPS)
    zh_wads = {f.lower(): os.path.join(champs_dir, f) for f in os.listdir(champs_dir) if f.lower().endswith(".zh_cn.wad.client")}
    mn_wads = {f.lower(): os.path.join(champs_dir, f) for f in os.listdir(champs_dir)
               if f.lower().endswith(".wad.client") and ".zh_cn." not in f.lower() and f.count(".") == 2}

    bgm_dir = os.path.join(out_dir, "bgm")
    os.makedirs(bgm_dir, exist_ok=True)

    def read_gd_ogg(kind, cid):
        p = f"plugins/rcp-be-lol-game-data/global/zh_cn/v1/champion-{kind}-vo/{cid}.ogg"
        if not gd_wad.has(p):
            return None
        x, sr = sf.read(io.BytesIO(gd_wad.read_path(p)), always_2d=True)
        return trim_both(resample(x, sr), max_s=8.0)

    def one(slug):
        alias = SLUG_TO_ALIAS.get(slug, slug)
        cid = alias_to_id.get(alias)
        if cid is None:
            raise RuntimeError(f"{slug}: not in champion-summary.json (alias {alias})")
        wad_hint = SLUG_TO_WAD.get(slug, alias).lower()
        zh_p = zh_wads.get(f"{wad_hint}.zh_cn.wad.client") or zh_wads.get(f"{slug}.zh_cn.wad.client")
        mn_p = mn_wads.get(f"{wad_hint}.wad.client") or mn_wads.get(f"{slug}.wad.client")
        if not zh_p or not mn_p:
            raise RuntimeError(f"{slug}: missing WAD in {champs_dir}")

        mw = Wad(mn_p)
        vw = Wad(zh_p)
        base = os.path.basename(mn_p)[:-len(".wad.client")].lower()
        vo_bank = f"assets/sounds/wwise2016/vo/en_us/characters/{base}/skins/base/{base}_base_vo_"
        media = parse_wpk(vw.read_path(vo_bank + "audio.wpk"))
        banks = SoundBanks([vw.read_path(vo_bank + "events.bnk")], media)

        raw = b""
        for bp in (f"data/characters/{base}/skins/skin0.bin", f"data/characters/{base}/skins/root.bin",
                   f"data/characters/{base}/{base}.bin"):
            if mw.has(bp):
                raw += mw.read_path(bp)
        wn = os.path.basename(mn_p)[:-len(".wad.client")]
        evs = set(m.decode("ascii", "ignore") for m in re.findall(rb'Play_vo_[A-Za-z0-9_]{3,80}', raw))
        for tail in ("Death", "Death3D", "Death2D", "Die", "Kill", "Kill3D", "Kill2D", "KillChampion",
                     "KillChampion3D", "KillChampion2D", "Kill2DGeneral", "Kill3DGeneral", "Respawn",
                     "Respawn3D", "Respawn2D", "Respawn2DGeneral", "Respawn3DGeneral",
                     "Move2DFirst", "Move3DFirst", "Move2DStandard", "Move3D", "Move2D",
                     "Taunt3DGeneral", "Taunt3D", "Taunt2D", "Laugh3DGeneral", "Attack2DGeneral", "Attack3DGeneral"):
            evs.add(f"Play_vo_{wn}_{tail}")
            evs.add(f"Play_vo_{wn}_{wn}{tail}")
        ev_low = sorted((e, e.lower()) for e in evs if banks.event_media(e))

        used_ids = set()
        sources = {}

        # 1. start: official Chinese Champion Select pick voice (173/173 iconic quotes!)
        x_start = read_gd_ogg("choose", cid)
        if x_start is None:
            raise RuntimeError(f"{slug}: missing choose-vo/{cid}.ogg")
        sources["start"] = "choose-vo"

        def ban_or_opening():
            x_ban = read_gd_ogg("ban", cid)
            if x_ban is not None:
                return x_ban, "ban-vo"
            return x_start, "choose-vo"

        # 2. dead: official Death VO -> fallback ban-vo
        hit_dead = _pick_vo_media(
            banks, media, vgmstream,
            [r'_death(?:3d|2d)?(?:general)?$', r'_death(?:3d|2d)?\d*$', r'death(?:3d|2d)general', r'_death', r'_die'],
            ev_low, used_ids, min_s=0.35, max_s=5.5,
        )
        if hit_dead:
            used_ids.add(hit_dead[0])
            x_dead = hit_dead[1]
            sources["dead"] = hit_dead[2]
        else:
            x_dead, sources["dead"] = ban_or_opening()

        # 3. kill: explicit general KillChampion / KillGeneral / Kill -> fallback general Taunt / Laugh / ban-vo
        hit_kill = _pick_vo_media(
            banks, media, vgmstream,
            [r'kill(?:3d|2d)?champion(?:general)?$', r'kill(?:3d|2d)?general$', r'_kill(?:3d|2d)?$',
             r'takedown(?:3d|2d)?(?:general)?$', r'taunt(?:3d|2d)?general$', r'_taunt(?:3d|2d)?$',
             r'laugh(?:3d|2d)?general$', r'_laugh(?:3d|2d)?$'],
            ev_low, used_ids, min_s=0.5, max_s=5.5,
        )
        if hit_kill:
            used_ids.add(hit_kill[0])
            x_kill = hit_kill[1]
            sources["kill"] = hit_kill[2]
        else:
            x_kill, sources["kill"] = ban_or_opening()

        # 4. respawn: explicit general Respawn -> fallback general FirstMove / MoveStandard / Move / Attack
        hit_resp = _pick_vo_media(
            banks, media, vgmstream,
            [r'respawn(?:3d|2d)?(?:general)?$', r'_respawn(?:3d|2d)?$', r'revive(?:3d|2d)?(?:general)?$',
             r'move(?:3d|2d)?first$', r'firstmove(?:3d|2d)?(?:general)?$',
             r'move(?:3d|2d)?standard$', r'move(?:3d|2d)?order$', r'move(?:3d|2d)?general$',
             r'_move(?:3d|2d)?$', r'attack(?:2d|3d)general$', r'_attack(?:2d|3d)?$'],
            ev_low, used_ids, min_s=0.5, max_s=5.5,
        )
        if hit_resp:
            used_ids.add(hit_resp[0])
            x_resp = hit_resp[1]
            sources["respawn"] = hit_resp[2]
        else:
            x_resp, sources["respawn"] = ban_or_opening()

        for cue, arr in (("start", x_start), ("kill", x_kill), ("dead", x_dead), ("respawn", x_resp)):
            mono = arr.mean(1, keepdims=True)
            out_p = os.path.join(bgm_dir, f"lol_ch_{slug}_{cue}.mp3")
            sf.write(out_p, np.clip(level(mono, CHAMP_VOICE_RMS, CHAMP_VOICE_PEAK, limit=True), -1, 1), SR, format="MP3")
        return slug, sources

    done = 0
    fallback_counts = {"dead_fallback": 0, "kill_explicit": 0, "respawn_explicit": 0}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for slug, src in ex.map(one, slugs):
            done += 1
            if src["dead"] in ("ban-vo", "choose-vo"):
                fallback_counts["dead_fallback"] += 1
            if "kill" in src["kill"].lower() or "takedown" in src["kill"].lower():
                fallback_counts["kill_explicit"] += 1
            if "respawn" in src["respawn"].lower() or "revive" in src["respawn"].lower():
                fallback_counts["respawn_explicit"] += 1
            if done % 25 == 0 or done == len(slugs):
                print(f"  champions: {done}/{len(slugs)} done (last: {slug} -> dead={src['dead']}, kill={src['kill']}, respawn={src['respawn']})")
    print(f"Champion lifecycle voices built: {done} champions x 4 cues = {done * 4} MP3s "
          f"(kill_explicit={fallback_counts['kill_explicit']}, respawn_explicit={fallback_counts['respawn_explicit']}, "
          f"dead_explicit={done - fallback_counts['dead_fallback']})")


def write(path, x):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sf.write(path, np.clip(x, -1, 1), SR, format="MP3")
    try:
        shown = os.path.relpath(path, HERE)
    except ValueError:
        shown = path
    print(f"  {shown}  {len(x) / SR:.1f} s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lol", help="League of Legends install folder (has Game/ and LeagueClient/)")
    ap.add_argument("--vgmstream")
    ap.add_argument("--out", default=os.path.join(HERE, "sound"))
    ap.add_argument("--events", action="store_true",
                    help="only write the sound events and mod.override_info entries (no League install read)")
    ap.add_argument("--champions", action="store_true",
                    help="only build the 173 LoL champions' start/kill/dead/respawn voice clips (+ events)")
    ap.add_argument("--only", nargs="+", metavar="CLIP",
                    help="build only these clips (e.g. lol_executed); every other file stays as it is")
    a = ap.parse_args()
    if a.events:
        write_events()
        return
    if not a.lol or not a.vgmstream:
        ap.error("--lol and --vgmstream are needed to build audio")
    if a.champions:
        build_champion_voices(a.lol, a.vgmstream, a.out)
        write_events()
        return
    only = set(a.only or ())
    unknown = sorted(c for c in only if c not in DRAFT and c not in VOICE and c not in CHAMP and not RIFT.fullmatch(c))
    if unknown:
        ap.error(f"unknown clip {', '.join(unknown)}; the clips: {', '.join(DRAFT)}, lol_rift_music1..3, "
                 f"{', '.join(VOICE)}, {', '.join(CHAMP)}")

    def want(clip):
        return not only or clip in only

    if any(want(c) for c in DRAFT):
        cs = Wad(os.path.join(a.lol, CS))
        ban = mix(*(read_ogg(cs, f"music-cs-draft-ban-{p}") for p in ("base-layer-01", "intensity-layer-01")))
        trans = read_ogg(cs, "music-cs-draft-ban-to-pick-trans-01")
        pick = [read_ogg(cs, f"music-cs-draft-pick-{p}") for p in ("base-layer-01", "intensity-layer-01",
                "intensity-layer-02", "intensity-layer-03", "intensity-layer-04")]
        if want("lol_draft"):
            write(os.path.join(a.out, "bgm", "lol_draft.mp3"),
                  level(np.concatenate([ban, trans, mix(*pick[:3])]), MUSIC_RMS, MUSIC_PEAK, limit=True))
        if want("lol_draft_final"):
            write(os.path.join(a.out, "bgm", "lol_draft_final.mp3"),
                  level(mix(*pick), MUSIC_RMS, MUSIC_PEAK, limit=True))

    rift = sorted(int(RIFT.fullmatch(c).group(1)) for c in only if RIFT.fullmatch(c))
    if not only or rift:
        pack = parse_wpk(Wad(os.path.join(a.lol, MAPS, "Map11.wad.client")).read_path(RIFT_MUSIC))
        tracks = sorted((x for x in (wem(d, a.vgmstream) for d in pack.values()) if len(x) >= TRACK_MIN * SR),
                        key=len, reverse=True)
        if not tracks:
            sys.exit(f"no track of {TRACK_MIN} s or more in {RIFT_MUSIC}")
        if rift and rift[-1] > len(tracks):
            sys.exit(f"lol_rift_music{rift[-1]} asked for, {RIFT_MUSIC} has {len(tracks)} tracks")
        for i, x in enumerate(tracks, 1):
            if want(f"lol_rift_music{i}"):
                write(os.path.join(a.out, "bgm", f"lol_rift_music{i}.mp3"), level(x, RIFT_RMS, MUSIC_PEAK, limit=True))

    if any(want(c) for c in VOICE):
        vo = Wad(os.path.join(a.lol, MAPS, "Map11.zh_CN.wad.client"))
        media = parse_wpk(vo.read_path(VO_BANK + "audio.wpk"))
        banks = SoundBanks([vo.read_path(VO_BANK + "events.bnk"), vo.read_path(VO_BANK + "audio.bnk")], media)
        for clip, event in VOICE.items():
            if not want(clip):
                continue
            ids = banks.event_media(VO_EVENT + event)
            if not ids:
                sys.exit(f"no media for {VO_EVENT + event}")
            x = trim_tail(wem(media[ids[0]], a.vgmstream)).mean(1, keepdims=True)  # mono, like the game's own
            write(os.path.join(a.out, "sfx", clip + ".mp3"), level(x, VOICE_RMS, VOICE_PEAK, limit=True))
        write_events()

    for clip, (champion, event, k) in CHAMP.items():
        if not want(clip):
            continue
        media, banks = champ_vo(a.lol, champion)
        ids = banks.event_media(event)
        if len(ids) <= k:
            sys.exit(f"{event}: {len(ids)} media, no variant {k}")
        x = trim_tail(wem(media[ids[k]], a.vgmstream)).mean(1, keepdims=True)
        write(os.path.join(a.out, "sfx", clip + ".mp3"), level(x, VOICE_RMS, VOICE_PEAK, limit=True))
        write_events()
    if not only:
        build_champion_voices(a.lol, a.vgmstream, a.out)
        write_events()


if __name__ == "__main__":
    main()
