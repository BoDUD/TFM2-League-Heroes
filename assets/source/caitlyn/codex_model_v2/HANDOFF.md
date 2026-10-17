# Caitlyn model v2 — selection handoff

This package contains three idle-model candidates only. Choose A, B, or C before action strips are rebuilt.

## Files

- `caitlyn_design_A.png`, `B`, `C`: cleaned large-block generated design sources.
- `logical/caitlyn_design_A_1x.png`, `B`, `C`: transparent 1× logical-pixel assets.
- `caitlyn_model_v2_comparison.png`: side-by-side selection preview.
- `caitlyn_model_v2_logical_preview.png`: enlarged view of the 1× readback assets.
- `generation_sources/`: preserved generated sources before readback.
- `validation.json`: measured dimensions, palette counts, and alpha checks.

## Measured grid and segment plan

All three occupied silhouettes are normalized to 40 logical rows from topmost visible block to boot sole. The canvas adds one transparent safety cell on each side. Alpha is binary and each candidate uses at most 24 opaque colors.

| Variant | Design intent | Hat | Face | Torso | Skirt | Legs + boots | Total | Logical canvas |
|---|---|---:|---:|---:|---:|---:|---:|---|
| A | balanced slim | 8 | 8 | 8 | 7 | 9 | 40 | 26×42 |
| B | longest legs | 7 | 8 | 7 | 6 | 12 | 40 | 21×42 |
| C | slightly larger face | 8 | 9 | 7 | 6 | 10 | 40 | 25×42 |

The segment numbers are the redraw guide used to distinguish the three candidates. The 40-row occupied-height measurement is verified from the exported alpha bounds.

## Next step after selection

Use the selected 1× model as the single body reference for idle/run/attack/passive/skill/skill2/E/ultimate/hit/death. Effects remain separate from the character body.

## Limits

These are selection candidates and have not yet been installed or live-tested in Teamfight Manager 2. No installed mod files were changed.
