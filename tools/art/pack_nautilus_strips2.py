"""Build nautilus_strips2_pack.zip: step 2 again - Codex redraws Nautilus's action strips SIDE-ON (the user, 2026-10-11:
「还有你这个姿势是不是还是正面？ 我现在完成的所有英雄都是侧面吧 除了待机姿势」, 「武器变形了吧？头大的把身体全盖住了？」,
「学隔壁oppi怎么弄的吧」, 「让codex帮忙把」).

    python tools/art/pack_nautilus_strips2.py [--out DIR]

The first pack (tools/art/pack_nautilus_strips.py, MODEL_STRIPS.md) told Codex to keep the idle's body in every frame and
paste the design's helmet: every action came back facing the camera, and the re-posing that followed here (rig_nautilus,
League's frames restyled with the helmet pasted) showed a front-on body, a voted anchor changing shape and a pasted
helmet covering the body. This pack keeps the first pack's files (design, now, pose, guide, cells - the same renders in
%TEMP%/nt_work/pose_n) and rewrites the prompt: every action side-on like the pack's other heroes and oppi's League of
Legends Reborn sprites (refs/style_*.png: every frame drawn by hand on the same body, the weapon the same shape at every
angle, the run a clear stride), the helmet turned with the body (never pasted front-on), the body visible under it, the
anchor one rigid object, legs and arms the design's thickness. Writes MODEL_STRIPS2.md next to MODEL_STRIPS.md.
"""
import argparse
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pack_nautilus_strips as B  # noqa: E402

TMP = B.TMP
REVIEW = os.path.join(TMP, "review")
OPPI = os.path.join(TMP, "oppi")
PACK = os.path.join(TMP, "strips2", "nautilus_strips2_pack")
ZIP = os.path.join(TMP, "strips2", "nautilus_strips2_pack.zip")
DOC = os.path.join(B.SRC, "MODEL_STRIPS2.md")
CODEX1 = os.path.join(B.SRC, "codex_strips", "nautilus-strips", "previews", "contact_sheet.png")
# reference pictures (local renders: oppi's sprites from the Workshop, the pack's heroes, League's frames)
REFS = {
    "style_oppi_galio.png": os.path.join(OPPI, "galio_z5.png"),
    "style_oppi_sion.png": os.path.join(OPPI, "sion_z.png"),
    "style_oppi_alistar.png": os.path.join(OPPI, "ali_z.png"),
    "style_oppi_vi.png": os.path.join(OPPI, "vi_z.png"),
    "style_pack_heroes.png": os.path.join(REVIEW, "pack_views.png"),
    "lol_turned_body.png": os.path.join(REVIEW, "lol_mix.png"),
    "lol_run_legs.png": os.path.join(REVIEW, "lol_run_legs8.png"),
    "rejected_first_delivery.png": CODEX1,
    "rejected_front_on.png": os.path.join(REVIEW, "z10.png"),
    "rejected_pasted_helmet.png": os.path.join(REVIEW, "optR_run.png"),
}

LEGS_TXT = ("SIDE-ON legs like the pack's other heroes and oppi's sprites: under the turned body, one leg in front of the "
            "other (not the idle's wide front stance), each leg the design's own leg - the dark grey-black suit, the bronze "
            "knee guard on the front of the knee, the huge diving boot with its thick bronze sole pointing to the image "
            "right - the SAME width and length in every frame (never squashed, stretched, sheared, slid sideways or broken "
            "into scraps); a bent knee is drawn as a bent leg; the far leg a shade darker where the near one crosses it; "
            "standing or braced frames plant both boots flat on the feet line, a lunge steps the front boot forward")
ORB_TXT = ("the helmet keeps the design's size and details (the rusty-red pipe hood, the three vent holes, the black viewing "
           "slit with the two red-orange eyes, the square jaw guard) but TURNS WITH THE BODY: seen from the front-right, the "
           "viewing slit moved toward the helmet's right side, the far eye narrower, the hood and the vent holes following; "
           "the SAME turned helmet in every frame of an action, never pasted front-on and never covering the whole body - "
           "under and beside it the bronze chest and shoulder plates with their sea-green seams, the belt, the arms and the "
           "legs stay visible as on League's model (pose/), the near shoulder plate in front, the far one partly behind the "
           "helmet")
ARMS_TXT = ("the arms are the design's arms - thick dark grey-black suit arms with bronze bracers and big grey gloves - never "
            "longer than the design's own arm (no long stretched arms), never thinner, each growing from its shoulder plate; "
            "the ANCHOR is ONE rigid object with exactly the design's shape and size (the grey stone-iron shank with its red "
            "band and brown rope, the ring, the wide crown and the two hooked flukes): only moved and turned whole, drawn "
            "clean at every angle like oppi draws Sion's axe (refs/style_oppi_sion.png) - never bent, melted, shortened, "
            "thinned or changing shape from frame to frame; the iron chain runs from his near hand to the anchor's ring; the "
            "hand holding it is never hidden behind the body")


