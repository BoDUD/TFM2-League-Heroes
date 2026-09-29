# Art spec: sprites, VFX, icons

The goal every successful pack states the same way: custom sprites that "do not stray too far
from the base game aesthetic" (oppi). The numbers below are measured, not eyeballed:
**base** = all 78 base champion sprites (from `bundle.game_data`); **oppi** = the 12 hand-made
`.aseprite` champions in LoL Reborn (Nocturne, Jax, Lulu, Lux, Vi, Jinx, Caitlyn, Swain, Sion,
Alistar, K'Sante, Galio). The Dota 2 Heroes pack (Axe, Zeus, Huskar, Shadow Fiend, Elder Titan)
uses the same hand and rules. Re-measure anything with `scripts/tfm2_ase.py metrics`.

## Numbers

| Property | Base game | oppi packs | Rule for new heroes |
|---|---|---|---|
| Character height (idle, feet to top) | median 35 px, IQR 34-37, big units 41-45 | 33-39, tanks 44-51 | 34-38 px; bruisers/tanks up to ~45 |
| Facing / view | right, 3/4 side | right, 3/4 side | always face right |
| Proportions | chibi, ~3 heads tall | ~3 heads, less deformed | big head, readable hands, oversized signature prop |
| Silhouette outline | 1 px near-black on 100% of edge (median) | 93-100% | 1 px #000000-#0a0a0a around the whole silhouette |
| Interior near-black pixels | 15% median (1-51) | 20-45% | use black for inner lines and deepest shadow |
| Colours per idle set | median 25 (IQR 21-29, max 39) | 49-120 | 25-120; >160 means painted/downscaled art |
| Semi-transparent body pixels | 0 | 0 | 0 - no anti-aliasing, no soft shading |
| Shading | 2-3 hard steps | 3-4 hard steps, darker overall | hard cel steps, light from upper front |
| Palette | muted, earthy | muted base + 1-2 saturated signature colours | pick 1-2 signature colours per hero |

oppi's look in one line: base-game proportions and outline, but darker, denser rendering and
more colours - dark heroes (Nocturne, Shadow Fiend) are near-black bodies with glowing accents.

## Animation tags and timing

| Tag | Base (median frames @ ms) | oppi | Notes |
|---|---|---|---|
| idle | 4 @ 140-200 | 7 @ 100 | breathing / weapon sway |
| run | 8 @ 80 | 6-9 @ 75-100 | the move loop; may be a walk (League Garen: 8 @ 117) |
| attack | 5 @ 80 | 6-8 @ 75-85 | anticipation -> hit frame -> recovery |
| skill / skill1, skill2, ult | 5 @ 80 | 6-13 @ 80-100 | any name, but it must equal the action's `action_name` |
| hit | 1 @ 100 | often omitted | recommended |
| dead | 10 @ 100 | 6 @ 100 (often omitted) | recommended |
| extras | `ult_dash`, `ult_pre`, `ult_loop`, `skill2_attack`, `*_projectile`, `*_effect` | `attack_enhanced`, `ult_cast`, `ult_dash` | used by `CasterAnimation` or view bindings |

The hit frame of `attack` should land around the action's `start_timing` (e.g. attack
`duration` 20-24 ticks = 0.33-0.4 s, hit at tick 13-15).

