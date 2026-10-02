# Nocturne TFM2 size-design handoff

Two preliminary game-size designs were exported from the supplied image pack. The image-generation instructions in that pack were treated as production specifications, while its images were used as references.

## Deliverables

- `nocturne_design_A.png` / `nocturne_design_B.png`: 1024×1024 PNG, exact nearest-neighbour 8× presentation on a 128×128 game-pixel canvas.
- `nocturne_design_A_1x.png` / `nocturne_design_B_1x.png`: the same 128×128 canvases at actual game-pixel size.
- `nocturne_design_comparison.png`: A/B comparison, including a neutral-background 8× preview and small-size views.
- `palette_*.gpl` and `palette_*.json`: palette for each version.
- `QA.json`: measured dimensions, palette and alpha checks.

## What passed

- The generated art was sampled on its recovered logical pixel grid, one source cell per game pixel; the final 1024px files use hard 8× nearest-neighbour blocks.
- Alpha is binary (0 or 255), the only background pixels are transparent, and the character is a single 8-connected silhouette.
- A uses 21 opaque colours; B uses 20. White cells occur only at the eyes.
- Both tails end on canvas column 64, row 99 (8× canvas coordinate x=512, y=792). No opaque pixels occur below the tail tip.
- A has diagonal 2×1 eye slits; B has two 2×2 eye blocks. Both retain the hunched pose, shoulder runes, gauntlets, forearm blades, tabard and smoke tail.

## Deviations to resolve before production use

The package specified a 32×44 game-pixel body. Grid measurement found A at **37×50** and B at **37×46**. The requested geometry reduction did not complete because the image-generation endpoint returned HTTP 403 twice. The character was therefore not cropped or reshaped to disguise the mismatch. B’s eyes and head are larger than A’s as requested, but the whole pose and the two silhouettes still need final visual approval. These files are size-study candidates; they are not a packed or animated game asset.

Next: redraw to 32×44 while preserving the approved silhouette, review against the in-game quality reference, then proceed to action frames only after a design is selected.

