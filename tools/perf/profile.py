#!/usr/bin/env python3
"""Where does a simulated match spend its CPU? A sampling profiler for tools/perf/tick.exe (Windows only).

Build tick.exe with a linker map (add `-C link-arg=/MAP:tick.map` to the rustc line of the SDK's build.sh),
then run from the folder that holds sim/assets/:

    python tools/perf/profile.py sim/tick.exe sim/tick.map 300 1 <10 champions as for tick.exe>

Every 2 ms the main thread is suspended and its call stack walked with dbghelp's StackWalk64; addresses
are named with the map file. Prints the functions by inclusive share of samples, then which callers sit
above the effect-tree clones (DataEffectDef::clone) and their drops - the two hot spots of docs/perf.md.
"""
import bisect
import collections
import ctypes
import ctypes.wintypes as wt
import re
import subprocess
import sys
import time

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
dbg = ctypes.WinDLL("dbghelp", use_last_error=True)
psapi = ctypes.WinDLL("psapi")
IMAGE_BASE = 0x140000000


class ADDRESS64(ctypes.Structure):
    _fields_ = [("Offset", ctypes.c_uint64), ("Segment", ctypes.c_uint16), ("Mode", ctypes.c_uint32)]


class KDHELP64(ctypes.Structure):
    _fields_ = [("Thread", ctypes.c_uint64), ("ThCallbackStack", wt.DWORD), ("ThCallbackBStore", wt.DWORD),
                ("NextCallback", wt.DWORD), ("FramePointer", wt.DWORD), ("KiCallUserMode", ctypes.c_uint64),
                ("KeUserCallbackDispatcher", ctypes.c_uint64), ("SystemRangeStart", ctypes.c_uint64),
                ("KiUserExceptionDispatcher", ctypes.c_uint64), ("StackBase", ctypes.c_uint64),
                ("StackLimit", ctypes.c_uint64), ("BuildVersion", wt.DWORD), ("RetpolineStubFunctionTableSize", wt.DWORD),
                ("RetpolineStubFunctionTable", ctypes.c_uint64), ("RetpolineStubOffset", wt.DWORD),
                ("RetpolineStubSize", wt.DWORD), ("Reserved0", ctypes.c_uint64 * 2)]


class STACKFRAME64(ctypes.Structure):
    _fields_ = [("AddrPC", ADDRESS64), ("AddrReturn", ADDRESS64), ("AddrFrame", ADDRESS64), ("AddrStack", ADDRESS64),
                ("AddrBStore", ADDRESS64), ("FuncTableEntry", ctypes.c_void_p), ("Params", ctypes.c_uint64 * 4),
                ("Far", wt.BOOL), ("Virtual", wt.BOOL), ("Reserved", ctypes.c_uint64 * 3), ("KdHelp", KDHELP64)]


class THREADENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ThreadID", wt.DWORD),
                ("th32OwnerProcessID", wt.DWORD), ("tpBasePri", wt.LONG), ("tpDeltaPri", wt.LONG), ("dwFlags", wt.DWORD)]


