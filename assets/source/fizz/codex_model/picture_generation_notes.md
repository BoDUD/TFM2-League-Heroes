# Fizz 图片生成记录

使用内置 image_gen 工具，参考素材来自用户提供的 fizz_picture_pack.zip。

A：1536×1024，RGBA PNG，双手横握三叉戟。
B：1024×1536，RGBA PNG，倒置三叉戟拄地。

两张包含真实 alpha 透明通道。B 已再次调整为更大的四周留白。检查发现生成工具仍留下了少量极淡的半透明外缘；最终文件保留当前效果，未用程序修改像素。

## A 初始生成提示词

Use case: stylized-concept. Create ONE final full-body illustration of Fizz, the Tidal Trickster from League of Legends, classic in-game look. Picture A: 1536x1024 landscape RGBA PNG, true transparent background.
References: images 01 and 02 are ART STYLE AND PROPORTIONS ONLY (Tristana, Veigar): crisp detailed pixel art, dark stepped pixel outlines, 3–5 flat tones per material, bold chibi forms. Do not copy their characters, weapons, backgrounds, glow. Image 03 is authoritative idle pose A; 04 face; 05 drooping fin ears; 08 back fins anatomy only, NEVER copy rear viewpoint; 09 trident design.
Fizz is facing RIGHT in a three-quarter FRONT view, his face and pale belly clearly visible and BOTH big eyes visible, far eye narrower. Big round head 40% of character height, short broad rounded snout, no nose, no hair, thin curved mischievous closed-mouth grin, NO teeth. Cyan blue skin, pale crown spots, cream-yellow throat and belly, large white eyes with green irises, black pupils and one white highlight each, heavy blue upper lids. Two long floppy BLUE fin-ears droop from top of head past shoulders with orange-red inner frills; two additional rear fin-lobes fall behind his back. Thin long arms and small three-fingered hands. Small orange elbow spines. Short tail with small gold ring at base. Legs deepen to navy from knees down, large flat webbed feet with long splayed toes.
Pose A: feet apart, both soles on SAME horizontal baseline, knees gently bent; BOTH hands visibly grip the long trident horizontally across waist. Weapon head faces RIGHT, green-gold finned butt end LEFT. Long crimson-wrapped shaft, silver bands, JADE GREEN three-prong trident head, longest central spike, pale steel edges, small blue gems at junction. Trident length about 1.3 times full character height, entirely inside canvas. Keep recognizable League trident silhouette from reference 09.
Composition: single centered character, about 750 pixels from crown to soles, at least 80 px empty alpha margins on all sides, entire ears, toes and weapon visible. NO pixels or objects below sole baseline, no ground shadow, no backdrop, no halo, no glow, no aura, no water, no text, no border, no pedestal. Genuine transparent alpha outside silhouette. CRISP PIXEL ART with stepped edges and flat clean color clusters, not smooth vector or painting or 3D render.

## A 最终调整提示词

Edit this existing Fizz character illustration. Preserve exactly this character identity, face with BOTH green eyes visible, colors, crisp pixel-art style and both-hands horizontal trident pose. Deliver 1536x1024 landscape. Remove the ENTIRE colored background and every glow/halo behind character and weapon; alpha must be ZERO everywhere outside clean character silhouette. NO aura, shadow, lighting clouds or stray pixels, especially no pixels below feet. Reframe slightly smaller, about 750px crown-to-soles, and center the ENTIRE weapon and character to leave at least 80px genuinely empty transparent margin on ALL four sides. Keep both webbed feet soles on same horizontal baseline. Keep trident head facing RIGHT, finned tail LEFT. Do not alter the design. Produce a clean cutout, not a checkerboard or colored backdrop. True transparent RGBA PNG.

## B 初始提示词

Create ONE 1024x1536 portrait RGBA transparent PNG, Fizz character illustration B.
Image 1 is the approved character identity and pixel-art STYLE. Preserve same face, proportions, ear fins, colors, character design and trident design. Absolutely DO NOT copy any RGB-colored glow/cloud behind that character: empty transparent cutout ONLY.
Image 2 is the authoritative alternate idle pose B, image 3 face, image 4 trident detail. Redraw as crisp detailed pixel art matching image 1, dark stepped outlines, 3–5 flat tones per material, hard highlights, chibi big head about 40% of character height. NOT 3D lighting, gradients, blur or smooth illustration.
Single full-body classic League of Legends Fizz, facing RIGHT in three-quarter FRONT view, both large green eyes visible (far eye narrower), pale cream-yellow throat/belly visible, sky-blue cyan body and pale crown spots, long floppy blue fin-ears with vivid orange-red inner frills, extra rear fin lobes falling behind back, thin curved closed-mouth sly smile no teeth or nose, long thin blue arms, three-fingered hands, small orange elbow spines, navy lower legs and broad flat webbed feet, short blue tail with gold ring.
POSE B: relaxed feet apart with soles on same horizontal baseline. Near hand grips a UPRIGHT vertical trident shaft alongside him on the RIGHT; free arm relaxed. THE WEAPON IS UPSIDE DOWN: THREE-PRONG JADE GREEN AND PALE STEEL HEAD IS AT THE BOTTOM, pointing DOWN, with central spike lowest and touching exactly the SAME baseline as feet. Green-and-gold finned butt is at TOP, above his head. Crimson wrapped shaft and bright silver bands, blue gems. Full weapon length 1.3 times character height. ALL trident prongs must end AT OR ABOVE soles, NO pixel below feet; raise the whole trident to obey this even if reference pose has a lower point.
Composition: entire character and weapon centered in tall canvas, body crown-to-soles about 750px, at least 80px empty transparent margins all around. Both eyes readable, face clearly frontal three-quarter, never back view. NO ground, contact shadow, cast shadow, halo, aura, backdrop, water, platform, text, labels. Actual alpha 0 outside clean silhouette, with absolutely no stray pixels below sole baseline.
