"""
Create post-processing TOPs under /project1/fish_tank_install if missing:

  install_grain (noise) — very subtle animated grain
  vignette_ramp (+ vignette_ramp_keys table) — radial multiply for edge darkening
  install_finish — add grain over graded image
  install_vignette — multiply finish × vignette_ramp

Then run repair_fish_tank_install_wiring.py to reconnect.

Safe to run repeatedly: only creates ops that are missing.
"""
import td

I = op("/project1/fish_tank_install")
if not I:
    raise RuntimeError("Missing fish_tank_install")

W, H = 1280, 720

tbl = I.op("vignette_ramp_keys")
if not tbl:
    tbl = I.create(td.tableDAT, "vignette_ramp_keys")
tbl.clear()
tbl.appendRow(["pos", "r", "g", "b", "a"])
tbl.appendRow([0, 1, 1, 1, 1])
tbl.appendRow([0.45, 0.55, 0.62, 0.72, 1])
tbl.appendRow([1, 0.15, 0.2, 0.28, 1])

vr = I.op("vignette_ramp")
if not vr:
    vr = I.create(td.rampTOP, "vignette_ramp")
vr.par.dat = tbl.path
vr.par.type = "radial"
vr.par.outputresolution = "custom"
vr.par.resolutionw = W
vr.par.resolutionh = H
vr.par.position1 = 0.5
vr.par.position2 = 1.0

grain = I.op("install_grain")
if not grain:
    grain = I.create(td.noiseTOP, "install_grain")
grain.par.outputresolution = "custom"
grain.par.resolutionw = W
grain.par.resolutionh = H
grain.par.type = "random"
grain.par.mono = True
grain.par.period = 0.9
grain.par.harmon = 3
grain.par.amp = 0.018
grain.par.tx.expr = "absTime.seconds * 2"
grain.par.ty.expr = "absTime.seconds * -1.7"

fin = I.op("install_finish")
if not fin:
    fin = I.create(td.compositeTOP, "install_finish")
fin.par.operand = "add"
fin.par.size = "input1"

vcomp = I.op("install_vignette")
if not vcomp:
    vcomp = I.create(td.compositeTOP, "install_vignette")
vcomp.par.operand = "multiply"
vcomp.par.size = "input1"

print("OK: post nodes ready — run repair_fish_tank_install_wiring.py")
