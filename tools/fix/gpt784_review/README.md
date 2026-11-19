# Review of GPT's redo on #784 (2026-11-19)

GPT (Codex) pushed four commits to `codex/xinzhao-loris-scuttle-atlases` (6aec571d7, d6f8abdb0, 9dc47a6a0, d8b29e512):
full redraws of league_galio, league_braum, league_chogath, league_gragas, league_nasus (Infernal), league_tryndamere
(Blood Moon) and league_yasuo (Nightbringer), their skin effects, and installed them (mods/ and the Steam Workshop copy).

Checked and fine: frame counts and durations, tag sets (league.dll's compiled-in tag lists still match), 1x / lo_
frames against the dense ones, Yasuo's sword (85 dense px in every frame that draws it), Braum's E (no third hand),
CI's 57 Python checks and the Rust suites.

Fixed here:

- Cho'Gath: GPT's redo and the fixes on it (`chogath_size.py` hd.rs SIZES 0.79, `chogath_run.py`, `chogath_holes.py`,
  the reel picks and face point) are undone at the user's word (2026-11-19: 「科加斯也还原吧不改了」): every
  Cho'Gath file, SIZES, face point and idle picks are main's (099abf3b3) again; the three tools are gone.
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

## Nasus: ears, outline, and League's motions (2026-11-19 night)

The user on GPT's Nasus: 「狗头的右耳朵我还感觉少了一块」「狗头的耳朵画精致一点啊」「还有狗头的黑边处理干净点」
「放Q的时候头部有个黑色阴影块没处理干净 头旁边」 and 「狗头的平A动作不像英雄联盟的 重改 包括释放其他技能时都要像英雄联盟的
动作才行」. Run in this order, each from the state the one before leaves (all have --check):

1. `nasus_clean.py` (+ `nasus_ears.json`): one pair of ears per form, square for square, outlined, the near one with a
   dark-red inner ear, standing on the head at one place for every frame (GPT's broken one-square near ear, and ears
   one or two rows higher or lower from frame to frame); then every picture's outline: the body's edge outlined where
   GPT left it bare, the outline one square deep all round (near-black shade under it counted as outline), the inside
   of solid-black areas (the shoulder and neck painted black beside the head in the Q / attack blow) turned into the
   dark of the colours round them, lone squares and specks off the body gone, thin_outline.py's own pass last. The 1x
   and lo_ frames get only the change, the strips frame by frame.
2. `nasus_actions.py` (+ `nasus_actions.json`): attack, Q (skill) and E (skill2), both forms, as League's clips
   (tools/lol/pose_ref.py: nasus_attack1 a chop over the head, Nasus_Spell1 a slam into a low crouch with the staff along
   the ground, Nasus_Base_Spell3_Full the staff raised high then cast forward), from pictures the sheet already has;
   same lengths. The hit's frame 0 keeps the braced guard (`nasus_hit.py` now reads its rects from the table).
3. W (skill_w) keeps GPT's frames (the free hand pushed forward, the staff raised): League's Spell2 raises the free
   hand over his head, and two tries at that from GPT's drawings deformed him (the hanging arm mirrored upside down;
   then GPT's thin, foreshortened forward forearm turned up, his side hollow where the big arm hung - 「左手变形了啊
   武器也变形 你自己不review的吗」「还是有点变形」): that pose needs the arm and shoulder drawn anew.
4. tools/art/hero_reels.py --hero nasus (the idle / BP reels come from the new actions), illaoi_souls.py, league.dll
   0.9.109 (hd.rs compiles his .fanim in).

R (ult) keeps GPT's frames: crouch, rise, the staff raised, the big form - as League's Spell4.

## Nidalee's idle, the spear upright (2026-11-19)

The user: 「豹女新模型待机动作也应该竖着拿枪啊 我只是改跑步时候而已」, then 「好的豹女ok了」. `nidalee_idle_spear.py` (made in
its own session, branch claude/gpt784-nidalee-idle): GPT's idle held the spear across her body; the spear is taken
out (what it hid filled back in) and stood upright in her right hand, its butt by her right boot. illaoi_souls.py
again.