Idle breathing in almost every base sprite: the body sinks 1, 2, 1 px over the 4 frames, and
everything from the crown down to the thighs moves together; only the lowest 5-7 rows (shins
and feet) stay, and the rows the move covers vanish inside the legs. Do not move the upper body
over a still pelvis: the seam then sits at the waist and the belt slides over the hips (Lee
Sin's first idle, fixed in `leesin_retouch.json`).

## Canvas and anchoring

- Base exported frames are cropped with odd sizes so the pivot pixel sits in the middle; the
  **feet (bottom edge) are 11.5 px below the frame centre** in essentially all 78 sprites, and
  `champion_view` offsets (face y ~ -34, center y ~ -12) are measured up from the feet.
- oppi's `.aseprite` canvases (70x70 to 139x109) keep the body horizontally centred with the
  **feet 17-20 px below the canvas centre** (tanks further down).
- Nobody has documented the engine's exact rule for `.aseprite` canvases. Pick one convention
  per pack, keep it identical for every frame, and verify in-game by standing the hero next to a
  base champion; adjust the canvas (not the art) until the feet line up.
- Never let the character drift between frames: keep the feet row fixed in idle/attack/skills.
- A hovering hero floats a few pixels above that line: the base ghost's lowest pixel is about 6 px above
  where feet would be. league_janna floats 3 px (`native_pose.py` `"hover"`: the pivot moves down, so every
  frame stands that high; her idle floats a row up and down as one drawing, and her death `"sink"`s back to the
  ground). Draw the ground line on the loops when you check them.

## Aseprite file conventions (what the game loads)

- RGBA colour mode. One file per hero: `champions/<hero>.aseprite`, every animation a tag.
- Layers used by oppi: `body`, `body2`, `effect`, `effect2`; hidden reference layers stay in
  the shipped files, so hidden layers are evidently not rendered *(inferred)*.
- Tag names are the animation names. Frame durations come from Aseprite's per-frame duration.
- Effects: one `.aseprite` per effect in `effects/`, `fx/` (projectiles) or `buffs/`, each with
  its own tag(s) (`loop`, `hit`, `impact`, `skill2`...).
- The engine also reads exported `#sheet.png` + `#anim.fanim` pairs (base format).

## VFX spec (oppi)

- Saturated, bright, often a white-hot core with 2-3 step colour ramps (blue->cyan->white,
  gold->pale gold->white, crimson->pink->white). **No black outline** - the opposite of bodies.
- Mostly opaque pixels; semi-transparency only for fades, shields, ghostly clones.
- 5-10 frames @ 65-125 ms; impact frames can flash white silhouettes.
- Sizes: projectiles 25-75 px, impacts 100-250 px wide, ground zones drawn with `z: -1/-2`.
- Reuse base effects when they fit (`bundle_tool.py list --grep skill_effect/`).
- **Anything with an up and down goes on a caster view.** A projectile's view is turned to the
  cast direction (champion-data section 6), so a wall or a banner on a `LineRangeProjectile` lies
  across the screen when cast upward. A `CasterViewEffect` is not turned, is mirrored for a
  left-facing caster and stands where it was played. league_yasuo's Wind Wall went this way (64 px
  tall, 20 px in front of him) before the user dropped the skill: Codex's twisted column of wind read
  as a tornado, League's ground-line shape (a long line with the ends bent back) read as a wall, and
  44 px was too small to shield him. A projectile that has an up and down but must fly (league_thresh's
  lantern, thrown to an ally anywhere) is laid along its flight instead: `import_thresh.py` turns Codex's
  upright lantern a quarter, ring toward its trail, and mirrors it top to bottom, so it reads the same
  flying left, right, up or down. Blades and hooks on chains are mirrored the same way.
- **A chain from the hand to a flying hook grows frame by frame.** A projectile's picture is one length:
  drawn 48 px long, league_thresh's hook stuck out 43 px behind him as it left his hand. Its chain is drawn
  by the importer link by link, one frame every two ticks, as long as the hook has flown (champion-data
  section 6): the blade is Codex's, the links take the colours of Codex's chain.

## Skill icons

Two accepted styles:
- **Base game:** 24x24 pixel-art glyphs on a transparent background - one saturated hue in 2-3
  shades plus white highlights, a single bold symbol (slash, arrow, flame, mask), no outline.
  Packed in an atlas (`UI_aseprite/skill_icon#sheet.png` + `#data.sprite_sheet`, 355 icons).
- **oppi packs:** 64x64 PNG, square, full-bleed, the **official ability art of the source game
  downscaled** (500-900 colours) - instantly recognisable to fans of that game.

Either way three per hero: `<hero>_skill`, `<hero>_skill2`, `<hero>_ult` in `skill_icons`
(or one atlas + 3 tags via `skill_icon`).

## Reference-first workflow

The base game itself keeps high-res chibi concept art for its newest champions
(`asset/base/aseprite_resources/champions/reference/*` ~1024x1536). Work the same way:

