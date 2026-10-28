#!/usr/bin/env python3
"""Find league.dll's places in a new game build and print the `Build` for addons/league_main/src/build.rs.

    python -I tools/re/find_build.py [--exe <TeamfightManager2.exe>] [--out build.rs.txt]

league.dll (PPU dense frames) and the whole-body add-ons (league_kayn_form, league_viego_soul, league_nidalee
view.rs) patch fixed places of the game EXE. A game update moves them (0.6.3 -> 0.6.4 moved all of them; the
structures they read stayed). This tool starts from the build build.rs lists - its fingerprints and the layout
of its call sites - and finds every place again in the new EXE, the way 0.6.4 was found by hand (2026-10-14):

1. the anim / sheet lookups: the 128-byte head of the old anim lookup with every call / rip-relative
   displacement wildcarded (33 monomorphized HashMap<String, _>::get share it), each calling the hash (the old
   hash's head, wildcarded) at the old offset;
2. which candidate is the anim lookup: the one called by a function laid out like the old battlefield frame
   lookup (the call, then the two size asks at the old distances, the same bytes); the sheet lookup is the other
   candidate that function calls;
3. the body draw: the caller of that frame lookup holding the four size asks of the old body draw at the old
   spacing; the entity render: the caller of the body draw that reads `movss xmm, [reg+0x1b4]` right after;
   grow_one of the draw commands: called by the body draw, `mov qword [rsp+0x28], 0xd0` inside;
4. the display handler: the old handler's 48-byte head; its slot: the .rdata qword pointing at it;
5. the UI drawers (encyclopedia, pick slot, BP grid, pick moment, scoreboard portraits): every caller of the anim
   lookup scored by how close its four following size asks sit to the old drawer's spacing - this step is a
   heuristic, the table it prints (best and second best) is for a human to confirm;
6. the UI sheets' places (src/ui.rs): each drawer's own sheet lookup, the draw command made from a name, the image
   node's setter; 7. the view node draw (src/view.rs effect_detour) among the body draw's callees;
8. the hooks' assumptions asserted on the new EXE (the 12-byte prologue the hooks replace, the slot pointing at
   the handler, the 0x1b4 scale read, 0xd0-byte commands).

0.6.5 -> 0.7.0 (2026-10-28) was the first update built by another compiler: no lookup head in common (step 1 then takes
the lookups by their shape), the body draw's size asks through other registers (step 3 by their spacing alone), the
scale read through r12 (a SIB form), the scale / restore command tags moved by one (read from the entity render), the
draw command made from a name pushing one register more (its prologue is decoded, not compared).

Then a match in game confirms it: league.log `game build: <name>`, the "lookup anim from rva" / "texture width
asked from rva" lines of every screen. The structures (display world table, entity value fields, draw command
layout) are NOT re-derived here: check them as build.rs's header describes when the code around them changes.

Since 2026-10-20 league.dll and the add-ons first try the same steps at run time (addons/game_places, patterns from
tools/re/make_sigs.py); this tool is for when they fail - after updating build.rs, run make_sigs.py again.
Needs `pip install capstone pefile`. Reads the EXE only; writes nothing unless --out.
"""
import argparse
import bisect
import hashlib
import os
import re
import struct
import sys

try:
    import capstone
    import pefile
except ImportError:
    sys.exit("needs: pip install capstone pefile")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILD_RS = os.path.join(ROOT, "addons", "league_main", "src", "build.rs")
GAME = r"D:/steam/steamapps/common/Teamfight Manager2/TeamfightManager2.exe"
PROLOGUE = bytes([0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x53])
UI_NAMES = ["encyclopedia / face icons", "pick slot", "BP grid", "pick moment", "scoreboard portraits"]
X86 = capstone.x86


# ---- the build build.rs lists ----------------------------------------------------------------------------------

