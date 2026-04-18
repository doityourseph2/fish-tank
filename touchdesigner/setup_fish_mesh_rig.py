"""
Rebuild the 3D fish path under /project1/fish_tank_poll:

  fish_movie (texture URL from kiosk) → fish_pbr base color
  fish_mesh_rig: grid → transform → noise (swim) → material → render
  fish_render + fish_label → fish_comp → fish_out

Non-Commercial safe: fish_render is 1280×720 (≤1280×1280).

Paste into Textport. Destroys existing fish_mesh_rig, fish_pbr, fish_cam, fish_light, fish_render
if present, then recreates.
"""
import td

P = op("/project1/fish_tank_poll")
if not P:
    raise RuntimeError("Missing /project1/fish_tank_poll")

# Drop render + geo before material (geo references fish_pbr).
for name in ("fish_render", "fish_light", "fish_cam", "fish_mesh_rig", "fish_pbr"):
    n = P.op(name)
    if n:
        n.destroy()

G = P.create(td.geometryCOMP, "fish_mesh_rig")
G.par.tx.expr = "sin(absTime.seconds * 0.7) * 0.15"
G.par.ty.expr = "cos(absTime.seconds * 0.5) * 0.08"

body = G.create(td.gridSOP, "body")
body.par.rows = 24
body.par.cols = 32

pose = G.create(td.transformSOP, "pose")
pose.inputConnectors[0].connect(body)
pose.par.sx = 1.1
pose.par.sy = 0.55
pose.par.ry = 15

swim = G.create(td.noiseSOP, "swim")
swim.inputConnectors[0].connect(pose)
swim.par.type = "sparse"
swim.par.amp = 0.12
swim.par.period = 2.2
swim.par.rough = 0.55
swim.par.tz.expr = "absTime.seconds * 0.8"

mat1 = G.create(td.materialSOP, "mat1")
mat1.inputConnectors[0].connect(swim)

M = P.create(td.pbrMAT, "fish_pbr")
M.par.basecolormap = P.path + "/fish_movie"
M.par.roughness = 0.45
M.par.metallic = 0
mat1.par.mat = M.path

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
if fc and fr:
    fc.inputConnectors[0].connect(fr)

print("OK:", G.path, rend.path)
