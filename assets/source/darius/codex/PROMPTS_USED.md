# 实际调用生图接口的提示词

共 19 次，全部成功。动作每次按所列顺序附 3 张图；特效无附图。之后进行原尺寸角色重绘和特效像素整理。

## 2. darius_idle.png

附图：darius_native.png → darius_native_idle.png → darius_pose_idle.png

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: IDLE, 6 frames, a seamless gentle loop, as in the SECOND image: he stands firm and menacing, the huge axe hanging from the hand on the left of the image with its blade by his feet, his other hand at his side, and breathes slowly - his body (not the boots) is one square lower in frames 1, 2 and 6 than in frames 3, 4 and 5; the axe moves with his hand; the cape sways a little. The head is exactly the same drawing in all 6 frames, it only moves up and down with the body; the boots stay planted.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2112x1536; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

## 3. darius_run.png

附图：darius_native.png → darius_native_run.png → darius_pose_run.png

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: RUN loop, 8 frames, as in the SECOND image: a heavy, powerful bounding run, leaning forward; he carries the axe low in the hand on the left of the image, the ring end up behind his shoulder and the blade down by his legs; his other arm swings; one boot on the ground in frames 3 and 7, both boots off the ground in the other frames; his body rises in the air and dips at each landing; the cape streams out behind him. Keep his head in the same column in every frame, as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2816x1536; frame N in the same cell as in the SECOND image, at the same place and height, the soles (or the ground line under them) 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

## 4. darius_attack.png

附图：darius_native.png → darius_native_attack.png → darius_pose_attack.png

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: BASIC ATTACK, a two-handed overhead axe chop, 6 frames, as in the SECOND image: 1 leaving his stance; 2 he heaves the axe high up behind his head, blade up; 3 he lunges forward, the axe swung back behind him; 4 the axe comes round and down, low; 5 THE HIT: he lunges forward and chops the blade into the ground in front of him (to the right), his cape flying out behind; 6 back toward his stance. Draw no slash and no blood - they are separate effects.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2112x1536; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

## 5. darius_skill.png

附图：darius_native.png → darius_native_skill.png → darius_pose_skill.png

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: DECIMATE, a wind-up and a full-circle axe swing, 8 frames, as in the SECOND image: 1 leaving his stance; 2-3 he heaves the axe up and back over his far shoulder with both hands, winding up; 4 he crouches and starts the swing, the axe low behind him; 5 THE SPIN: he whirls round, the axe held out at full reach to the right; 6 still whirling, the axe swept round behind him to the lower left, his cape flaring out; 7 the axe comes round in front again, reaching out to the right; 8 back toward his stance. The axe is very long at full reach - draw it inside the cell as in the SECOND image. Draw no motion trail - the spin is a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2816x1536; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

## 6. darius_w_attack.png

附图：darius_native.png → darius_native_w_attack.png → darius_pose_w_attack.png

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: CRIPPLING STRIKE, a low sweeping cut at the enemy's legs, 6 frames, as in the SECOND image: 1 he crouches low, the axe drawn back low behind him; 2 he whirls it low along the ground; 3 the axe low behind him again as he turns; 4 the axe sweeps low in front of his legs; 5 THE HIT: crouched, the blade sweeping at knee height in front of him (to the right); 6 back toward his stance. Draw no slash and no blood - they are separate effects.
Layout: exactly like the SECOND image - a grid of 3 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2112x1536; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

## 7. darius_skill2.png

附图：darius_native.png → darius_native_skill2.png → darius_pose_skill2.png

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: APPREHEND, a hooking pull, 8 frames, as in the SECOND image: 1 leaving his stance, crouching; 2 he leaps forward, swinging the axe low; 3 lunging, he throws the axe forward and down; 4 THE HOOK: the axe held out at full reach far to the right, its hooked blade catching the enemy, both arms stretched out, his body low at the left of the cell; 5-6 he yanks the axe back toward himself; 7 the axe pulled back behind him, crouched; 8 back toward his stance. The axe is very long at full reach - draw it inside the cell as in the SECOND image. Draw no streak and no glow - they are separate effects.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2816x1536; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

## 8. darius_ult.png

附图：darius_native.png → darius_native_ult.png → darius_pose_ult.png

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in every frame - the same size, the same black spiky hair covering his head, the same eyes (the near eye on the left 2 squares wide, the far eye 1 square, each 3 rows tall) and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image and the same size in every frame: a 1-square dark iron handle with the 3x3 iron ring at its top end, and at its bottom end the double-crescent head - a dark iron hub with a white emblem, a big tall crescent blade on one side and a smaller crescent on the other, pale cyan cutting edges, curved notches between the blade tips and the handle (never a heart, a V or a solid wedge) - separated from his hands and legs by an outline, in the hands shown in the SECOND image. 3/4 FRONT view facing right; never draw his back - when he turns or swings, keep his face and chest turned toward the viewer.
Animation: NOXIAN GUILLOTINE, a leaping execution, 8 frames, as in the SECOND image: 1 he crouches, gripping the axe; 2 he leaps up, raising the axe over his head with both hands; 3-4 high in the air, the axe held up behind his head; 5 dropping, the axe raised straight up above him; 6 THE SLAM: he lands crouched and drives the blade down into the ground in front of him (to the right; the blade reaches below the line of his soles, exactly as in the SECOND image); 7 holding the slam; 8 standing up toward his stance. He is in the air in frames 2-5 exactly as high as in the SECOND image. Draw no giant axe, no glow and no blood - they are a separate effect.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells, each cell 88x96 squares (704x768 px), image 2816x1536; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