def old_build(path=BUILD_RS):
    src = open(path, encoding="utf-8").read()
    body = src[src.index("pub static BUILDS"):]
    body = body[:body.index("}];")]

    def num(field):
        return int(re.search(rf"\b{field}: (0x[0-9a-f]+),", body).group(1), 16)

    def nums(field):
        m = re.search(rf"\b{field}: &\[([^\]]*)\]", body)
        return [int(x, 16) for x in re.findall(r"0x[0-9a-f]+", m.group(1))]

    sigs = []
    for m in re.finditer(r"\((0x[0-9a-f]+),\s*&\[([^\]]*)\]\)", body[body.index("sigs: &["):]):
        sigs.append((int(m.group(1), 16), bytes(int(x, 16) for x in re.findall(r"0x([0-9a-f]{2})", m.group(2)))))
    b = {k: num(k) for k in ("anim", "sheet", "hash", "display_fn", "display_slot", "body_draw", "cmd_grow",
                               "cmd_by_name", "node_image", "effect_draw")}
    b.update({k: nums(k) for k in ("battle_anim_ret", "battle_size_ret", "ui_anim_ret", "ui_size_ret")})
    b["name"] = re.search(r'name: "([^"]*)"', body).group(1)
    b["sigs"] = dict(sigs)
    return b


# ---- the EXE -----------------------------------------------------------------------------------------------------

