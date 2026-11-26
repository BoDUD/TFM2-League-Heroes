# 终末的女武神 · Q 版像素画

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-23，交付包 `D:/TFM2-Workshop/ragnarok_hd_packs/outputs/ragnarok_q_pixel_0.11.0.zip`）。
用户：「女武神换成了Q版像素风格 帮我整体更换一下 还有BP格子也是 现在这个系列的就用Q版像素风格就行了 但是还是要用PPU保持高清」。

这里放了交付的全部文件（81 个，每个都对过 `checksums.json`，压缩包里的 72 个和这里逐字节相同）：`champions/`（18 个英雄连 6 套
形态的战斗图集，1 倍、hd_、lo_ 三档都是 Q 版）、`ui_sheets/idle/`（Codex 一起重画的待机界面图，打包时 `tools/package_mod.py` 会从
英雄图集重新拼一份，这里只作对照）、`redraw.json`（每一格原来是哪个动作的第几帧）、`verification.json`（Codex 自己的检查）、
`review/`（可播放的预览页和全员总览）。

## 接入（Claude，2026-11-23）

- 交的是 0.11.0 发行版那一版图集（打过包的：相同的帧合成一格、挨着排），每个 `#anim.fanim` 和发行版逐字节相同，只换了像素。仓库里
  的图集没打包、帧的位置不一样，但每个动作的帧数、每帧的大小和时长都一样：`tools/art/ragnarok_q_pixel.py` 按「同一个动作的第几帧」
  把这里的像素拷进 `ragnarok/champions/<英雄>#sheet.png`，帧表（`#anim.fanim`）、PPU（`addons/ragnarok/src/hd.rs`）都不动，高清帧
  还是高清帧。CI 用 `--check` 守着。
- 选人格子、百科这些界面用的图（`ui_sheets/`）是打包时从英雄图集拼的，所以跟着变成 Q 版；选人格子的动图（`bp`）也一样。
- 只修了一处（用户：「应该是这个手的位置歪了」「其他帧数是对的」「只把索尔那个问题修复了就行」）：索尔待机第 0 帧扛锤的手举在
  脸前、挡住半张脸，换成第 1 帧的画（三档都换，按格子中心对齐）。阿波罗待机第 0 帧也和别的帧不是同一版画（窄一圈，胸甲和腰带之间
  一道黑线），用户看了：「算了不用改了 就用黑线吧」，照原样。
- 没换的：特效图、弹道图（比如索尔飞出去的锤子）、技能图标、选人立绘，Codex 说明里写明保留原来的。
- 头像点、百科中心、选人卡位置、界面缩放（`UI_SIZES`）、选人格子的动图片段都照旧（Q 版的人和原来站在同一个格子、同样高）。跟着
  画重出的只有从英雄的画生成的东西：俄洛伊的灵魂图（`tools/art/illaoi_souls.py`）和悠米骑乘的头顶高度（`tools/art/yuumi_ride_lifts.py`）。
- 重新导入一个英雄（`tools/art/import_<英雄>.py`）写的还是 Codex 原来那一版画：之后按顺序跑 `ppu_hd.py`、`hero_reels.py`、
  `ragnarok_run_pace.py`，最后跑 `ragnarok_q_pixel.py`。
