"""Find zones (RangePeriodProjectile) whose applied effects do something a player sees behind a caster flag, without
asking first whether the caster lives (a RandomTarget AllyOnlySelf adding a flag that gates them: a search finds no dead
caster). A dead caster's buffs freeze, so a flag frozen on (or off) lets such a zone fire every period while he is dead
(league_caitlyn W, league_jhin E: the reference's "A dead caster"; league_maokai E, league_zoe E, league_azir's soldiers,
league_gangplank's kegs, 2026-11-02). What is left on 2026-11-02 lives a second or two or fires slower than once a
second - turrets, tentacles, plants - and league_teemo R's cloud is guarded by tools/fix/fix_teemo_dead.py.

    python -I tools/kit/scan_dead_zones.py league/champion tft/champion addons/<add-on>/override ...
"""
import json
import os
import sys

VISIBLE = {"ViewEffect", "Sfx", "TargetSfx", "CasterViewEffect", "Attack", "ApAttack", "FixedAttack", "Bind", "Stun",
           "Airborne", "Knockback", "Grab", "Heal", "Shield", "AddBuff", "Fear", "Silence", "Taunt", "Charm",
           "TargetProjectile", "LinearProjectile", "ParabolicProjectile", "RangeProjectile", "RangePeriodProjectile",
           "MoveToTarget", "MoveTo", "Teleport"}


def children(node):
    """Child effect nodes of an effect node."""
    for k, v in node.items():
        if k in ("buff_state", "shape"):
            continue
        items = v if isinstance(v, list) else [v]
        for x in items:
            if not isinstance(x, dict):
                continue
            if "type" in x:
                yield x
            elif isinstance(x.get("effect"), dict):
                yield x["effect"]


def walk(node):
    yield node
    for c in children(node):
        yield from walk(c)


def guard_flags(effect):
    """Flags a search for the caster himself adds, at any range (it finds no dead caster)."""
    out = set()
    for n in walk(effect):
        if n.get("type") == "RandomTarget" and n.get("casting_target") == "AllyOnlySelf":
            for m in walk(n):
                if m.get("type") == "AddCasterBuff":
                    out.add(m["buff_state"]["name"])
    return out


def exposed(node, guards, gates, out):
    """Visible effects reached through caster-flag gates (`gates`) with no guard flag among them."""
    t = node.get("type")
    if t == "RangePeriodProjectile" and gates is not None:
        return  # a zone of its own, scanned on its own
    if t in VISIBLE and gates and not (set(gates) & guards):
        out.add(tuple(gates))
    if t == "RandomTarget" and node.get("casting_target") == "AllyOnlySelf":
        return  # runs only on him, and a search finds no dead caster
    if t == "SwitchByBuff":
        for b in ("effect_buff", "effect_none"):
            if isinstance(node.get(b), dict):
                exposed(node[b], guards, (gates or ()) + (node["buff_name"],), out)
        return
    for c in children(node):
        exposed(c, guards, gates or (), out)


def scan(path, label):
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print("skip", label, e)
        return
    seen = set()
    for action in ("attack", "skill", "skill2", "ult"):
        a = data.get(action)
        if not isinstance(a, dict) or not isinstance(a.get("effect"), dict):
            continue
        for z in walk(a["effect"]):
            if z.get("type") != "RangePeriodProjectile":
                continue
            if z.get("applied_target") == "AllyOnlySelf":
                continue  # it reaches him alone, and a dead caster is no target
            effs = [ap.get("effect") if isinstance(ap, dict) and "effect" in ap else ap
                    for ap in z.get("applied_effects", [])]
            effs = [e for e in effs if isinstance(e, dict)]
            guards = set().union(*(guard_flags(e) for e in effs)) if effs else set()
            out = set()
            for eff in effs:
                exposed(eff, guards, (), out)
            if not out:
                continue
            flags = sorted({g for gates in out for g in gates})
            key = (z.get("name"), tuple(flags))
            if key in seen:
                continue
            seen.add(key)
            print(f"{label}  {action}  zone {z.get('name')}  period {z.get('period')}  life {z.get('tick')}  gates {flags}")


def main(args):
    for a in args:
        if os.path.isdir(a):
            for root, _, files in os.walk(a):
                for f in sorted(files):
                    if f.endswith(".data_champion"):
                        scan(os.path.join(root, f), os.path.relpath(os.path.join(root, f), a))
        else:
            scan(a, a)


if __name__ == "__main__":
    main(sys.argv[1:])
