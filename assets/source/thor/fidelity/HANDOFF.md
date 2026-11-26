# 索尔铁手套格挡（2026-11-26 Codex 跟着 Q 版整个重画的新造型重画）

这里的 `atlases/` 是 `tools/art/thor_q_redo.py` 从 Codex 的交付（`assets/source/thor/q_redo/thor_guard`，交接说明
`q_redo/HANDOFF.md`）原样生成的（用户：「用codex原样」），不要手改：

- Codex 的角色图存成了两倍（每 2x2 一块，身体 78-88 格高），frames.json 却照旧按逻辑像素写（格子 216×168、脚点 (98, 148)、
  hd_multiplier 2），照读游戏里大一倍：每 2x2 取一格读回逻辑像素（格子 108×84、脚点 (49, 74)）。导入时再放大两倍就是 Codex
  那张图，像素不变。
- 特效图、挂点照 Codex 的；特效每帧的偏移用 Codex 跟着新手套重标的 `fx_events`（抄进 `fx`，`tools/art/ragnarok_atlas.py` 的
  `redraw_offset` 读那一份）。

动作轨 skill2，8 帧，逻辑格 108×84，脚点 (49, 74)，`hd_multiplier` 2。帧时长和 cues 照 Codex 的。
