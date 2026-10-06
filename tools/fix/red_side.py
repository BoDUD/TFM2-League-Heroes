"""The red-side changes (tools/fix/red_side_caster_fx.py) applied to a kit built again from its parameters.

    import red_side; kit = red_side.apply(kit, "tryndamere")

tools/kit/build_tryndamere.py and build_xinzhao.py write their heroes' kits from parameter tables, and the add-ons'
make_override.py build their copies the same way; the red-side pass (pictures drawn into the hero's frames, others
made symmetric) changed the written kits, so build() runs this on what it makes: tools/fix/bake_caster_fx.py frozen to
assets/source/native/<hero>_bake.json, then tools/fix/mirror_union_fx.py's <hero>_sym.json bindings.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bake_caster_fx  # noqa: E402
import mirror_union_fx  # noqa: E402
from red_side_caster_fx import CUT  # noqa: E402


def apply(kit, hero):
    bake_caster_fx.bake_kit(kit, hero, cut=[f"league_{hero}_{n}" for n in CUT.get(hero, [])], frozen=True)
    return mirror_union_fx.rebind(kit, hero)
