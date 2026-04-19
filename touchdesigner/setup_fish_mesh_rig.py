"""
Legacy single-slot 3D fish under /project1/fish_tank_poll:

  fish_movie → fish_matalpha (Reorder: A→R) → fish_pbr; fish_movie → base color → fish_mesh_rig → …

For the installation, prefer **`build_fish_school.py`**, which creates **20** slots
(`fish_movie_0` … `fish_movie_19`, matching `apply_fish_display`).

Non-Commercial safe: this script used 1280×720 for one `fish_render` (≤1280×1280).

Paste into Textport. Destroys existing fish_mesh_rig, fish_pbr, fish_cam, fish_light, fish_render
if present, then recreates.
"""
import td

P = op("/project1/fish_tank_poll")
if not P:
    raise RuntimeError("Missing /project1/fish_tank_poll")

# Drop render + geo before material (geo references fish_pbr).
for name in ("fish_render", "fish_light", "fish_cam", "fish_mesh_rig", "fish_pbr", "fish_matalpha"):
    n = P.op(name)
    if n:
        n.destroy()

G = P.create(td.geometryCOMP, "fish_mesh_rig")
G.par.tx.expr = "math.sin(absTime.seconds * 0.7) * 0.15"
G.par.ty.expr = "math.cos(absTime.seconds * 0.5) * 0.08"

body = G.create(td.gridSOP, "body")
body.par.rows = 24
body.par.cols = 32

pose = G.create(td.transformSOP, "pose")
pose.inputConnectors[0].connect(body)
pose.par.sx = 1.1
pose.par.sy = 0.55
pose.par.ry = 15

swim_wave = G.create(td.pointSOP, "swim_wave")
swim_wave.inputConnectors[0].connect(pose)
swim_wave.par.tx.expr = "me.inputPoint.x"
swim_wave.par.ty.expr = (
    "me.inputPoint.y + 0.005 * math.sin(2 * math.pi * 1.22 * me.inputTexture[0] - 6.2 * absTime.seconds)"
)
swim_wave.par.tz.expr = (
    "me.inputPoint.z + 0.0015 * math.cos(2 * math.pi * 1.22 * me.inputTexture[0] - 6.2 * absTime.seconds)"
)

swim = G.create(td.noiseSOP, "swim")
swim.inputConnectors[0].connect(swim_wave)
swim.par.type = "sparse"
swim.par.amp = 0.038
swim.par.period = 2.2
swim.par.rough = 0.4
swim.par.tz.expr = "absTime.seconds * 0.38"

mat1 = G.create(td.materialSOP, "mat1")
mat1.inputConnectors[0].connect(swim)

# New Geometry COMP spawns a default torus — remove it or the render shows a torus, not the grid.
for ch in list(G.children):
    if ch.name.startswith("torus") or "torus" in ch.OPType.lower():
        ch.destroy()

mv_src = P.op("fish_movie")
if not mv_src:
    raise RuntimeError("Missing fish_movie — create or load texture first.")

ro = P.create(td.reorderTOP, "fish_matalpha")
ro.inputConnectors[0].connect(mv_src)
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

M = P.create(td.pbrMAT, "fish_pbr")
M.par.basecolormap = mv_src.path
# PBR reads alphamap **red** as mask; use Reorder so PNG alpha (not RGB) drives it.
M.par.alphamap = ro.path
M.par.alphamode = True
M.par.pointcolorpremult = "premultinshader"
M.par.alphatest = True
M.par.alphafunc = "greater"
M.par.alphathreshold = 0.28
M.par.alphaside = 1
try:
    M.par.postmultalpha = False
except Exception:
    pass
M.par.blending = False
M.par.depthwriting = True
M.par.roughness = 0.4
M.par.metallic = 0
mat1.par.mat = M.path

# Geometry COMP only draws / renders SOPs with display+render enabled (blue/purple flags in UI).
for ch in G.children:
    try:
        ch.display = ch == mat1
        ch.render = ch == mat1
    except Exception:
        pass

cam = P.create(td.cameraCOMP, "fish_cam")
cam.par.tz = 5

light = P.create(td.lightCOMP, "fish_light")

rend = P.create(td.renderTOP, "fish_render")
rend.par.camera = cam.path
rend.par.geometry = G.path
rend.par.lights = light.path
rend.par.rendermode = "render3d"
rend.par.outputresolution = "custom"
rend.par.resolutionw = 1280
rend.par.resolutionh = 720
rend.par.bgcolora = 0

fc = P.op("fish_comp")
fr = P.op("fish_render")
fl = P.op("fish_label")
if fc and fr:
    fc.inputConnectors[0].connect(fr)
if fc and fl:
    fc.inputConnectors[1].connect(fl)

print("OK:", G.path, rend.path)
