# 凯南特效原稿生成提示词

生成工具：内置 image_gen；transparent_background=true。

共同追加要求：

Production: true alpha transparency, no background pixels, NO soft bloom or blurred glow, no black outlines. Deliberately chunky low-resolution tactical-game VFX, each visible block corresponds to a game pixel, few colors, not detailed illustration. Exactly the requested frame count in one uniform horizontal row. Leave transparent breathing room at all cell edges. Do not draw any characters, labels or grid lines. If exact requested image size is unsupported, preserve frame count and row layout; actual size can differ.

## 1. kennen_fx_a_star.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a gold ramp (#FFF4C8, #FEDC80, #F8A23B, #CB7420) with a white highlight.
Effect: a SMALL SPINNING SHURIKEN, 4 frames, a seamless loop: a gold four-pointed throwing star with a tiny dark hole in its middle and a white glint on one point, turning a quarter of 90 degrees each frame so the 4 frames loop.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 2. kennen_fx_a_cast.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a gold ramp (#FFF4C8, #FEDC80, #F8A23B, #CB7420) with white.
Effect: a SMALL THROW FLASH, 3 frames: 1 a tiny white point; 2 a small four-pointed gold-white flash with two short wind streaks to the right; 3 the flash fades to two gold specks.
Layout: one horizontal row of 3 equal square cells, image size 768x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 3. kennen_fx_a_hit.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a gold ramp (#FFF4C8, #FEDC80, #F8A23B, #CB7420) with white.
Effect: a SMALL SHURIKEN HIT, 4 frames: 1 a white flash; 2 a gold burst with 4 short spikes; 3 the spikes break into small gold sparks flying outward; 4 a few fading specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 4. kennen_fx_a_cast2.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a CHARGED THROW FLASH, 4 frames: 1 a white point; 2 a violet-white electric flash with 3 short jagged lightning forks jumping out; 3 the forks flicker to new places, cyan sparks; 4 they fade.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 5. kennen_fx_a_hit2.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: an ELECTRIC HIT, 5 frames: 1 a white flash at the center; 2 a violet-white burst with 4 jagged lightning forks shooting out; 3 the forks jump to new places around the center, cyan sparks; 4 thinner forks, sparks flying out; 5 a few fading violet specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 6. kennen_fx_k_mark1.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4).
Effect: a MARK COUNTER floating over a head, 4 frames: three small lightning-bolt symbols side by side (each about 4 squares tall, zigzag shaped); the LEFT one lit bright violet-white, the other two dark violet empty slots; 1 the lit symbol flashes white; 2-4 it settles to bright violet and the row stays.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the row of symbols centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 7. kennen_fx_k_mark2.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4).
Effect: a MARK COUNTER floating over a head, 4 frames: the same three small lightning-bolt symbols; the LEFT TWO lit bright violet-white, the right one a dark violet empty slot; 1 the second symbol flashes white; 2-4 both lit symbols crackle slightly.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the row of symbols centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 8. kennen_fx_k_stun.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a LIGHTNING STUN around a standing figure (do NOT draw the figure), 10 frames: 1-2 three small lightning-bolt symbols flash white over the head and burst; 3-9 jagged violet-white lightning crackles all over the figure's outline from head to feet - 3-4 forks that jump to new places every frame - and a small ring of violet sparks spins over the head; 10 the lightning fades to a few sparks.
Layout: one horizontal row of 10 equal cells, each 4 wide to 5 tall, image size 5120x1280 (each cell 512x640); the figure's place centered at the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 9. kennen_fx_q_star.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a gold ramp (#FFF4C8, #FEDC80, #F8A23B, #CB7420) for the shuriken and a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a FLYING LIGHTNING SHURIKEN moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the front (right) a gold four-pointed throwing star, spinning (a quarter turn over the 4 frames), wrapped in flickering violet-white electric sparks; behind it (to the left) a jagged violet lightning trail that changes shape every frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the shuriken on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 10. kennen_fx_q_cast.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with gold sparks (#FFF4C8, #FEDC80, #F8A23B, #CB7420).
Effect: a LIGHTNING THROW FLASH, 4 frames: 1 a white point; 2 a violet-white electric flash, 2 short lightning forks and a few gold sparks; 3 the flash at full size; 4 it fades.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 11. kennen_fx_q_hit.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5) and gold sparks (#FFF4C8, #FEDC80, #F8A23B, #CB7420).
Effect: a LIGHTNING SHURIKEN IMPACT, 5 frames: 1 a white flash; 2 a star-shaped violet-white electric burst with gold sparks; 3 5-6 jagged lightning forks shoot outward; 4 the forks break into cyan and violet sparks; 5 fading specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 12. kennen_fx_w_burst.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: an ELECTRIC SURGE around a figure (do NOT draw the figure), 7 frames: 1 a white flash at the center bottom; 2 a ring of violet-white electricity starts on the ground (a flattened ellipse, twice as wide as tall) and 6-8 jagged lightning forks shoot outward from the center; 3 THE SURGE: the ring at two thirds of the cell's width, 10-12 forks reaching outward, cyan sparks; 4 the ring reaches the cell's edges, the forks flicker; 5 the ring thins and breaks into arcs; 6 the forks fade to violet; 7 a few sparks.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 3584x256 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 13. kennen_fx_w_hit.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a SMALL ELECTRIC SHOCK, 4 frames: 1 a white flash; 2 a violet-white burst with 3 short lightning forks; 3 the forks jump to new places, cyan sparks; 4 they fade.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 14. kennen_fx_e_in.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a LIGHTNING TRANSFORM FLASH, 4 frames: 1 a white flash; 2 a round violet-white electric burst with a cyan jagged edge; 3 the burst stretches to the right, 3 lightning forks whipping right; 4 it fades to sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 15. kennen_fx_e_ball.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a BALL OF LIGHTNING around a small dashing figure (do NOT draw the figure; keep the middle open so the figure shows through), 4 frames, a seamless loop: a round shell of jagged violet-white electricity with spiky cyan edges, 3-4 lightning forks crawling over it that change place every frame, and 3 short lightning streaks trailing to the LEFT behind it.
Layout: one horizontal row of 4 equal cells, each 6 wide to 5 tall, image size 3072x640 (each cell 768x640); the ball centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 16. kennen_fx_e_hit.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a SMALL ELECTRIC ZAP, 4 frames: 1 a white flash; 2 a small violet-white burst with 2 lightning forks; 3 cyan sparks; 4 fading specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 17. kennen_fx_e_out.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a LIGHTNING BALL BREAKING, 5 frames: 1 a round violet-white electric shell with cyan spikes; 2 it bursts: a white flash and 6 lightning forks shooting outward; 3 the forks break into sparks; 4 sparks fly out and fade; 5 a few specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 18. kennen_fx_r_storm.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5), dark storm clouds (#2A1446, #3E2066, #5B3590) and gold (#FFF4C8, #FEDC80, #F8A23B, #CB7420) for the small shurikens.
Effect: a SWIRLING LIGHTNING STORM around a figure (do NOT draw the figure), 12 frames: a wide flattened ring on the ground (twice as wide as tall) made of dark violet storm clouds and 6-8 small spinning gold shurikens circling around the center; 2-3 jagged violet-white lightning bolts strike down onto the ring from above in every frame, at new places each frame; 1-2 the ring forms from the center outward; 3-10 the ring turns (the clouds and shurikens move a little around the circle each frame) - a seamless loop from 10 back to 3; 11-12 the ring breaks up and fades.
Layout: one horizontal row of 12 equal cells, each 2 wide to 1 tall, image size 6144x256 (each cell 512x256); the ellipse centered in the lower part of every cell, the lightning reaching up. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 19. kennen_fx_r_hit.png

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a LIGHTNING BOLT STRIKE, 5 frames: 1 a thin white bolt appears from the top of the cell down to the bottom; 2 the bolt at full thickness, jagged, violet-white with a white core, and a burst of electricity where it hits the bottom; 3 the bolt flickers to a new jagged shape, the burst widens, cyan sparks; 4 the bolt breaks into short pieces; 5 a fading glow at the bottom.
Layout: one horizontal row of 5 equal cells, each 1 wide to 3 tall, image size 1280x768 (each cell 256x768); the bolt centered, its impact at the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.

## 重生成与修订

### 1 手里剑旋转

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a gold ramp (#FFF4C8, #FEDC80, #F8A23B, #CB7420) with a white highlight.
Effect: a SMALL SPINNING SHURIKEN, 4 frames, a seamless loop: a gold four-pointed throwing star with a tiny dark hole in its middle and a white glint on one point, turning a quarter of 90 degrees each frame so the 4 frames loop.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Production: true alpha transparency, no background pixels, NO soft bloom or blurred glow, no black outlines. Deliberately chunky low-resolution tactical-game VFX, each visible block corresponds to a game pixel, few colors, not detailed illustration. Exactly the requested frame count in one uniform horizontal row. Leave transparent breathing room at all cell edges. Do not draw any characters, labels or grid lines. If exact requested image size is unsupported, preserve frame count and row layout; actual size can differ.
CRITICAL rotation angles for FOUR stars in left-to-right order: 0 degrees (cardinal cross), 22.5 degrees (tilted halfway between cross and X), 45 degrees (diagonal X), 67.5 degrees (tilted halfway between X and next cross). Four VISIBLY DISTINCT angular orientations, NOT cross/X/cross/X. Pixel cluster approximation at 16x16 resolution is acceptable. Identical shape scale and small center hole. Transparent gutter 15% of cell width. Gold and white only.

后续定向编辑：

Edit this four-frame gold shuriken sprite sheet. Keep transparent background, pixel style, colors, four equally spaced isolated stars, dimensions and small center holes. ONLY change orientation of SECOND star from the left: rotate it to 22.5 degrees clockwise from a cardinal cross, halfway between the FIRST cardinal cross and the THIRD diagonal X. Leave first cross and third X. Set fourth orientation 67.5 degrees clockwise from first. Four incremental 22.5-degree rotations must be distinct: first up/right/down/left; second top-right leaning mostly upward/right/down/left; third diagonal X; fourth the opposite in-between orientation. Do not repeat second and third. No background, shadow, labels, additional frames or outlines.

### 9 Q 飞行图

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a gold ramp (#FFF4C8, #FEDC80, #F8A23B, #CB7420) for the shuriken and a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a FLYING LIGHTNING SHURIKEN moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the front (right) a gold four-pointed throwing star, spinning (a quarter turn over the 4 frames), wrapped in flickering violet-white electric sparks; behind it (to the left) a jagged violet lightning trail that changes shape every frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the shuriken on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Production: true alpha transparency, no background pixels, NO soft bloom or blurred glow, no black outlines. Deliberately chunky low-resolution tactical-game VFX, each visible block corresponds to a game pixel, few colors, not detailed illustration. Exactly the requested frame count in one uniform horizontal row. Leave transparent breathing room at all cell edges. Do not draw any characters, labels or grid lines. If exact requested image size is unsupported, preserve frame count and row layout; actual size can differ.
CRITICAL graphic: FOUR isolated mirrored projectiles, each centered in its quarter panel. Draw each frame as a horizontally symmetric icon: gold four-point star on RIGHT, one thin zigzag white-core purple trail on horizontal centerline stretching LEFT, with any lightning fork above matched exactly by a reflected fork below. No random asymmetric sparks. Upper silhouette is exact mirror of lower silhouette. Visible star orientations across frames cross, 22.5 tilt, X, opposite tilt; prioritize mirrored projectile silhouettes. Each effect fits middle 80% of its cell width, no touching neighbor.

### 12 W 放电

Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: an ELECTRIC SURGE around a figure (do NOT draw the figure), 7 frames: 1 a white flash at the center bottom; 2 a ring of violet-white electricity starts on the ground (a flattened ellipse, twice as wide as tall) and 6-8 jagged lightning forks shoot outward from the center; 3 THE SURGE: the ring at two thirds of the cell's width, 10-12 forks reaching outward, cyan sparks; 4 the ring reaches the cell's edges, the forks flicker; 5 the ring thins and breaks into arcs; 6 the forks fade to violet; 7 a few sparks.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 3584x256 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Production: true alpha transparency, no background pixels, NO soft bloom or blurred glow, no black outlines. Deliberately chunky low-resolution tactical-game VFX, each visible block corresponds to a game pixel, few colors, not detailed illustration. Exactly the requested frame count in one uniform horizontal row. Leave transparent breathing room at all cell edges. Do not draw any characters, labels or grid lines. If exact requested image size is unsupported, preserve frame count and row layout; actual size can differ.
CRITICAL DESIGN: Seven SMALL isolated effects. Centers along one baseline at canvas x positions 7.14%,21.43%,35.71%,50%,64.29%,78.57%,92.86%. Each effect ONLY uses middle 65% of its 1/7-width cell (large transparent side margins), even peak frames. Never overlap or touch adjacent frames. Use a simplified flatter 2:1 ground ellipse ring, avoid crowns/flames. Lightning forks angle RADIALLY outward parallel to ground, with only a few short upward arcs. Very chunky intentional low resolution square clusters. Frame 7 only 3-4 specks, no surviving arcs. No purple glow haze, no white fuzzy halo.