dbg.SymFunctionTableAccess64.restype = ctypes.c_void_p
dbg.SymFunctionTableAccess64.argtypes = [wt.HANDLE, ctypes.c_uint64]
dbg.SymGetModuleBase64.restype = ctypes.c_uint64
dbg.SymGetModuleBase64.argtypes = [wt.HANDLE, ctypes.c_uint64]
dbg.StackWalk64.argtypes = [wt.DWORD, wt.HANDLE, wt.HANDLE, ctypes.POINTER(STACKFRAME64), ctypes.c_void_p,
                            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
dbg.SymInitialize.argtypes = [wt.HANDLE, ctypes.c_char_p, wt.BOOL]
k32.OpenThread.restype = wt.HANDLE
k32.OpenProcess.restype = wt.HANDLE
CONTEXT_SIZE, CONTEXT_FULL = 1232, 0x10001F
RIP, RSP, RBP, FLAGS = 0xF8, 0x98, 0xA0, 0x30


def load_map(path):
    syms = []
    for line in open(path, encoding="latin-1"):
        m = re.match(r"\s*[0-9a-f]{4}:[0-9a-f]{8}\s+(\S+)\s+([0-9a-f]{16})\s", line)
        if m and int(m.group(2), 16):
            syms.append((int(m.group(2), 16), m.group(1)))
    syms.sort()
    return [a for a, _ in syms], [s for _, s in syms]


def short(sym):
    """Readable path of a Rust mangled symbol: its length-prefixed identifiers joined with ::."""
    ids, i = [], 0
    while i < len(sym):
        if sym[i].isdigit() and (i == 0 or not sym[i - 1].isdigit()):
            j = i
            while j < len(sym) and sym[j].isdigit():
                j += 1
            n = int(sym[i:j])
            j += sym[j:j + 1] == "_"
            ident = sym[j:j + n]
            if n > 1 and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", ident) and not re.fullmatch(r"h[0-9a-f]{16}", ident):
                ids.append(ident)
                i = j + n
                continue
        i += 1
    return "::".join(ids)[-110:] or sym[:110]


def sample(exe, mapfile, args):
    addrs, names = load_map(mapfile)
    p = subprocess.Popen([exe] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.4)
    snap = k32.CreateToolhelp32Snapshot(4, 0)
    te = THREADENTRY32()
    te.dwSize = ctypes.sizeof(THREADENTRY32)
    tid = None
    ok = k32.Thread32First(snap, ctypes.byref(te))
    while ok and tid is None:
        if te.th32OwnerProcessID == p.pid:
            tid = te.th32ThreadID
        ok = k32.Thread32Next(snap, ctypes.byref(te))
    k32.CloseHandle(snap)
    th = k32.OpenThread(0x1FFFFF, False, tid)
    hproc = k32.OpenProcess(0x1FFFFF, False, p.pid)
    mods = (ctypes.c_void_p * 64)()
    needed = wt.DWORD()
    psapi.EnumProcessModules(hproc, mods, ctypes.sizeof(mods), ctypes.byref(needed))
    delta = mods[0] - IMAGE_BASE
    dbg.SymInitialize(hproc, None, True)
    raw = ctypes.create_string_buffer(CONTEXT_SIZE + 16)
    ctx = (ctypes.addressof(raw) + 15) & ~15
    fta = ctypes.cast(dbg.SymFunctionTableAccess64, ctypes.c_void_p)
    gmb = ctypes.cast(dbg.SymGetModuleBase64, ctypes.c_void_p)
    stacks = collections.Counter()
    while p.poll() is None:
        if k32.SuspendThread(th) == 0xFFFFFFFF:
            break
        ctypes.memset(ctx, 0, CONTEXT_SIZE)
        ctypes.c_uint32.from_address(ctx + FLAGS).value = CONTEXT_FULL
        frames = []
        if k32.GetThreadContext(th, ctypes.c_void_p(ctx)):
            sf = STACKFRAME64()
            for field, off in (("AddrPC", RIP), ("AddrFrame", RBP), ("AddrStack", RSP)):
                getattr(sf, field).Offset = ctypes.c_uint64.from_address(ctx + off).value
                getattr(sf, field).Mode = 3
            for _ in range(48):
                if not dbg.StackWalk64(0x8664, hproc, th, ctypes.byref(sf), ctypes.c_void_p(ctx), None, fta, gmb, None):
                    break
                if not sf.AddrPC.Offset:
                    break
                frames.append(sf.AddrPC.Offset - delta)
        k32.ResumeThread(th)
        if frames:
            stacks[tuple(names[bisect.bisect_right(addrs, a) - 1] if IMAGE_BASE <= a < IMAGE_BASE + 0x10000000
                         else "<external>" for a in frames)] += 1
        time.sleep(0.002)
    print(p.stdout.read().decode(errors="replace").splitlines()[0])
    return stacks


def report(stacks):
    n = sum(stacks.values())
    print(f"{n} samples")
    incl = collections.Counter()
    for st, c in stacks.items():
        for s in set(st):
            incl[s] += c
    print("== inclusive")
    for s, c in incl.most_common(40):
        print(f"{100 * c / n:5.1f}%  {short(s)}")
    for what, keys in (("clone", ("clone", "Clone")), ("drop", ("drop",))):
        above = collections.Counter()
        for st, c in stacks.items():
            hit = [i for i, s in enumerate(st) if "DataEffectDef" in s and any(k in s for k in keys)]
            if hit:
                for s in st[hit[-1] + 1:]:
                    if not any(k in s for k in ("clone", "Clone", "alloc", "drop", "from_iter")):
                        above[short(s)] += c
                        break
        print(f"== first caller above DataEffectDef {what}")
        for s, c in above.most_common(8):
            print(f"{100 * c / n:5.1f}%  {s}")


if __name__ == "__main__":
    report(sample(sys.argv[1], sys.argv[2], sys.argv[3:]))
