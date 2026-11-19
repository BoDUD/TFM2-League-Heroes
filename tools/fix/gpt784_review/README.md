# Review of GPT's redo on #784 (2026-11-19)

GPT (Codex) pushed four commits to `codex/xinzhao-loris-scuttle-atlases` (6aec571d7, d6f8abdb0, 9dc47a6a0, d8b29e512):
full redraws of league_galio, league_braum, league_chogath, league_gragas, league_nasus (Infernal), league_tryndamere
(Blood Moon) and league_yasuo (Nightbringer), their skin effects, and installed them (mods/ and the Steam Workshop copy).

Checked and fine: frame counts and durations, tag sets (league.dll's compiled-in tag lists still match), 1x / lo_
frames against the dense ones, Yasuo's sword (85 dense px in every frame that draws it), Braum's E (no third hand),
CI's 57 Python checks and the Rust suites.

Fixed here:

- `chogath_size.py`: GPT's Cho'Gath stood 58 dense rows (48 game px) against the user's 「38 像素」: hd.rs SIZES 0.79,
  his dense frames 4 rows lower (Zaahen's drop), lo_ frames again with the size in them, strips.
- `nasus_hit.py`: his hit (both forms) flipped the staff from across to upright and back inside 0.2 s: frame 0 is now
  the braced guard of his attack (attack[4] / b_attack[4]), no pixel drawn.
- `galio_loop.py`: idle_loop frames 1 and 7 stood a row higher than the idle (a bob in every hold): moved down a row.
- `tools/art/hero_reels.json` + hero_reels.py for the seven: GPT's idle / bp reels were not the tool's (Galio's idle
  played the bobbing idle_base frames instead of the wing loop; pictures that are in no action); the hand picks made for
  the old drawings were redone where the new frames broke them (Nasus: upright-staff cast frames in his idle; Tryndamere:
  a frame of his other look; Yasuo: R's jump in his idle).
- champion_view face points of Cho'Gath (x 0.79 about the soles), Nasus, Tryndamere and Yasuo (their heads sit
  further back in the new drawings).
- tools/art/illaoi_souls.py again: Illaoi's souls of the seven still showed the old drawings.

Left for the user (needs new pictures, not edits): Tryndamere is three separately generated looks (topknot + small
horned mask / long hair + horned mask in the run / wild mane + big mask, bulkier, in W Q R hit death) with blades of
different sizes; Yasuo's blade-out frames (ys_flare) are another colouring (bright blue trousers, gold trims) than his
idle and run.

## After GPT's second delivery (bdbda7d47, the redraw pack)

GPT redrew Tryndamere's run / cast frames in the tb_swing look (checked: one face, one blade size), Braum's run[0..3]
shield, Nasus's n_cast frames, Yasuo's blade-out frames and Nidalee's skill2[0], [3]. Checked again, then:

- `nidalee_run_spear.py --from 02b3aa862`: her run keeps the shoulder carry (the user: 「豹女跑步保持这个姿势就行了 我指出的问题
  是枪看起来在脸的另外一边」); in frames 4-7 the shaft span her collar and hair covered is painted in front of her face.
- `braum_run_outline.py`: the smaller shield left straight cuts with no outline where the big one covered him (underside
  of the forearm, side of the chest, the shield's top-left bevel; 44-52 light edge squares a frame, 0-1 elsewhere): the
  2-square outline round them, body untouched.
- `nasus_cast_colours.py`: the new n_cast frames (skill[0], skill2, skill_w, ult[0, 1, 2, 4, 5], dead, b_ twins) were
  drawn in his palette but much lighter (median Lab L 27 against 21, a grey-brown as the commonest body colour, lava all
  over): mapped onto the n_hit set's colours by lightness quantile.
- Yasuo: GPT's redo (Nightbringer, d6f8abdb0 / 9dc47a6a0 / d8b29e512 / bdbda7d47) and the fixes made on it
  (`yasuo_navy.py`, `yasuo_skin.py`, the skin / navy / idle reel rounds) are undone at the user's word
  (2026-11-19: 「亚索恢复到之前的版本吧 不改了」): every Yasuo file, his face point and idle picks are main's
  (099abf3b3) again; the two tools are gone.
- illaoi_souls.py again.
