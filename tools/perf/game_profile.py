#!/usr/bin/env python3
"""Where does the running game spend its CPU? A sampling profiler that attaches to TeamfightManager2.exe (Windows).

    python tools/perf/game_profile.py [seconds=60] [--pid N] [--out report.txt]

Start the game, open a match (on screen, at the speed that stutters), then run this. For `seconds` it measures each
thread's CPU time (GetThreadTimes) and every ~3 ms suspends the busy threads and walks their stacks (dbghelp
StackWalk64, the modules' own unwind tables). Prints per thread: CPU use second by second, the share of samples whose
innermost frame is in each module, the share with each module anywhere on the stack (a mod's DLL calling back into
the game counts for the mod), and for the mods' DLLs the functions (by their PDB when it sits where it was built,
else by export or RVA). Nothing is written into the game; the threads stop for a few microseconds per sample.
"""
import argparse
import collections
import ctypes
import ctypes.wintypes as wt
import os
import sys
import time

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
dbg = ctypes.WinDLL("dbghelp", use_last_error=True)
psapi = ctypes.WinDLL("psapi")


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


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.c_void_p), ("th32ModuleID", wt.DWORD), ("cntThreads", wt.DWORD),
                ("th32ParentProcessID", wt.DWORD), ("pcPriClassBase", wt.LONG), ("dwFlags", wt.DWORD),
                ("szExeFile", wt.WCHAR * 260)]


class MODULEINFO(ctypes.Structure):
    _fields_ = [("lpBaseOfDll", ctypes.c_void_p), ("SizeOfImage", wt.DWORD), ("EntryPoint", ctypes.c_void_p)]


class SYMBOL_INFO(ctypes.Structure):
    _fields_ = [("SizeOfStruct", wt.ULONG), ("TypeIndex", wt.ULONG), ("Reserved", ctypes.c_uint64 * 2),
                ("Index", wt.ULONG), ("Size", wt.ULONG), ("ModBase", ctypes.c_uint64), ("Flags", wt.ULONG),
                ("Value", ctypes.c_uint64), ("Address", ctypes.c_uint64), ("Register", wt.ULONG), ("Scope", wt.ULONG),
                ("Tag", wt.ULONG), ("NameLen", wt.ULONG), ("MaxNameLen", wt.ULONG), ("Name", ctypes.c_char * 512)]


dbg.SymFunctionTableAccess64.restype = ctypes.c_void_p
dbg.SymFunctionTableAccess64.argtypes = [wt.HANDLE, ctypes.c_uint64]
dbg.SymGetModuleBase64.restype = ctypes.c_uint64
dbg.SymGetModuleBase64.argtypes = [wt.HANDLE, ctypes.c_uint64]
dbg.StackWalk64.argtypes = [wt.DWORD, wt.HANDLE, wt.HANDLE, ctypes.POINTER(STACKFRAME64), ctypes.c_void_p,
                            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
dbg.SymInitialize.argtypes = [wt.HANDLE, ctypes.c_char_p, wt.BOOL]
dbg.SymFromAddr.argtypes = [wt.HANDLE, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(SYMBOL_INFO)]
dbg.SymSetOptions.argtypes = [wt.DWORD]
dbg.SymLoadModuleExW.restype = ctypes.c_uint64
dbg.SymLoadModuleExW.argtypes = [wt.HANDLE, wt.HANDLE, wt.LPCWSTR, wt.LPCWSTR, ctypes.c_uint64, wt.DWORD,
                                 ctypes.c_void_p, wt.DWORD]
k32.OpenThread.restype = wt.HANDLE
k32.OpenProcess.restype = wt.HANDLE
k32.CreateToolhelp32Snapshot.restype = wt.HANDLE
k32.GetThreadTimes.argtypes = [wt.HANDLE] + [ctypes.POINTER(ctypes.c_uint64)] * 4
psapi.EnumProcessModulesEx.argtypes = [wt.HANDLE, ctypes.c_void_p, wt.DWORD, ctypes.POINTER(wt.DWORD), wt.DWORD]
psapi.GetModuleFileNameExW.argtypes = [wt.HANDLE, ctypes.c_void_p, wt.LPWSTR, wt.DWORD]
psapi.GetModuleInformation.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.POINTER(MODULEINFO), wt.DWORD]
CONTEXT_SIZE, CONTEXT_FULL = 1232, 0x10001F
RIP, RSP, RBP, FLAGS = 0xF8, 0x98, 0xA0, 0x30
GAME = "TeamfightManager2.exe"


def find_pid():
    snap = k32.CreateToolhelp32Snapshot(2, 0)
    pe = PROCESSENTRY32W()
    pe.dwSize = ctypes.sizeof(pe)
    ok = k32.Process32FirstW(snap, ctypes.byref(pe))
    pid = None
    while ok:
        if pe.szExeFile.lower() == GAME.lower():
            pid = pe.th32ProcessID
        ok = k32.Process32NextW(snap, ctypes.byref(pe))
    k32.CloseHandle(snap)
    return pid


