# Fix blue (and any low-R) fish colours vanishing in PBR.
# PBR MAT reads opacity from the alphamap's RED channel, not PNG alpha — this Reorder
# copies true alpha → red. Run after pull or if fish_pbr still points alphamap at fish_movie.
#
# Textport:
#   exec(open(r"/Users/seph/Desktop/FishTank/V1/fish-tank/touchdesigner/patch_fish_matalpha_reorder.py", encoding="utf-8").read())

import td


def _configure_fish_alpha_reorder(ro):
    for src in ("input0", "input1", "i0", "i1", 0, 1):
        try:
            ro.par.outputred = src
            break
        except Exception:
            continue
    for ch in ("a", "alpha", 3):
        try:
            ro.par.outputredchan = ch
            break
        except Exception:
            continue


P = op("/project1/fish_tank_poll")
if not P:
    raise RuntimeError("Missing /project1/fish_tank_poll")

for i in range(20):
    mv = P.op("fish_movie_%d" % i)
    M = P.op("fish_pbr_%d" % i)
    if not mv or not M:
        print("skip slot", i)
        continue
    ro = P.op("fish_matalpha_%d" % i)
    if not ro:
        ro = P.create(td.reorderTOP, "fish_matalpha_%d" % i)
    ro.inputConnectors[0].connect(mv)
    _configure_fish_alpha_reorder(ro)
    M.par.basecolormap = mv.path
    M.par.alphamap = ro.path
    print("OK", ro.path, "→", M.path)

M0 = P.op("fish_pbr")
mv0 = P.op("fish_movie")
if M0 and mv0:
    ro0 = P.op("fish_matalpha")
    if not ro0:
        ro0 = P.create(td.reorderTOP, "fish_matalpha")
    ro0.inputConnectors[0].connect(mv0)
    _configure_fish_alpha_reorder(ro0)
    M0.par.basecolormap = mv0.path
    M0.par.alphamap = ro0.path
    print("OK", ro0.path, "→", M0.path)

print("Done: patch_fish_matalpha_reorder")