## 9. darius_hit.png

附图：darius_native.png → darius_native_hit.png → darius_pose_hit.png

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the head of the FIRST image, copied square for square, in both frames - the same black spiky hair, the same eyes and the same one-square dark red mouth. Keep the axe exactly as in the FIRST image, separated from his body by an outline. 3/4 FRONT view facing right, never his back.
Animation: HIT, 2 frames, as in the SECOND image: 1 he flinches from a blow - hunching a little, head dipped, the axe tilting; 2 recovering toward his stance.
Layout: exactly like the SECOND image - a grid of 2 columns x 1 row of cells, each cell 88x96 squares (704x768 px), image 1408x768; frame N in the same cell as in the SECOND image, at the same place, the soles on the same line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

## 10. darius_dead.png

附图：darius_native.png → darius_native_dead.png → darius_pose_dead.png

```text
Three attached images. FIRST: the approved clean pixel-art design of Darius at 8x (every pixel an 8x8 block) - copy his colors, shapes, face and pixel style exactly. SECOND: League of Legends' real animation of Darius rendered at our game's sprite size and shown at 8x, frames in a grid of cells read left to right, top to bottom - copy each frame's pose, size and position in its cell exactly, but NOT its blurry pixels. THIRD: the same frames as a high-resolution render, same grid, same places - look at it wherever a pose in the SECOND image is hard to read.
Task: redraw every frame of the SECOND image as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size: standing he is 34 pixels tall from the tips of his hair to his soles, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur.
Pixel rules (most important): at most 20 colors (those of the FIRST image); big flat areas, 2-3 shades per material; no dithering, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette. His head is EXACTLY the size of the head in the FIRST image, counted in squares, in every frame. Keep the axe exactly as in the FIRST image. The same camera as the FIRST image.
Animation: DEATH, 7 frames, as in the SECOND image: 1 struck, he doubles over, head down; 2 he twists and staggers; 3 he sinks to his knees; 4 he topples backwards, the axe flung up out of his hands; 5 he falls on his back; 6-7 he lies on the ground, his cape spread under him, the axe lying on the ground beyond his head. Draw the axe exactly where the SECOND image has it, inside the cell. He lies on the ground line in frames 5-7, exactly as high as in the SECOND image.
Layout: exactly like the SECOND image - a grid of 4 columns x 2 rows of cells (the last cell stays empty), each cell 88x96 squares (704x768 px), image 2816x1536; frame N in the same cell as in the SECOND image, at the same place and height, the ground line 18 squares above the bottom of the cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels.
```

## 11. darius_fx_hit.png

附图：无

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFFFFF, #FFC2B8, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF, #7E8A94).
Effect: a heavy AXE CHOP hit, 5 frames: 1 a white flash where the blade lands; 2 a thick crescent slash cutting diagonally down from upper left to lower right, white core with a crimson edge; 3 the slash splits and dark red sparks and a few blood drops burst out; 4 the sparks fly apart and shrink; 5 the last red specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, the slash at most 70% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

## 12. darius_fx_bleed.png

附图：无

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood color ramp (#FFC2B8, #FF3B30, #B3121F, #5A0710).
Effect: HEMORRHAGE, a bleeding wound, 5 frames: 1 a small red slash glint; 2 three or four fat blood drops spurt up and out from it; 3 the drops arc outward and down; 4 they fall, smaller; 5 two last drops fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the wound at the center of every cell, the whole effect at most 45% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

## 13. darius_fx_q_spin.png

附图：无

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFFFFF, #FFC2B8, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF, #7E8A94).
Effect: DECIMATE, a giant axe swung in a full circle around a warrior, seen from the same slightly top-down game camera, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 40% of the cell height stands there, feet at 70% of the cell height) - never draw the person. The swing is a slightly flattened ring about 1.3 times wider than tall, filling 92% of the cell width, centered at the person's waist. 1 a short bright arc starts at the right side of the ring, a white-hot leading edge; 2 the arc sweeps round the front and the left: a thick crescent of crimson with a white edge and a steel-grey trail behind it; 3 the arc sweeps round the back, almost closing the ring; 4 THE FULL RING: a complete thick crimson ring with a white-hot outer edge, a few blood drops flung outward; 5 the ring breaks into curved crimson streaks spinning outward; 6 the last dark red wisps fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

