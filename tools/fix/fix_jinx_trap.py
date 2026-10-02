"""Jinx E (Flame Chompers): one bite per trap, whatever the engine does with a dead caster.

Players on the new version again: a champion died at once standing on two traps ("被秒的英雄同时碰到了两个炸弹").
The trap was a chain of links started from each other's end_effects - those go on after Jinx dies - and a bite
stopped the chain through a lock on Jinx (WithSelf -> Delayed 1 -> AddCasterBuff, 20 ticks). A dead caster's buffs
are frozen (nothing added), so after her death every link bit the rooted champion again; the 0.36.1 fix only kept
the checks from spawning (in the SDK a dead caster fires no projectile from a Delayed), which the game version may
not share. Two traps at once (cooldown cuts) also shared the lock: checks on the same tick both bit.

The trap is rebuilt flat (league_teemo R's way): a Position cast keeps its point for every effect it runs, so the 20
links are Delayed effects of the cast itself (36 + 15 k ticks: the throw lands on tick 36), the fizzle after them.
A dead caster's pending Delayed effects stop with him (SDK), so her trap dies with her. Each link, at the cast point:
- skip if this trap already bit (e_spent<slot>, set 1 tick after a bite) - one bite per trap;
- from the third link on, skip unless the link before ran (e_hb<slot>_<k-1>, set by it): if her links did go on after
  death (her flags frozen, nothing added), the trap would stop one link later, at most one bite after it;
- the lying trap's picture; the check (RangeProjectile on EnemyChampion, as before) unless a trap bit someone in the
  last 90 ticks (e_lock: the root's length, shared by her traps) - every champion inside at that check is bitten
  (Bind 90, 80 + 100% AD), then e_lock and e_spent<slot> go on a tick later.
Casts alternate between two slots (a permanent e_slot toggle), so a second trap thrown while the first lies (cooldown
cuts) has flags of its own; each cast clears its slot's. The first link is ungated by the heartbeat, so the AI, which
scores the branch the caster's buffs pick, still sees the bite. The throw now lands on the cast point itself (range
120000: the links stand there).

    python tools/fix/fix_jinx_trap.py <league_jinx.data_champion>
"""
import json
import os
import sys

N = 20                      # links: 5 s
FIRST = 36                  # the throw lands (Delayed 12 + travel 24)
STEP = 15
LOCK = 90                   # e_lock: the root's length
P = "league_jinx_"


def n(x):
    return P + x


def flag(name, tick):
    return {"type": "AddCasterBuff", "buff_state": {"name": n(name), "duration": {"Time": {"tick": tick}}},
            "only_to_enemy": False}


def sw(buff, yes, no):
    return {"type": "SwitchByBuff", "buff_name": n(buff), "effect_buff": yes, "effect_none": no}


def combine(*effects):
    return {"type": "Combine", "effects": list(effects)}


NONE = combine()


def rm(*names):
    return [{"type": "RemoveCasterBuff", "name": n(x)} for x in names]


def find(o, pred):
    if isinstance(o, dict):
        if pred(o):
            return o
        for v in o.values():
            r = find(v, pred)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find(v, pred)
            if r is not None:
                return r
    return None


def depth(o):
    if isinstance(o, dict):
        return 1 + max((depth(v) for v in o.values()), default=0)
    if isinstance(o, list):
        return 1 + max((depth(v) for v in o), default=0)
    return 0


def main(path):
    lp = chr(92) * 2 + "?" + chr(92) + os.path.abspath(path)
    raw = open(lp, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"
    k = json.loads(raw)
    e = k["skill2"]["effect"]
    cast_sfx = e["effects"][0]
    throw = e["effects"][1]["effects"][0]
    assert throw["name"] == n("e_throw")
    old_check = find(e, lambda o: o.get("type") == "RangeProjectile" and o.get("name") == n("e_check"))
    bite = old_check["applied_effects"][0]["effect"]["effect_none"]["effects"]
    kinds = [b["type"] for b in bite]
    assert kinds == ["ViewEffect", "TargetSfx", "Bind", "Attack", "WithSelf"], kinds
    arm_sfx, arm_view = throw["end_effects"][0], throw["end_effects"][1]["effects"][0]
    assert arm_view == {"type": "ViewEffect", "name": n("e_arm")}

    def trap(slot):
        spent = f"e_spent{slot}"
        life = FIRST + STEP * (N + 1)
        after_bite = {"type": "WithSelf", "effects": [{"type": "Delayed", "tick": 1, "effects": [
            flag("e_lock", LOCK), flag(spent, life)]}]}
        check = {"type": "RangeProjectile", "name": n("e_check"), "delay": old_check["delay"], "apply": old_check["apply"],
                 "shape": old_check["shape"], "applied_target": "EnemyChampion",
                 "applied_effects": [{"casting_type": "Targeting", "effect": sw("e_lock", NONE, sw(spent, NONE, combine(
                     *bite[:4], after_bite)))}]}
        links = []
        for j in range(1, N + 1):
            body = combine(flag(f"e_hb{slot}_{j}", STEP * 2), {"type": "ViewEffect", "name": n("e_trap")},
                           sw("e_lock", NONE, check))
            gated = body if j <= 2 else sw(f"e_hb{slot}_{j - 1}", body, NONE)
            links.append({"type": "Delayed", "tick": FIRST + STEP * j, "effects": [sw(spent, NONE, gated)]})
        fizzle = {"type": "Delayed", "tick": FIRST + STEP * (N + 1), "effects": [
            sw(spent, NONE, sw(f"e_hb{slot}_{N}", {"type": "ViewEffect", "name": n("e_fizzle")}, NONE))]}
        clear = rm(spent, *[f"e_hb{slot}_{j}" for j in range(1, N + 1)])
        return combine(*clear, *links, fizzle)

    throw["range"] = 120000                       # lands on the cast point, where the links stand
    throw["end_effects"] = [arm_sfx, arm_view]
    k["skill2"]["effect"] = combine(
        cast_sfx, e["effects"][1],
        sw("e_slot", combine(*rm("e_slot"), trap(1)),
           combine({"type": "AddCasterBuff", "buff_state": {"name": n("e_slot"), "duration": "Permanent"},
                    "only_to_enemy": False}, trap(0))))
    out = json.dumps(k, ensure_ascii=False, indent=2) + "\n"
    if nl == "\r\n":
        out = out.replace("\n", "\r\n")
    open(lp, "wb").write(out.encode("utf-8"))
    print(f"{path}: E rebuilt flat, {N} links x 2 slots, depth {depth(k['skill2'])}, "
          f"{len(json.dumps(k['skill2']))} bytes")


if __name__ == "__main__":
    main(sys.argv[1])