class Exe:
    def __init__(self, path):
        self.data = open(path, "rb").read()
        pe = pefile.PE(data=self.data, fast_load=True)
        self.base = pe.OPTIONAL_HEADER.ImageBase
        self.secs = {s.Name.rstrip(b"\0").decode(): (s.VirtualAddress, s.Misc_VirtualSize, s.PointerToRawData,
                                                      s.SizeOfRawData) for s in pe.sections}
        va, vs, ro, rs = self.secs[".text"]
        self.text_rva, self.text = va, self.data[ro:ro + min(vs, rs)]
        self.md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
        self.md.detail = True
        va, vs, ro, rs = self.secs[".pdata"]
        raw = self.data[ro:ro + vs]
        self.funcs = sorted((b, e) for b, e, _ in struct.iter_unpack("<III", raw[:len(raw) // 12 * 12]) if b)
        self._calls = None

    def read(self, rva, n):
        for va, vs, ro, rs in self.secs.values():
            if va <= rva < va + max(vs, rs):
                return self.data[ro + rva - va:ro + rva - va + n]
        return None

    def ins(self, rva):
        return next(self.md.disasm(self.read(rva, 16), rva, 1))

    def func_of(self, rva):
        i = bisect.bisect_right(self.funcs, (rva, 1 << 40)) - 1
        return self.funcs[i] if i >= 0 and self.funcs[i][0] <= rva < self.funcs[i][1] else None

    def find(self, pattern):
        return [self.text_rva + m.start() for m in re.finditer(pattern, self.text, re.DOTALL)]

    def calls_to(self, target):
        if self._calls is None:
            self._calls = {}
            t = self.text
            for m in re.finditer(b"\xe8", t):
                i = m.start()
                if i + 5 <= len(t):
                    tgt = self.text_rva + i + 5 + struct.unpack_from("<i", t, i + 1)[0]
                    self._calls.setdefault(tgt, []).append(self.text_rva + i)
        return self._calls.get(target, [])

    def call_target(self, rva):
        b = self.read(rva, 5)
        return rva + 5 + struct.unpack_from("<i", b, 1)[0] if b and b[0] == 0xE8 else None


def wildcard(code, rva):
    """A regex for `code` (read at `rva` in some build) with calls / jumps out of it and rip displacements wildcarded."""
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    md.detail = True
    mask = [False] * len(code)
    for i in md.disasm(code, rva):
        o = i.address - rva
        for op in i.operands:
            if op.type == X86.X86_OP_MEM and op.mem.base == X86.X86_REG_RIP:
                for k in range(i.disp_offset, i.disp_offset + 4):  # rip-relative is disp32 (capstone's size lies)
                    mask[o + k] = True
        if (i.group(capstone.CS_GRP_JUMP) or i.group(capstone.CS_GRP_CALL)) and i.operands \
                and i.operands[0].type == X86.X86_OP_IMM and not rva <= i.operands[0].imm < rva + len(code):
            for k in range(i.imm_offset, i.imm_offset + i.imm_size):
                mask[o + k] = True
    return b"".join(b"." if m else re.escape(bytes([c])) for c, m in zip(code, mask))


def one(what, cands):
    if len(cands) != 1:
        sys.exit(f"{what}: {len(cands)} candidates {[hex(c) if isinstance(c, int) else c for c in cands[:12]]}")
    return cands[0]


def call_targets(e, f, n):
    """The `call rel32` targets in the first `n` bytes of `f`, in order (a byte scan: only for short heads)."""
    out, a = [], f
    while a < f + n:
        t = e.call_target(a)
        if t is not None and e.func_of(t) and e.func_of(t)[0] == t:
            out.append(t)
            a += 5
        else:
            a += 1
    return out


def shaped_lookups(e, hashes):
    """The HashMap<String, _>::get heads by their shape alone (0.7.0, a newer compiler: the listed head's bytes are
    gone): the 12-byte prologue and `sub rsp, imm32`, a call building the key, then a call of one of `hashes`, both in
    the first 0x90 bytes."""
    out = []
    for f, _ in e.funcs:
        if e.read(f, 15) != PROLOGUE + b"\x48\x81\xec":
            continue
        calls = call_targets(e, f, 0x90)
        if len(calls) >= 2 and calls[1] in hashes:
            out.append(f)
    return out


def is_call_reg(e, rva):
    """`call r64` (ff d0..d7 but d4, or 41 ff d0..d7) at `rva`: a size ask through a register holding a vtable entry."""
    b = e.read(rva, 3) or b""
    return (len(b) >= 2 and b[0] == 0xFF and 0xD0 <= b[1] <= 0xD7 and b[1] != 0xD4) or \
        (len(b) == 3 and b[0] == 0x41 and b[1] == 0xFF and 0xD0 <= b[2] <= 0xD7)


def prologue_len(code):
    """The length of a push / `sub rsp` prologue at the start of `code` once it covers the 12 bytes a hook overwrites
    (push r64: 50..57 or 41 50..57; sub rsp, imm8 / imm32: 48 83 ec ib / 48 81 ec id), else None - src/ui.rs runs those
    whole instructions from its trampoline."""
    i = 0
    while i < 12:
        if 0x50 <= code[i] <= 0x57:
            i += 1
        elif code[i] == 0x41 and 0x50 <= code[i + 1] <= 0x57:
            i += 2
        elif code[i:i + 3] == b"\x48\x83\xec":
            i += 4
        elif code[i:i + 3] == b"\x48\x81\xec":
            i += 7
        else:
            return None
    return i


# ---- the search --------------------------------------------------------------------------------------------------

def search(e, b):
    sig = b["sigs"]
    found, notes = {}, []
    # 1. hash and lookups: the listed build's lookup head first, else the lookups' shape (0.6.5 -> 0.7.0)
    hashes = set(e.find(wildcard(sig[b["hash"]], b["hash"])))
    anim_sig = sig[b["anim"]]
    hash_call = next(i.address - b["anim"] for i in e.md.disasm(anim_sig, b["anim"])
                     if i.mnemonic == "call" and i.operands[0].imm == b["hash"])
    lookups = [f for f in e.find(wildcard(anim_sig, b["anim"])) if e.call_target(f + hash_call) in hashes]
    if lookups:
        found["hash"] = one("hash called by the lookups", sorted({e.call_target(f + hash_call) for f in lookups}))
    else:
        lookups = shaped_lookups(e, hashes)
        notes.append(f"the listed build's lookup head is not in this EXE: {len(lookups)} lookups found by their shape")
    # 2. the battlefield frame lookup -> anim and sheet
    old_call = b["battle_anim_ret"][0] - 5
    asks = [(r, sig[r - n]) for r in b["battle_size_ret"][:2] for n in (2, 3) if r - n in sig]
    hits = []
    for f in lookups:
        for c in e.calls_to(f):
            if all(e.read(c + (r - len(x)) - old_call, len(x)) == x for r, x in asks):
                hits.append((f, c))
    anim, frame_call = one("the battlefield frame lookup's call", hits)
    found["anim"] = anim
    if "hash" not in found:
        found["hash"] = call_targets(e, anim, 0x90)[1]
        lookups = [f for f in lookups if call_targets(e, f, 0x90)[1] == found["hash"]]
    notes.append(f"{len(lookups)} HashMap<String, _>::get candidates, all calling the hash {found['hash']:#x}")
    frame_fn = e.func_of(frame_call)
    sheet_calls = []
    for i in e.md.disasm(e.read(frame_fn[0], frame_fn[1] - frame_fn[0]), frame_fn[0]):
        if i.mnemonic == "call" and i.operands[0].type == X86.X86_OP_IMM and i.operands[0].imm in lookups \
                and i.operands[0].imm != anim:
            sheet_calls.append(i.operands[0].imm)
    found["sheet"] = one("the sheet lookup in the frame lookup", sorted(set(sheet_calls)))
    found["battle_anim_ret"] = [frame_call + 5]
    found["battle_frame"] = frame_fn[0]
    battle_asks = [frame_call + (r - len(x)) - old_call for r, x in asks]
    # 3. the body draw, the entity render, grow_one
    body_asks_old = [(r, next(sig[r - n] for n in (2, 3) if r - n in sig)) for r in b["battle_size_ret"][2:]]
    first = body_asks_old[0][0] - len(body_asks_old[0][1])
    bodies = []
    offs = [(r - len(x)) - first for r, x in body_asks_old]
    for c in e.calls_to(frame_fn[0]):
        f = e.func_of(c)
        code = e.read(f[0], f[1] - f[0])
        for m in re.finditer(re.escape(body_asks_old[0][1]), code):
            p = f[0] + m.start()
            if all(e.read(p + (r - len(x)) - first, len(x)) == x for r, x in body_asks_old):
                bodies.append((f[0], p))
    if not bodies:
        # 0.7.0: the same spacing, other registers (call r13 -> call r15)
        for c in e.calls_to(frame_fn[0]):
            f = e.func_of(c)
            bodies += [(f[0], p) for p in range(f[0], f[1] - offs[-1]) if all(is_call_reg(e, p + o) for o in offs)]
        notes.append("the body draw's size asks matched by their spacing alone (their registers changed)")
    body, body_ask0 = one("the body draw (four size asks at the old spacing)", sorted(set(bodies)))
    found["body_draw"] = body
    battle_asks += [body_ask0 + o for o in offs]
    # the entity render: the caller of the body draw that reads its scale, [reg+0x1b4] (0.7.0: [r12+0x1b4], a SIB form),
    # soon after - not a local of its frame
    renders = []
    for c in e.calls_to(body):
        for i in e.md.disasm(e.read(c, 0x200), c):
            if i.mnemonic == "movss" and i.operands[1].type == X86.X86_OP_MEM and i.operands[1].mem.disp == 0x1B4 \
                    and i.operands[1].mem.base not in (X86.X86_REG_RSP, X86.X86_REG_RBP, X86.X86_REG_RIP):
                renders.append((c, i.address))
                break
    found["render_call"], found["render_scale"] = one("the entity render (movss [reg+0x1b4] after the body draw)",
                                                       renders)
    # the scale and restore commands it wraps the body draw's commands in: their tags are the first two niche values it
    # writes after that read (0.6.5: 0x8000000000000011 / ...12; 0.7.0 ...12 / ...13 - a variant was added before them)
    tags = []
    for i in e.md.disasm(e.read(found["render_scale"], 0x200), found["render_scale"]):
        if i.mnemonic == "movabs" and i.operands[1].type == X86.X86_OP_IMM and \
                0x8000000000000000 <= i.operands[1].imm & 0xFFFFFFFFFFFFFFFF <= 0x80000000000000FF:
            tags.append((i.address, i.operands[1].imm & 0xFFFFFFFFFFFFFFFF))
    if len(tags) < 2 or tags[1][1] != tags[0][1] + 1:
        sys.exit(f"the entity render's scale / restore command tags: not found after {found['render_scale']:#x} ({tags})")
    found["cmd_tags"] = tags[:2]
    grows = set()
    for i in e.md.disasm(e.read(body, e.func_of(body)[1] - body), body):
        if i.mnemonic == "call" and i.operands[0].type == X86.X86_OP_IMM:
            g = i.operands[0].imm
            head = e.read(g, 0x40) or b""
            if b"\x48\xc7\x44\x24\x28\xd0\x00\x00\x00" in head:
                grows.add(g)
    found["cmd_grow"] = one("grow_one of the 0xd0-byte draw commands", sorted(grows))
    # 4. the display handler and its slot
    found["display_fn"] = one("the display handler", e.find(wildcard(sig[b["display_fn"]], b["display_fn"])))
    va, vs, ro, rs = e.secs[".rdata"]
    rdata = e.data[ro:ro + vs]
    want = struct.pack("<Q", e.base + found["display_fn"])
    found["display_slot"] = one("the display slot", [va + m.start() for m in re.finditer(re.escape(want), rdata)
                                                     if m.start() % 8 == 0])
    # 5. the UI drawers by the spacing of their size asks (return addresses relative to the anim call's). Spacing alone
    # can pick a look-alike (0.6.4: a champion effect drawer, 0x1fc5510, has the old pick slot's exact spacing), so a
    # drawer not clearly ahead of the rest is also asked to sit where the old one sat next to a drawer already found
    # (0.6.4's pick slot: 0x3bd7 before the encyclopedia's call, 0.6.3's 0x3be5 - the same code unit).
    callers = e.calls_to(anim)
    sites = []
    for k, ret in enumerate(b["ui_anim_ret"]):
        old = [r - ret for r in b["ui_size_ret"][4 * k:4 * k + 4]]
        scored = []
        for c in callers:
            new_asks = [i for i in e.md.disasm(e.read(c, 0x800), c)
                        if i.mnemonic == "call" and i.operands[0].type != X86.X86_OP_IMM]
            best = None
            for s in range(len(new_asks) - 3):
                w = [i.address + i.size - (c + 5) for i in new_asks[s:s + 4]]
                d = sum(abs((w[j] - w[0]) - (old[j] - old[0])) for j in range(4)) + abs(w[0] - old[0]) // 16
                if best is None or d < best[0]:
                    best = (d, [i.address for i in new_asks[s:s + 4]])
            if best:
                scored.append((best[0], c, best[1]))
        scored.sort()
        sites.append((ret - 5, scored))
    chosen = {}
    for k, (_, scored) in enumerate(sites):
        if scored[0][0] <= 1 and (len(scored) == 1 or scored[1][0] >= scored[0][0] + 5):
            chosen[k] = (scored[0], "clear")
    for k, (old_call, scored) in enumerate(sites):
        if k in chosen:
            continue
        taken = {v[0][1] for v in chosen.values()}
        best = None
        for d, c, w in scored:
            if c in taken:
                continue
            mismatch = min((abs((c - v[0][1]) - (old_call - sites[j][0])) for j, v in chosen.items()), default=1 << 40)
            total = d + (0 if mismatch < 0x100 else 5)
            if best is None or total < best[0]:
                best = (total, (d, c, w), f"next to a found drawer (off by {mismatch:#x})" if mismatch < 0x100
                        else "spacing only")
        chosen[k] = (best[1], best[2])
    ui, ui_rows = [], []
    for k in range(len(sites)):
        (d, c, w), how = chosen[k]
        ui.append((c, w))
        others = [s for s in sites[k][1] if s[1] != c][:1]
        second = f"; next best spacing {others[0][0]} at {others[0][1]:#x}" if others else ""
        name = UI_NAMES[k] if k < len(UI_NAMES) else str(k)
        ui_rows.append(f"  {name:26s} call {c:#x} in {e.func_of(c)[0]:#x}: spacing {d}, {how}{second}")
    found["ui"] = ui
    found["battle_asks"] = battle_asks
    # 6. src/ui.rs (the UI sheets): each drawer's own call of the sheet lookup between its anim call and its first size
    # ask, and the two functions they hand the sheet's name to - the draw command made from a name (called by the BP
    # grid and the scoreboard portraits after their sheet lookup; `mov rdi, r8; test r8, r8` in its head: 0.6.5 and
    # 0.7.0) and the image node's setter (called by the encyclopedia and the pick slot; the listed build's head)
    sheet_calls, after = [], []
    for c, w in ui:
        s = next((a for a in range(c + 5, w[0]) if e.call_target(a) == found["sheet"]), None)
        if s is None:
            sys.exit(f"UI drawer at {c:#x}: no call of the sheet lookup before its size asks")
        sheet_calls.append(s)
        f = e.func_of(c)
        after.append({i.operands[0].imm for i in e.md.disasm(e.read(s + 5, f[1] - s - 5), s + 5)
                      if i.mnemonic == "call" and i.operands[0].type == X86.X86_OP_IMM})
    found["ui_sheet_calls"] = sheet_calls
    mark = b"\x4c\x89\xc7\x4d\x85\xc0"
    found["cmd_by_name"] = one("the draw command made from a sheet's name",
                               sorted(t for t in after[2] & after[4] if mark in (e.read(t, 0x60) or b"")))
    node_heads = set(e.find(wildcard(sig[b["node_image"]], b["node_image"])))
    found["node_image"] = one("the image node's setter", sorted(after[0] & after[1] & node_heads))
    for k in ("cmd_by_name", "node_image"):
        if prologue_len(e.read(found[k], 24)) is None:
            sys.exit(f"{k} {found[k]:#x}: not a push / sub rsp prologue src/ui.rs can run from its trampoline")
    # 7. the view node draw (src/view.rs effect_detour): a function with the listed head (prologue, sub rsp, lea rbp -
    # 38 in 0.7.0) that the body draw calls (it and the world's effects do; 0.7.0 0x245f150), else not known (0: dense
    # effects drawn PPU times big)
    eff = []
    if b.get("effect_draw") in sig:
        called = {i.operands[0].imm for i in e.md.disasm(e.read(body, e.func_of(body)[1] - body), body)
                  if i.mnemonic == "call" and i.operands[0].type == X86.X86_OP_IMM}
        eff = [f for f in e.find(wildcard(sig[b["effect_draw"]], b["effect_draw"])) if f in called]
    found["effect_draw"] = eff[0] if len(eff) == 1 else 0
    if not found["effect_draw"]:
        notes.append(f"the view node draw: {len(eff)} candidates called by the body draw - effect_draw 0 (not hooked)")
    return found, notes, ui_rows


def check(e, f):
    for k in ("anim", "sheet", "body_draw"):
        assert e.read(f[k], 12) == PROLOGUE and e.read(f[k] + 12, 3) == b"\x48\x81\xec", f"{k}: not the 12-byte prologue"
    assert struct.unpack("<Q", e.read(f["display_slot"], 8))[0] == e.base + f["display_fn"]
    assert e.call_target(f["render_call"]) == f["body_draw"]
    assert e.read(f["cmd_grow"] + 0x21, 9) == bytes.fromhex("48c7442428d0000000")


def rust(e, f):
    def hexes(bs, per=16, ind=8):
        return "\n".join(" " * ind + ", ".join(f"0x{c:02x}" for c in bs[k:k + per]) + "," for k in range(0, len(bs), per))

    def short(bs):
        return ", ".join(f"0x{c:02x}" for c in bs)

    def at(rva):
        return f"({rva:#x}, &[{short(e.read(rva, e.ins(rva).size))}])"

    sha = hashlib.sha256(e.data).hexdigest()
    ui_ret = [c + 5 for c, _ in f["ui"]]
    ui_size = [a + e.ins(a).size for _, w in f["ui"] for a in w]
    asks = f["battle_asks"]

    def rets(v, ind):
        return (",\n" + " " * ind).join(", ".join(f"{r:#x}" for r in v[k:k + 8]) for k in range(0, len(v), 8))

    sized = [1, 2, 3]  # the pick slot, the BP grid, the pick moment draw the whole body
    out = ["pub static BUILDS: &[Build] = &[Build {",
           f'    name: "<version> (Steam, EXE sha256 {sha[:8]}...)",',
           f"    anim: {f['anim']:#x},", f"    sheet: {f['sheet']:#x},", f"    hash: {f['hash']:#x},",
           f"    display_fn: {f['display_fn']:#x},", f"    display_slot: {f['display_slot']:#x},",
           f"    battle_anim_ret: &[{f['battle_anim_ret'][0]:#x}],",
           "    battle_size_ret: &[" + ", ".join(f"{a + e.ins(a).size:#x}" for a in asks) + "],",
           "    ui_anim_ret: &[" + ", ".join(f"{r:#x}" for r in ui_ret) + "],",
           "    ui_size_ret: &[" + rets(ui_size, 19) + "],",
           "    ui_sized_anim_ret: &[" + ", ".join(f"{ui_ret[k]:#x}" for k in sized) + "],",
           "    ui_sized_size_ret: &[" + rets([r for k in sized for r in ui_size[4 * k:4 * k + 4]], 25) + "],",
           "    ui_sheet_ret: &[" + ", ".join(f"{s + 5:#x}" for s in f["ui_sheet_calls"]) + "],",
           f"    cmd_by_name: {f['cmd_by_name']:#x},", f"    node_image: {f['node_image']:#x},",
           f"    body_draw: {f['body_draw']:#x},", f"    cmd_grow: {f['cmd_grow']:#x},",
           f"    effect_draw: {f['effect_draw']:#x},",
           f"    cmd_scale: {f['cmd_tags'][0][1]:#x},", f"    cmd_restore: {f['cmd_tags'][1][1]:#x},", "    sigs: &[",
           "    // the anim-table lookup", f"    ({f['anim']:#x}, &[\n{hexes(e.read(f['anim'], 128))}\n    ]),",
           "    // the sheet (texture) lookup", f"    ({f['sheet']:#x}, &[\n{hexes(e.read(f['sheet'], 128))}\n    ]),",
           "    // the battlefield body draw", f"    ({f['body_draw']:#x}, &[\n{hexes(e.read(f['body_draw'], 24))}\n    ]),",
           "    // the draw commands' grow_one (new capacity max(4, 2 x cap), 0xd0 bytes, align 8)",
           f"    ({f['cmd_grow']:#x}, &[\n{hexes(e.read(f['cmd_grow'], 48))}\n    ]),"]
    if f["effect_draw"]:
        out += ["    // the view node draw", f"    ({f['effect_draw']:#x}, &[\n{hexes(e.read(f['effect_draw'], 24))}\n    ]),"]
    out += ["    // the entity render's call of the body draw, its read of the scale (+0x1b4 round the body draw's commands)",
            "    // and the tags of the scale / restore commands it wraps them in",
            f"    {at(f['render_call'])},", f"    {at(f['render_scale'])},",
            f"    {at(f['cmd_tags'][0][0])}, {at(f['cmd_tags'][1][0])},",
            "    // the UI's calls of the anim lookup (encyclopedia, pick slot, BP grid, pick moment, scoreboard portraits) and",
            "    // their size asks"]
    for k, (c, w) in enumerate(f["ui"]):
        out.append(f"    {at(c)}, // {UI_NAMES[k] if k < len(UI_NAMES) else k}")
        out.append("    " + ", ".join(at(a) for a in w) + ",")
    out += ["    // the same drawers' own calls of the sheet lookup (src/ui.rs)",
            "    " + ", ".join(at(s) for s in f["ui_sheet_calls"]) + ",",
            "    // the draw command made from a sheet's name (src/ui.rs hooks its prologue)",
            f"    ({f['cmd_by_name']:#x}, &[\n{hexes(e.read(f['cmd_by_name'], 48))}\n    ]),",
            "    // the image node's setter (src/ui.rs hooks its prologue)",
            f"    ({f['node_image']:#x}, &[\n{hexes(e.read(f['node_image'], 48))}\n    ]),"]
    out += ["    // the anim tables' hash", f"    ({f['hash']:#x}, &[\n{hexes(e.read(f['hash'], 48))}\n    ]),",
            "    // the display-update handler",
            f"    ({f['display_fn']:#x}, &[\n{hexes(e.read(f['display_fn'], 48))}\n    ]),",
            "    // the battlefield frame lookup's call of the anim lookup, and its size asks (width, height)",
            f"    {at(f['battle_anim_ret'][0] - 5)},", f"    {at(asks[0])},", f"    {at(asks[1])},",
            "    // the body draw's size asks", "    " + ", ".join(at(a) for a in asks[2:]) + ",", "    ],", "}];"]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exe", default=GAME)
    ap.add_argument("--build-rs", default=BUILD_RS, help="the build.rs whose build is the starting point")
    ap.add_argument("--out")
    a = ap.parse_args()
    b = old_build(a.build_rs)
    e = Exe(a.exe)
    if all(e.read(r, len(x)) == x for r, x in b["sigs"].items()):
        print(f"this EXE is the build build.rs lists ({b['name']}): nothing to find")
        return
    found, notes, ui_rows = search(e, b)
    check(e, found)
    for n in notes:
        print(n)
    print(f"anim {found['anim']:#x}, sheet {found['sheet']:#x}, hash {found['hash']:#x}, battlefield frame lookup "
          f"{found['battle_frame']:#x}, body draw {found['body_draw']:#x}, entity render call "
          f"{found['render_call']:#x} / scale {found['render_scale']:#x}, grow_one {found['cmd_grow']:#x}, display "
          f"{found['display_fn']:#x} / slot {found['display_slot']:#x}")
    print(f"scale / restore command tags {found['cmd_tags'][0][1]:#x} / {found['cmd_tags'][1][1]:#x}; UI sheet sinks: draw "
          f"command {found['cmd_by_name']:#x}, image node {found['node_image']:#x}; view node draw {found['effect_draw']:#x}")
    print("UI drawers (confirm by eye: the lower the score the closer to the old layout):")
    print("\n".join(ui_rows))
    print(f"whole-body add-ons (view.rs): FN_RVA {found['display_fn']:#x}, SLOT_RVA {found['display_slot']:#x}")
    text = rust(e, found)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text + "\n")
        print("Build ->", a.out)
    else:
        print(text)


if __name__ == "__main__":
    main()