## 14. darius_fx_q_heal.png

附图：无

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood color ramp (#FFFFFF, #FFC2B8, #FF3B30, #B3121F, #5A0710).
Effect: a warrior drinking in the blood of his enemies, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 a few crimson wisps appear at both sides of the cell; 2-3 they curl inward toward the chest of the space as thin red streams with bright tips; 4 a crimson flash at chest height with a pale pink core; 5 a soft red ring pulses out from the chest; 6 the last red specks fade upward.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 70% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

## 15. darius_fx_might.png

附图：无

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark fire color ramp (#FFD9A0, #FF6A2B, #D11E1E, #6E0A12, #2A0508).
Effect: NOXIAN MIGHT, a blood-red battle rage aura around a warrior, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person; the aura is drawn BEHIND him, so it may overlap the space. A flat dark red glowing ellipse on the ground at the feet; tongues of crimson and dark red flame rising all around the space up to a little above the head, their tips curling into black-red smoke; small orange-red embers rising; the flames flicker and climb from frame to frame and frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the aura at most 75% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

## 16. darius_fx_w_ready.png

附图：无

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFC2B8, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF).
Effect: CRIPPLING STRIKE READY, a menacing mark on the ground under a warrior's feet, seen from the same slightly top-down game camera, 4 frames, a seamless loop: a flattened ellipse ring (about 2.5 times wider than tall) of dark crimson on the ground, with three small blade-shaped steel glints spaced around it; the glints slide around the ring a little each frame and pulse from dark red to bright red, frame 4 leading back into frame 1.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the ring centered at 75% of the cell height, 70% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

## 17. darius_fx_w_hit.png

附图：无

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFFFFF, #FFC2B8, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF, #7E8A94).
Effect: CRIPPLING STRIKE on an enemy's legs, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 a white flash at knee height; 2 a long low horizontal slash across the legs of the space, white core and crimson edge, sweeping from left to right; 3 blood sprays from the slash and a dark red X-shaped wound mark appears at the knees; 4 two short iron chain links snap shut around the ankles, dark red and steel; 5 the chains and the X mark flash once; 6 they fade into red specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 70% of the cell wide, around the lower half of the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

## 18. darius_fx_e_hook.png

附图：无

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFC2B8, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF, #7E8A94, #3C434A).
Effect: an enemy CAUGHT by an axe hook and yanked toward the LEFT, 5 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 60% of the cell height stands there, feet at 88% of the cell height) - never draw the person. 1 a curved steel hook glint snaps shut at chest height on the right side of the space; 2 a crimson jolt bursts from it; 3-4 dark red speed streaks stretch from the space toward the LEFT edge of the cell, showing the pull; 5 the streaks fade.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the effect at most 80% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

## 19. darius_fx_e_sweep.png

附图：无

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFFFFF, #FF3B30, #B3121F, #5A0710) with steel greys (#F2F6F8, #BFC8CF, #7E8A94, #3C434A).
Effect: APPREHEND, a giant axe hook sweeping out in a cone and yanking back, seen from the same slightly top-down game camera, pointing to the RIGHT, 5 frames. The warrior stands at the middle of the LEFT edge of every cell (never draw him): the cone opens from that point to the right, about 90 degrees wide, reaching the right edge. 1 a fan of three or four hooked steel-grey arcs shoots out from the left point toward the right, crimson streaks behind them; 2 THE FULL SWEEP: the hooked arcs reach the right part of the cell, a wide dark red fan glowing behind them; 3 the hooks snap back toward the left point, bright crimson pull streaks pointing left; 4 the streaks converge on the left point; 5 the last dark red wisps fading.
Layout: one horizontal row of 5 equal cells, each twice as wide as tall (2:1), image size 2560x256; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

## 20. darius_fx_r_impact.png

附图：无

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blood-and-steel color ramp (#FFFFFF, #FFC2B8, #FF3B30, #B3121F, #5A0710) with a dark fire accent (#FF6A2B, #2A0508) and steel greys (#F2F6F8, #BFC8CF).
Effect: NOXIAN GUILLOTINE, a giant ghostly executioner's axe slamming down on a target, 8 frames. The impact point is at the horizontal center of every cell, 12% of the cell height above the bottom edge (the target's feet; never draw the target). 1 a red glint high up near the top of the cell; 2 a huge spectral axe blade (crimson and dark red, with a white-hot cutting edge and a steel-grey handle top) appears high above, raised; 3 it drops fast toward the impact point with a crimson motion trail; 4 THE IMPACT: the blade hits the impact point, a blinding white-red flash; 5 a flattened crimson shockwave ring bursts on the ground around the impact point (about 1.3 times wider than tall, 70% of the cell width), a column of red light rising from it; 6 the ring widens to 90% of the cell width and blood-red shards fly up; 7 the column fades, embers drifting up; 8 the last red embers fading.
Layout: one horizontal row of 8 equal cells, each twice as tall as wide (1:2), image size 2048x512; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```
