"""
Kiosk PNGs are RGBA. Two ways to avoid a lit “grey box” on the full quad:

1) Soft transparency — alphamap + blending (semi-transparent edges on strokes).
2) Hard cutout — alphatest discards fragments below a threshold (only drawn pixels
   contribute; no shading where alpha is low).

PBR MAT reads the **red** channel of the alphamap as opacity (not PNG alpha). Prefer
`fish_matalpha` Reorder (see build_fish_school / patch_fish_matalpha_reorder.py).

This script applies both the alpha map and a cutout. Tune ALPHATEST_THRESHOLD: lower
keeps softer brush edges but may leave faint halos; higher is harsher but cleaner.

Set USE_ALPHATEST = False to rely on blending only (softer fringe, no discard).
"""
import td

USE_ALPHATEST = True
# Higher = more solid silhouette (less semi-transparent fringe on kiosk PNGs).
ALPHATEST_THRESHOLD = 0.28

P = op("/project1/fish_tank_poll")
M = P.op("fish_pbr") if P else None
if not M:
    raise RuntimeError("Missing /project1/fish_tank_poll/fish_pbr")

ro = P.op("fish_matalpha") if P else None
if ro:
    M.par.alphamap = ro.path
else:
    M.par.alphamap = M.par.basecolormap
M.par.alphamode = True
M.par.pointcolorpremult = "premultinshader"

if USE_ALPHATEST:
    M.par.alphatest = True
    M.par.alphafunc = "greater"
    M.par.alphathreshold = ALPHATEST_THRESHOLD
    try:
        M.par.alphaside = 1
    except Exception:
        pass
    try:
        M.par.postmultalpha = False
    except Exception:
        pass
    # Cutout: fragments are in or out; opaque-style compositing + depth.
    M.par.blending = False
    M.par.depthwriting = True
else:
    M.par.alphatest = False
    M.par.blending = True
    M.par.depthwriting = False

print("OK:", M.path, "| alphatest", M.par.alphatest.eval())
