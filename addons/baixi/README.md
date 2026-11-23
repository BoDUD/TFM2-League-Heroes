# baixi (`baixi.dll`)

百戏（`baixi`）独立原生英雄包的 DLL，随 `baixi/` 一起由 `tools/package_mod.py --src baixi` 编译并打包安装。

## 包含内容

- **高清帧引擎（`hd.rs`）**：通过 `hd_engine` 登记五位百戏英雄（点睛、三更、麦芽、火树、拂面，主体 PPU `2.75`，UI 小图集 `ui_sheets/`）及全部特效/弹道图集（FX PPU `3.3`）。
- **实时川剧变脸（`fumian.rs`）**：通过 `game_places` 挂钩按 `baixi_fumian_face_blk` / `baixi_fumian_face_gld` 实时把拂面的贴图标签切换至黑脸（`blk_*`）与金脸（`gld_*`），阵亡时保留当前脸谱。
- **语音与麦芽转盘（`voice.rs`）**：处理 5 位英雄共 25 条 AI 语音（全局 8 秒防刷屏间隔），并在麦芽开局自动挂上 `baixi_maiya_wheel_dragon` 展示头顶糖龙浮标。

## 版本

- `0.1.0`：首发 5 位百戏英雄（点睛、三更、麦芽、火树、拂面）。