def patch(text, old, new):
    assert old in text, old[:80]
    return text.replace(old, new)


def doc_text():
    t = B.DOC_TEXT
    t = patch(t, "# 诺提勒斯：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）",
              "# 诺提勒斯：动作帧重画——侧身版（第 2 步第二轮，给 Codex 的提示词）\n\n"
              "> **这一轮为什么重画**：上一轮的提示词要求「放技能时的身体就是待机的身体、头盔贴上去」，结果每个动作都是正面站着"
              "（`refs/rejected_first_delivery.png`、`refs/rejected_front_on.png`）；把造型图的头盔贴到英雄联盟的身体上又把身体全盖住了、"
              "锚每帧变形（`refs/rejected_pasted_helmet.png`）。用户：「我现在完成的所有英雄都是侧面吧 除了待机姿势」"
              "「武器变形了吧？头大的把身体全盖住了？」「学隔壁oppi怎么弄的吧」。\n"
              "> **这一轮的标准：像 oppi 的《League of Legends Reborn》那样一帧一帧手绘**（`refs/style_oppi_*.png`：Galio 待机正面、"
              "跑步和出招转成侧身；Sion 的斧子每个角度都是同一把斧子；Alistar、Vi 的跑步是清楚的交叉步）。"
              "**除待机外每个动作都是侧身朝右**（和本包其他英雄一样：`refs/style_pack_heroes.png`），身体转向右边——"
              "英雄联盟的动作本来就是这样转的（`refs/lol_turned_body.png`、`pose/`）。")
    t = patch(t, "> - **放技能时的身体就是待机的身体**（同一套像素）：头盔、胸甲肩甲、腿的形状和大小不能变，只动手臂和锚；整个人可以前倾后仰、前冲、下蹲。",
              "> - **动作帧是侧身**：身体朝右转（头盔的观察窗转到头盔右侧、远侧那只眼睛变窄，近侧肩甲在前、远侧肩甲一半在头盔后面），"
              "两腿一前一后侧着站或跑（不是待机那种正面八字站）；头盔大小、颜色、细节和造型图一样，只是转过去看；"
              "同一个动作里每帧的头盔、身体、腿、手臂、锚的大小和形状都一致（不能忽大忽小、不能变形），整个人可以前倾后仰、前冲、下蹲、跳起。")
    t = patch(t, "② 头盔是贴上去的（见下），**头盔每帧不变形、不旋转、始终是造型图的头盔和两只红眼**，**不画背影**；",
              "② **头盔跟着身体转向右边，不贴正面头盔**，也不能把身体全盖住（胸甲、肩甲、腰带、手臂、腿都要看得见）；**不画背影**；")
    t = patch(t, "4. **贴头盔**：把造型图的头盔", "4. **不要贴头盔**（上一轮的做法，已经作废）。原来是：把造型图的头盔")
    t = patch(t, "Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right,",
              "Every frame must be the FIRST image's character in a new pose, drawn by hand like oppi's sprites, but SIDE-ON: "
              "the body turned to face the image right (the helmet's viewing slit on the helmet's right side, the near "
              "shoulder plate in front, the far one partly behind the helmet, the legs one in front of the other) - only the "
              "idle faces the camera. The same")
    t = patch(t, "but keep the FIRST image's proportions and, in every standing frame, the FIRST image's own body and legs;",
              "the body turned the way the THIRD image turns it, with the FIRST image's proportions, colours and details;")
    t = patch(t, "The body is the idle body: in every frame the helmet, the chest and shoulder plates and the legs keep the FIRST "
                 "image's shapes and sizes square for square; only the arms and the anchor move, and the whole figure may "
                 "lean, lunge or crouch.",
              "Consistency: within an animation the helmet, the body, the legs, the arms and the anchor keep the same size and "
              "shape in every frame (the turned helmet is the same turned helmet in every frame); the whole figure may lean, "
              "lunge, crouch or hop.")
    t = patch(t, "The helmet (the pipe hood, the dome with three vent holes, the black viewing slit with the two red-orange eyes, "
                 "the jaw guard) is COPIED from the FIRST image in every frame, square for square, and only moved; never "
                 "redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own helmet before pasting "
                 "it, so no extra outline is left beside it.",
              "The helmet keeps the FIRST image's size, colours and details, turned to the right with the body; do not paste "
              "the FIRST image's front-on helmet and do not let the helmet cover the whole body.")
    t = patch(t, "3/4 view like the FIRST image; every cast goes to the RIGHT of the image; never his back, never upside down.",
              "Side-on facing the image right (only the idle faces the camera); every cast goes to the RIGHT of the image; "
              "never his back, never upside down.")
    t = patch(t, "the helmet identical to the FIRST image in every frame,", "every frame side-on with the turned helmet,")
    t = patch(t, "the standing frames on the FIRST image's own body and legs,", "the body visible under the helmet, the legs "
              "the same thickness in every frame,")
    t = patch(t, "2. 保留每一帧的动作：手臂、锚和身体的方向和姿势照图1（出招都朝图的右边，不画背影、不趴在地上）；头盔、身体和腿用图2自己的。",
              "2. 保留每一帧的动作：身体侧过来朝右（只有待机是正面），手臂、锚和身体的方向和姿势照图1（出招都朝图的右边，不画背影、不趴在地上）；"
              "头盔、身体和腿的颜色、细节、大小用图2的，头盔跟着身体转过去，不能把身体全盖住。")
    t = patch(t, "- [ ] 待机姿态时和造型图一样大；头盔就是造型图的头盔（逐格一样，只平移），头盔旁边没有多余的描边；",
              "- [ ] 除待机外每帧都是侧身朝右；头盔和造型图一样大、细节一样，跟着身体转向右边；身体（胸甲、肩甲、腰带、手臂、腿）看得见，"
              "没有被头盔全盖住；同一个动作里各部件大小形状不变；")
    t = patch(t, "- [ ] 每帧身体（头盔、胸甲肩甲、腿）和造型图一样；两只手臂都在、和造型图一样粗、从肩甲外侧长出来；",
              "- [ ] 两只手臂都在、和造型图一样粗、不比造型图的手臂长，从肩甲长出来；")
    t = patch(t, "- [ ] 跑步锚一直背在背上，两腿真正交叉（每半个周期两只靴子交换前后、抬起的靴子从另一只旁边越过），腿的颜色和待机一样，没有缺格子；",
              "- [ ] 跑步锚一直背在背上，侧身交叉步（像 `refs/style_oppi_alistar.png`、`refs/style_oppi_vi.png`：每半个周期两只靴子交换前后、"
              "抬起的腿屈膝），腿每帧一样粗、没有碎块、没有缺格子；")
    t += """
## 这一轮新增的参考图（`refs/`）

| 文件 | 内容 |
|---|---|
| `style_oppi_galio.png`、`style_oppi_sion.png`、`style_oppi_alistar.png`、`style_oppi_vi.png` | oppi 的手绘精灵（待机、跑步、普攻）：**要学的标准**——待机正面，跑步和出招侧身；每帧都是同一个人、同样大小；武器每个角度都是同一把武器 |
| `style_pack_heroes.png` | 本包已经做好的英雄（每行：待机、跑步 4 帧、普攻 1 帧）：动作都是侧身 |
| `lol_turned_body.png` | 英雄联盟里诺提勒斯的待机（正面）和跑步、普攻、W+E、R（身体都转向右边） |
| `lol_run_legs.png` | 英雄联盟跑步 8 帧的腿（交叉步、屈膝抬腿） |
| `rejected_first_delivery.png` | 上一轮交付（全是正面站着，锚变形）：**不要这样** |
| `rejected_front_on.png` | 用定稿零件摆出来的跑步（正面八字腿）：**不要这样** |
| `rejected_pasted_helmet.png` | 把正面头盔贴到英雄联盟身体上（身体被盖住、锚每帧变形）：**不要这样** |
"""
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="folder for the zip (default: next to the pack)")
    a = ap.parse_args()
    zpath = os.path.join(a.out, os.path.basename(ZIP)) if a.out else ZIP
    B.PACK = PACK
    B.DOC = os.path.join(TMP, "strips2", "unused_MODEL_STRIPS.md")
    B.LEGS_TXT, B.ORB_TXT, B.ARMS_TXT = LEGS_TXT, ORB_TXT, ARMS_TXT
    B.DOC_TEXT = doc_text()
    os.makedirs(os.path.dirname(PACK), exist_ok=True)
    sys.argv = [sys.argv[0], "--no-zip"]
    B.main()
    os.remove(os.path.join(PACK, "MODEL_STRIPS.md"))
    with open(B.DOC, encoding="utf-8") as f:
        doc = f.read()
    for path in (os.path.join(PACK, "MODEL_STRIPS2.md"), DOC):
        with open(B.lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    for name, src in REFS.items():
        shutil.copyfile(B.lp(src), os.path.join(PACK, "refs", name))
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(PACK):
            for fn in sorted(files):
                p = os.path.join(root, fn)
                z.write(p, os.path.join("nautilus_strips2_pack", os.path.relpath(p, PACK)).replace(os.sep, "/"))
    print(zpath, os.path.getsize(zpath) // 1024, "KB")


if __name__ == "__main__":
    main()