1. Collect official art of the hero (splash, model turnaround, skill icons).
2. Make a chibi reference: ~3 heads, 3/4 facing right, signature prop exaggerated.
3. Block the silhouette at 35 px height; check readability at 1x on the arena colour.
4. Outline, flat colours from a 20-40 colour palette, then 3-4 step hard shading.
5. Animate idle -> run -> attack -> skills -> ult -> hit -> dead.
6. `python scripts/tfm2_ase.py metrics champions/<hero>.aseprite` and
   `python scripts/tfm2_ase.py render champions/<hero>.aseprite --out preview.png` to review.

Plain downscaling of HD art fails the checks (hundreds of colours, soft edges, no outline).
Generated art passes them only through the import below.

## Generated art (image-model strips)

The route used for Garen in TFM2-League-Heroes: prompts in `assets/source/<hero>/PROMPTS.md`,
16 generated PNGs (1 reference, 9 animations, 6 effects), `tools/art/import_<hero>.py` built on
`scripts/strips.py`. What mattered:

- **Prompts.** One row of N frames per animation, real transparent background, feet on the same
  line in every cell, 3/4 view facing right. Generate a reference sheet first and attach it to
  every character prompt, or the hero drifts between animations.
- **Proportions: show them, don't only name them.** TFM2 heroes are ~3 heads tall with a big,
  flat-lit face (33-36 px heroes: head 12-13 px, 2x2 px eyes). Every Garen and Ashe prompt said
  "chibi", but the attached references (League renders, then the previous design sheet) were
  adult-proportioned, and the model followed the images: heads 1/5 of the height, faces two or
  three rows of skin without eyes in game, Ashe's also shaded by her hood - the user could not
  see either face. Attach a sheet of base heroes (idle + attack, 8x) to the design prompt, render
  the pose references with a big head (`pose_ref.py --head 2.0 --legs 0.8`), ask for a face that
  stays readable at 35 px (hood and bangs off the eyes), and check the design sheet's head size
  before generating any strip. The redraw (`assets/source/CHIBI_REDRAW.md`) came back right in the
  first round. After importing, `tfm2_ase.py face <sprite> --out face.png` puts the hero next to
  base champions at 1x and zoomed: look for the eyes before shipping. Counting skin-coloured
  pixels does not replace looking - the small-headed Garen scored more "skin" in his upper body
  than most base heroes, because his gold trim has skin tones.
- **A face without eyes has only its mouth left.** Lee Sin's blindfold hides the eyes, so every
  dark square under it reads as a feature. His delivered design had a 2 px dark stroke down the
  front of the face and a dark pair on the chin row: at card size the user saw a strange nose and
  mouth. Base faces draw no nose and, in idle, almost never a mouth. Under a band or mask, close the outline
  along the face's front, put a 2-square mouth two rows under the band, shade under the chin so it
  separates from the neck, and keep other dark squares out of the lower face. Give the face side a curve: the champion card
  is near-black, so the outline vanishes and only the skin shape reads; Lee Sin's straight 8 px
  right edge and square crown corner looked like half a head until the crown stepped in, the
  blindfold and nose tip stood out a pixel and the mouth and chin stepped back. Look at the face at
  card size (`tfm2_ase.py face`, and on a dark background) as well as zoomed.
- **In a 3/4 view the wide eye is the near one.** A hero facing right has the near eye left of the
  face's middle, two squares wide, and the far eye one square wide against the right cheek. Base
  eyes are three rows: dark lashes or brows, then a light highlight beside a dark pupil, then white
  beside the iris colour (the iris on the side the hero faces), with two rows of face and a chin
  shadow below. Soraka's approved design had the eyes mirrored (the wide one by the far cheek) and
  only two rows (a black lid over pale yellow) above five rows of face with a dark-blue jaw patch.
  The user called the face ugly twice before anyone spotted the mirroring. Fixed by one head swap
  in all 52 frames: the fringe one row lower, the eyes mirrored back and three rows tall, the patch
  cut back to the chin shadow. Offered no mouth and a one-square mouth, the user picked the mouth
  in dark red: a mouth in the skin's shadow colour merges with the chin shadow. When a design
  sheet comes back, compare its eyes with base heroes square by square, not just their size.