def threads_of(pid):
    snap = k32.CreateToolhelp32Snapshot(4, 0)
    te = THREADENTRY32()
    te.dwSize = ctypes.sizeof(te)
    out = []
    ok = k32.Thread32First(snap, ctypes.byref(te))
    while ok:
        if te.th32OwnerProcessID == pid:
            out.append(te.th32ThreadID)
        ok = k32.Thread32Next(snap, ctypes.byref(te))
    k32.CloseHandle(snap)
    return out


def modules_of(hproc):
    arr = (ctypes.c_void_p * 1024)()
    need = wt.DWORD()
    psapi.EnumProcessModulesEx(hproc, arr, ctypes.sizeof(arr), ctypes.byref(need), 3)
    mods = []
    for i in range(need.value // ctypes.sizeof(ctypes.c_void_p)):
        name = ctypes.create_unicode_buffer(520)
        psapi.GetModuleFileNameExW(hproc, arr[i], name, 520)
        mi = MODULEINFO()
        psapi.GetModuleInformation(hproc, arr[i], ctypes.byref(mi), ctypes.sizeof(mi))
        mods.append((mi.lpBaseOfDll, mi.lpBaseOfDll + mi.SizeOfImage, os.path.basename(name.value), name.value))
    mods.sort()
    return mods


def cpu_of(th):
    c, e, k, u = (ctypes.c_uint64() for _ in range(4))
    k32.GetThreadTimes(th, ctypes.byref(c), ctypes.byref(e), ctypes.byref(k), ctypes.byref(u))
    return (k.value + u.value) / 1e7


class Profiler:
    def __init__(self, pid):
        self.pid = pid
        self.hproc = k32.OpenProcess(0x1FFFFF, False, pid)
        if not self.hproc:
            sys.exit(f"cannot open process {pid} (error {ctypes.get_last_error()})")
        dbg.SymSetOptions(0x2 | 0x4 | 0x10)  # undecorate, deferred loads, load lines off
        dbg.SymInitialize(self.hproc, None, False)
        self.mods = modules_of(self.hproc)
        for lo, hi, _, path in self.mods:  # every module by hand: its PDB where it was built, else its exports
            dbg.SymLoadModuleExW(self.hproc, None, path, None, ctypes.c_uint64(lo), hi - lo, None, 0)
        self.raw = ctypes.create_string_buffer(CONTEXT_SIZE + 16)
        self.ctx = (ctypes.addressof(self.raw) + 15) & ~15
        self.fta = ctypes.cast(dbg.SymFunctionTableAccess64, ctypes.c_void_p)
        self.gmb = ctypes.cast(dbg.SymGetModuleBase64, ctypes.c_void_p)
        self.sym_cache = {}

    def module(self, a):
        lo, hi = 0, len(self.mods)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.mods[mid][0] <= a:
                lo = mid + 1
            else:
                hi = mid
        if lo and a < self.mods[lo - 1][1]:
            return self.mods[lo - 1]
        return None

    def name(self, a):
        m = self.module(a)
        if m is None:
            return "?"
        if a in self.sym_cache:
            return self.sym_cache[a]
        si = SYMBOL_INFO()
        si.SizeOfStruct = 88  # sizeof(SYMBOL_INFO) with its one-char Name
        si.MaxNameLen = 511
        disp = ctypes.c_uint64()
        if dbg.SymFromAddr(self.hproc, a, ctypes.byref(disp), ctypes.byref(si)) and disp.value < 0x100000:
            s = f"{m[2]}!{si.Name.decode(errors='replace')}"
        else:
            s = f"{m[2]}+{a - m[0]:#x}"
        self.sym_cache[a] = s
        return s

    def stack(self, th):
        if k32.SuspendThread(th) == 0xFFFFFFFF:
            return None
        frames = []
        try:
            ctypes.memset(self.ctx, 0, CONTEXT_SIZE)
            ctypes.c_uint32.from_address(self.ctx + FLAGS).value = CONTEXT_FULL
            if k32.GetThreadContext(th, ctypes.c_void_p(self.ctx)):
                sf = STACKFRAME64()
                for field, off in (("AddrPC", RIP), ("AddrFrame", RBP), ("AddrStack", RSP)):
                    getattr(sf, field).Offset = ctypes.c_uint64.from_address(self.ctx + off).value
                    getattr(sf, field).Mode = 3
                for _ in range(64):
                    if not dbg.StackWalk64(0x8664, self.hproc, th, ctypes.byref(sf), ctypes.c_void_p(self.ctx), None,
                                           self.fta, self.gmb, None):
                        break
                    if not sf.AddrPC.Offset:
                        break
                    frames.append(sf.AddrPC.Offset)
        finally:
            k32.ResumeThread(th)
        return tuple(frames)


WAITS = ("NtWaitFor", "NtDelayExecution", "NtUserMsgWaitFor", "ZwWaitFor", "NtRemoveIoCompletion", "SleepEx",
         "WaitForSingleObject", "WaitForMultipleObjects", "NtUserGetMessage", "NtUserPeekMessage", "SleepConditionVariable",
         "RtlSleepConditionVariable", "NtWaitForAlertByThreadId", "WaitOnAddress", "RtlWaitOnAddress")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seconds", nargs="?", type=float, default=60)
    ap.add_argument("--pid", type=int)
    ap.add_argument("--every", type=float, default=0.003, help="seconds between samples")
    ap.add_argument("--threads", type=int, default=6, help="how many of the busiest threads to sample")
    ap.add_argument("--out")
    a = ap.parse_args()
    pid = a.pid or find_pid()
    if not pid:
        sys.exit(f"{GAME} is not running")
    p = Profiler(pid)
    lines = []

    def out(s=""):
        print(s)
        lines.append(s)

    # 1. the busy threads: CPU over one second
    ths = {}
    for tid in threads_of(pid):
        h = k32.OpenThread(0x1FFFFF, False, tid)
        if h:
            ths[tid] = h
    c0 = {t: cpu_of(h) for t, h in ths.items()}
    time.sleep(1.0)
    busy = sorted(ths, key=lambda t: cpu_of(ths[t]) - c0[t], reverse=True)[:a.threads]
    first = min(ths)  # not reliable as the main thread; the report names threads by what they run
    out(f"{GAME} pid {pid}: {len(ths)} threads, sampling {len(busy)} busiest for {a.seconds:.0f} s every "
        f"{a.every * 1000:.0f} ms")
    mods = [m for m in p.mods if not m[3].lower().startswith(r"c:\windows")]
    out("non-system modules: " + ", ".join(f"{m[2]}@{m[0]:#x}" for m in mods))

    stacks = {t: collections.Counter() for t in busy}
    per_sec = {t: [] for t in busy}
    t_start = time.perf_counter()
    last_cpu = {t: cpu_of(ths[t]) for t in busy}
    next_sec = t_start + 1
    n = 0
    while True:
        now = time.perf_counter()
        if now - t_start >= a.seconds:
            break
        for t in busy:
            s = p.stack(ths[t])
            if s:
                stacks[t][s] += 1
        n += 1
        if now >= next_sec:
            for t in busy:
                c = cpu_of(ths[t])
                per_sec[t].append(c - last_cpu[t])
                last_cpu[t] = c
            next_sec += 1
        time.sleep(a.every)
    elapsed = time.perf_counter() - t_start
    out(f"{n} sampling rounds in {elapsed:.1f} s")

    for t in busy:
        st = stacks[t]
        total = sum(st.values())
        if not total:
            continue
        cpu = per_sec[t]
        out()
        out(f"=== thread {t}{' (first)' if t == first else ''}: {total} samples; CPU per second "
            f"mean {sum(cpu) / max(1, len(cpu)) * 100:.0f}% max {max(cpu, default=0) * 100:.0f}%")
        out("  CPU % by second: " + " ".join(f"{c * 100:.0f}" for c in cpu))
        top_mod = collections.Counter()
        incl_mod = collections.Counter()
        incl_fn = collections.Counter()
        leaf_fn = collections.Counter()
        waiting = 0
        for s, c in st.items():
            names = [p.name(x) for x in s]
            if any(w in nm for nm in names[:6] for w in WAITS):
                waiting += c
                continue
            top_mod[(p.module(s[0]) or (0, 0, "?"))[2]] += c
            for m in {(p.module(x) or (0, 0, "?"))[2] for x in s}:
                incl_mod[m] += c
            for nm in set(names):
                incl_fn[nm] += c
            leaf_fn[names[0]] += c
        run = total - waiting
        out(f"  waiting (blocked / sleeping / vsync): {100 * waiting / total:.1f}%   running: {100 * run / total:.1f}%")
        if not run:
            continue
        out("  innermost frame's module (share of running samples):")
        for m, c in top_mod.most_common(12):
            out(f"    {100 * c / run:5.1f}%  {m}")
        out("  module anywhere on the stack:")
        for m, c in incl_mod.most_common(16):
            out(f"    {100 * c / run:5.1f}%  {m}")
        out("  functions in the mods' DLLs, anywhere on the stack:")
        modnames = {m[2] for m in mods if m[2].lower() != GAME.lower()}
        k = 0
        for nm, c in incl_fn.most_common():
            if nm.split("!")[0].split("+")[0] in modnames and not nm.lower().startswith(("opengl", "nvogl", "atio", "ig")):
                out(f"    {100 * c / run:5.1f}%  {nm[:150]}")
                k += 1
                if k >= 30:
                    break
        out("  innermost functions:")
        for nm, c in leaf_fn.most_common(20):
            out(f"    {100 * c / run:5.1f}%  {nm[:150]}")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