- **Show faces as options, side by side.** league_yasuo's first drawn face followed the rule above
  to the letter (a black brow row, highlight + black pupil, white + iris, one skin column between
  the eyes, a dark-red mouth square) and the user found the eyes and mouth strange. Base male
  faces (`tfm2_face_ref_male.png`) differ in ways the rule missed: the top eye row is a dark-brown
  lash, not a black brow; the eyes stand two skin columns apart; the iris is coloured and
  lighter in its lower row; most draw no mouth; the face is the light skin tone with the mid tone
  only as shade (a mid-tone face swallows the eyes). Three variants at 12x on the arena and a dark
  card, with the full body at 3x and 1x and the base faces underneath, settled it: the user took
  the base-game eyes with a small muted mouth, then switched to League's stern look (a heavy
  three-square brow, one row of eye - white beside a dark pupil - and a one-square mouth in dark
  brown). Draw two or three faces from the start instead of one by the rule.
- **Keep the mouth on the face's middle line.** A 3/4 face turned right has its middle line between
  the near eye's pupil and the far eye, in front of the face's centre, and the mouth sits on it
  (league_darius: pupil at column 67, far eye at 69, mouth at 68). A redraw that moved the mouth one
  square back, under the near eye, and slid the brow back off the pupil got "the mouth is crooked,
  the eyes are strange". League's Darius (the design pose rendered at 1400 px with `pose_ref.py
  --hq`) scowls under slanted brows with stubble; the user kept the base game's two-row eyes and
  took a heavy three-square brow, a furrow before the far brow and stubble on the chin. A changed
  design face is pasted into every frame on the next `restyle_native.py` run; nothing else moves.
- **A pasted head sits on the shoulders, with no neck of its own.** league_janna's head block ended two
  rows under her chin, on the neck drawn for the idle body (an outline down its middle). Stamped on every
  frame, it met League's slender torso, side-on and three pixels wide in Monsoon, and in game the user saw
  the head apart from the body, joined by a pipe. End the block at the chin (a row of plain skin under it
  at most), seat the chin on the shoulders with `"dy"`, and where a pose turns the torso thin under a big
  head, widen the rows under the chin (`restyle_native.py` `"shoulders"`). Check the ult and every
  side-on pose at game size, not only the idle the design was drawn on.
- **A big pasted head needs a body under it, not a pipe.** In the 0.21.0 pass the user still saw league_janna's
  neck and body apart: her drawn head is ~15 squares wide over a body League renders 5 squares wide at head 2.0,
  and in the attack and spells League turns her side-on and throws her legs back, so the little body hung off
  a corner of the head. Two fixes the user accepted: render League's own head smaller (`"chibi"` head 2.0 ->
  1.6, height 28 -> 30), so the body gets more of the height and fills out under the drawn head (then re-seat
  the head: `jx`/`jy` follow League's head size, move `"dx"`/`"dy"` by the change), and blend the lunging frames
  35% toward idle so the body stays under the head (the arm and the staff still move). Measure the torso's lean
  (pelvis to neck on screen) per frame before choosing which frames to calm.
- **Trace the original** (the user's rule, 2026-09-29: "我让你修的英雄如果你感觉奇怪都要用 描原版"). When a
  head, hair or body part looks off, do not redraw it from imagination: render League's model at the sprite's
  scale (or the head a little bigger), vote each 8x8 block into the hero's palette by class, outline it, and
  draw only the features (eyes, brows, mouth) on the traced shape. Freehand Darius heads were rejected one
  after another (a chibi-round face: "诺手的脸有这么胖吗"; a spike crown, a combed-back dome: "发型也不及格"),
  while the trace showed what League's head is at 10 px - a dark hair mass combed back to the nape and a narrow
  long face, the proportions the approved sprite already had. A trace of League's head part carries the neck:
  end the block at the chin, or a lump of skin hangs under the face ("脸下那块肉看起来不怪吗").
- **A monster's face is built from the source's features, not from a chibi face.** For a rock giant the
  base rule (a big round head, three-row eyes) gave a smooth ball with eyes and a mouth, and the user
  rejected all three variants at once as a mascot. oppi's creatures in LoL Reborn (Alistar, Sion) show the
  head from the side: the snout points the way the hero faces, one small eye glows in a dark socket under a
  brow, and the head's mass joins the shoulders. league_malphite's head followed that and League's model
  (a dark stone snout, a thick pale horn standing clear of the spike crest, pale plate tops and cracks).
  Measure where the head meets the body in every frame of every tag (a count of head pixels touching the
  body) before showing a GIF: a pasted head far from the joint it follows floats off in the swings.
- **A prop touching a limb becomes part of it.** In Lux's run, League's wand swings upright
  behind her, and its gold end hangs by her back foot. At game size the end (gold, white and
  skin pixels, no outline between) merged with the leg and read as a gold foot: the user saw
  her lower body deform. Check each frame where a prop end meets a hand, foot or head. Separate
  them with outline or colour, or hide the end behind the limb. Lux's four frames were fixed in
  `lux_retouch.json`. Single-pixel fixes can go in
  `assets/source/native/<hero>_retouch.json`, which `import_native.py` applies after cutting the
  frames; it stops if a source pixel changed.
- **Pose references from the source game.** Without one the model invents the motion: Garen's
  first run trailed the sword and his idle rested it on the shoulder, while in League both hold
  it forward at the waist - the user spotted it at once. Render the real clips (for LoL:
  `tools/lol/pose_ref.py` in TFM2-League-Heroes, reads SKN/SKL/ANM from the local client) and
  attach them as a second image: "copy each frame's pose, draw it like the first image". Keep
  such renders local; they show the game's model. Make the first and last frame of an action a
  half-way blend with idle (`pose_ref.py --frame "idle@0>attack@0:0.5"`) so the strip starts and
  ends near the idle pose, and render every clip of a hero from the same side (Ashe:
  `ashe_pose_*` in `assets/source/ashe/PROMPTS.md`).
- **Name the gait and time it from the clip.** The move tag is called `run`, but League's Garen
  marches: upright, 0.93 s a cycle. Prompted as a run, he came out leaning into a sprint at
  0.54 s and the user saw "running, not walking". Say WALK (upright, one foot always down) when
  the clip is a walk, and take the frame times from it (Garen: 8 frames x 117 ms).
- **The move is League's movement clip at League's pace** (the user's rule, 2026-09-29: "英雄联盟原版的
  走路姿势"). A unit plays its `run` tag whenever it moves, so draw what League plays when the champion
  moves at base speed, at League's speed. `python tools/lol/anim_graph.py <Champ> --grep run` reads the
  animation graph: its `Run` clip picks a clip by a condition (Ekko: a `ConditionFloat` on move speed,
  `run_base` = `PunkGenius_Run1` from 315, `Run_Haste` from 535; Yone: a `ConditionBool` on the
  homeguard buff, `run_base` = `Yone_Walk01`, a walk), and `run_base` is the move. A cycle takes the
  clip's frames times its `mTickDuration` (1/30 s unless set): Ekko's Run1 1.067 s (8 x 133 ms), Yone's
  Walk01 38 frames at 1/35 s = 1.086 s (8 x 136 ms). A clip named Run is not always the move: Yone's
  `Yone_Run01` is `run_fast`, which `Run` never plays (another switch in the graph picks it). In game a unit crosses the ground at
  66 px a second (move speed 1100) whatever its run shows, and League's paces slide a little at game
  size (Ekko's planted foot goes back about 2.8 px a frame, 21 px a second at 133 ms); the user takes
  League's look over less sliding: Ekko at 8 x 80 ms and Yone's Run01 at 8 x 80 ms, picked to hide the
  slide, were both set back to League's pace when the user saw them differ from League. Never calm a
  run by blending it toward a crouched or wide-legged idle, which takes the stride with it (Ekko's first
  run, 60% toward his crouch, glided: "像僵尸步"). This is for new heroes and for a merged hero the user
  names; the approved heroes' runs stay as they are unless the user asks. A floater's move keeps League's float: league_kayle's glide rises and
  sinks 16 px over its 4.27 s (`Kayle_Run1`, one cycle whose halves differ, 16 x 267 ms); the user took it as League
  has it over a halved and a flat float, lifted only until its lowest frame's feet touch the ground (`"sink"`).
- **Render the side that shows the chest.** Every base champion faces right with its front to the
  viewer. League's Garen idles with his chest toward his own right, so a right-front camera
  shows his back - round 2 came out as a back view and the user rejected it at once. Render his
  left side and flip it (`pose_ref.py --mirror`), check the face and crest are visible, and say
  "3/4 FRONT view ... never show his back" in the prompt. Effects: separate strips,
  centred or with a fixed impact point, no outline, empty centre for rings around the hero.
- **Frames are not on a grid.** The model shifts the body inside its cell to fit a long weapon,
  and the spacing drifts (Garen: the body moved up to 13 px at game scale, the spacing
  drifted about 0.5 px per frame). Split
  at empty columns and keep connected blobs whole (`split_strip`); never place frames by cell.
- **Props that leave the body cross the cells.** Lux's Final Spark wand floats a third of a cell
  to her right, so `split_strip` handed frame 5's wand and blast to frame 6. Split such a strip by
  blobs instead: a blob holding the body's signature colour (her navy bodysuit) is a body, every
  other blob (prop, glow, sparks) joins the nearest body on its left (`split_bodies` in
  tools/art/import_lux.py).
- **Scale per strip.** Every generated strip comes at its own size (Garen round 4: the Q strip at
  half of idle's size, battle cry and hit far bigger). Pick a frame in idle's pose (the ready
  stance most strips start or end in), render it next to idle at game size at a few scales and
  choose by eye - head widths and hair-to-soles numbers were off by up to 2x on small or glowing
  frames. 36 px suits a big human (base humans ~31 px, the ogre ~38); 42 px looked like a giant.
  For chibi strips, scale by the **head**: GPT's head-to-body ratio also drifts between strips
  (Ashe's redraw: ~10%), so matching heights makes the head grow and shrink - the thing the user
  notices. Correlate idle's head (crown to chin) over each frame at a range of scales; within a
  strip the best scale agreed to 0.03 wherever the match was sure (>0.85). Where the head turns or
  bows (Garen's attack and death) the match is unsure: compare face and hair width at source size
  instead (the frame resized by 1/scale next to idle's head).
- **Lunges.** League blends back to idle over ~0.2 s; a sprite snaps back at once. Garen's attack
  head track (a 15 px lunge) made him jump back every swing, so attack, Q and R keep 65-70% of
  League's travel around idle's head, like the round the user approved. Get the tracks with
  `pose_ref.py --frame ... --track <hero px> --track-ref <idle clip@0>` (same camera, `--mirror`,
  `--head`, `--legs` as the references); it reproduces the tracks measured by hand before.
- **One look per hero.** Strips from different generation rounds disagree on proportions (round
  1 Garen: big head, broad shoulders; round 3: smaller head for the same height). No scale hides
  it - in-game he visibly grew and shrank between animations. When the look changes, regenerate
  every strip in one batch with the newest frame as design and size reference.
- **Horizontal pivot per frame.** Line the lowest ~12 px of legs up with idle frame 0
  (`leg_band` + `best_shift`); loops that turn or run (spin, run) are pinned by the head. A sword
  tip, smear or burst touching the ground gets matched as a foot: place those frames by the drawn
  spacing, corrected like their aligned neighbours, then nudge so one foot stays planted.
  Airborne frames keep their height above the strip's ground line.
- **Better, for strips drawn from a League clip:** put each frame's head where League's skeleton
  has it at the same frame time and camera (Garen's lunges and leaps then match the game).
  Re-base clips that start away from the unit (Garen's R starts 12 px behind it), and pin the
  feet's midpoint instead for a spin whose drawn lean is smaller than the clip's, or the body
  wobbles.
- **Pixels.** Premultiplied area downscale, alpha cut 0.5, one median-cut palette for all body
  frames (64 colours), then a 1 px near-black edge except on glowing pixels, then drop lonely
  pixels. Effects: alpha cut 0.4 plus tiny-spark keeping, own 32-colour palette, no outline.
- **Thin bright details need a vote, not an average.** Ashe's strips were ~12 source px per game
  px with a thin crystal bow and silver hair on a black hood: the average turned her into brown
  mud, the hair grey and the bow black (all edge, so all outline). `strips.render_vote` gives each
  game pixel the one palette colour covering most of it, times a class weight (bow blue 2.2, hair
  2.3, skin and gold 1.3); build that palette with a median cut per colour class (the lavender
  hair otherwise merges into light skin) and pass the prop's colours to `outline(keep=...)`.
  `metrics` then reports a lower outline share - it is the prop's edge, check which colours.
- **Detail density: have the body drawn at the game's size.** A vote does not save a strip drawn
  ~100 blocks tall (GPT's "pixel art") and squeezed 3:1 into 34 px: Ashe and Lux shipped at 41-42
  colours per idle frame with 15-18% of pixels matching their right neighbour (15 base heroes:
  16-33 colours, 18-46%, median 32%; Garen's big armour stayed readable at 63 and 15%), and the
  user saw both blurry in game. A second round drawn at native size fixed it (TFM2-League-Heroes
  `assets/source/NATIVE_REDRAW.md`): the current game frames at 8x in 56x64 cells as pose
  references, base heroes at 8x for style, "34 squares tall, every pixel one 8x8 square, at most
  20 colours, 2x2-square eyes", the design sheet first. The model's own output drifts off the grid
  (block pitch 7.4-8.6 px, narrowed faces); have it cleaned to exact 8x8 blocks, check that, then
  read one pixel per block - no resampling, palette or outline pass (`tools/art/import_native.py`:
  18-19 colours, 29-31%). Record where each reference frame's pivot sits in its cell when the
  references are drawn (`native_refs.py` writes `<hero>_cells.json`) so each redrawn frame lands
  where the old one stood, and steady idle and run on the head column: frames placed by their
  bounding box twitched 1-2 px in those loops. For a new hero, skip the first round: render
  League's clips straight at game size (`tools/lol/native_pose.py`) and give GPT that 8x
  reference next to the same frames as a high-resolution render. Lee Sin came back in one round,
  but GPT drew his actions ~1.4x the approved design (only idle, re-layered from the design by
  Codex, was right): measure each strip's head against idle (blindfold/eye size, band thickness)
  and shrink by that before importing (`tools/art/fit_native.py`: a 1.4x shrink by colour vote
  stays clean; 37% right-neighbour, 16 colours) - importing as delivered would make him grow
  whenever he moves.
- **Close small holes inside the body.** At game size a gap between a limb and the body (league_kayle's near arm
  held off her waist) is a few empty pixels in an outline ring: a black hole in the armour. `restyle_native.py`
  `"fill_holes": <pixels>` fills every empty region the frame's edge cannot reach, up to that size, and its inner
  outline with the body colours beside it; left out, every other hero's output is byte-identical.
- **Effect anchors.** Effect and buff frames are drawn centred on the unit's pivot, 11.5 px above
  the feet (base: `levelup_effect` ring at +9..+16, `shield_receive_effect` bubble -22..+13).
  Ground rings at about +10, hits and shields at -3..-6, overhead marks around -25. Time the
  impact frame to the damage tick (wrap the `ViewEffect` in `Delayed`). Find a ring by its biggest
  connected blob: by row extent, motes rising at both sides make rows above the ring look wide.
  For effects drawn in place (bursts, marks, bubbles, ground fields) anchor each frame on its
  cell: GPT centres every frame in its equal-width cell (within 8 px on all seven of Lux's), while
  a frame's own box drifts with its loose sparks - take the cell centre plus the strip's median
  offset across, and one height for the strip. A single anchor in strip coordinates puts every
  frame at its own cell's distance from the pivot (Lux's first import: the hit walked 5 cells).
  Projectiles keep a per-frame anchor on their head (arrow tip, orb).
- **Review before shipping.** Per-strip sheets with the idle silhouette overlaid, `metrics`,
  a side-by-side with base champions at 1x and 3x, and a scripted showcase against a dummy.

## QA checklist

- [ ] `metrics` passes: height, outline, 0 semi-alpha, colour count
- [ ] `idle`, `run`, plus every `action_name` and `CasterAnimation` name exists as a tag
      (`lint_mod.py` checks this against the data); `hit` and `dead` recommended
- [ ] feet stay on the same row in all frames; hero stands level with base champions in-game
- [ ] readable at 1x on the olive-grey arena; signature colour visible
- [ ] VFX visible on both light and dark map areas; no black outline on VFX
- [ ] three icons per hero, one consistent style across the pack (24x24 glyph or 64x64 art)
