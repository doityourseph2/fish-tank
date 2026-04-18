"""
Run in TouchDesigner Textport if composite TOPs report "Not enough sources" or after
reordering nodes under /project1/fish_tank_install.

Reconnects the intended signal chain (does not create missing OPs):

  tank_deep + sand_ramp → sand_merge
  sand_merge + seaweed_xform → env_base
  env_base + water_caustic → water_over_bg (add, size=input1)
  water_over_bg + bubble_level → bubble_merge (over, size=input1)
  bubble_noise → bubble_level
  seaweed_noise + seaweed_tint → seaweed_mat → seaweed_xform
  bubble_merge + fish_position → tank_scene (over, size=input1)
  fish_plate → fish_position
  tank_scene → installation_out

Also sets bubble_level opacity expression (audio-reactive; requires audio_analyze + mic).
"""
import td

I = op("/project1/fish_tank_install")
if not I:
    raise RuntimeError("Missing /project1/fish_tank_install")

def _req(name):
    o = I.op(name)
    if not o:
        raise RuntimeError("Missing OP: " + I.path + "/" + name)
    return o

tank_deep = _req("tank_deep")
sand_ramp = _req("sand_ramp")
sand_merge = _req("sand_merge")
seaweed_noise = _req("seaweed_noise")
seaweed_tint = _req("seaweed_tint")
seaweed_mat = _req("seaweed_mat")
seaweed_xform = _req("seaweed_xform")
env_base = _req("env_base")
water_caustic = _req("water_caustic")
water_over_bg = _req("water_over_bg")
bubble_merge = _req("bubble_merge")
bubble_level = _req("bubble_level")
bubble_noise = _req("bubble_noise")
tank_scene = _req("tank_scene")
fish_position = _req("fish_position")
installation_out = _req("installation_out")

seaweed_mat.inputConnectors[0].connect(seaweed_noise)
seaweed_mat.inputConnectors[1].connect(seaweed_tint)
try:
    seaweed_mat.par.operand = "multiply"
    seaweed_mat.par.size = "input1"
except Exception:
    pass

seaweed_xform.inputConnectors[0].connect(seaweed_mat)

sand_merge.inputConnectors[0].connect(tank_deep)
sand_merge.inputConnectors[1].connect(sand_ramp)
try:
    sand_merge.par.operand = "over"
    sand_merge.par.size = "input1"
except Exception:
    pass

env_base.inputConnectors[0].connect(sand_merge)
env_base.inputConnectors[1].connect(seaweed_xform)
try:
    env_base.par.operand = "over"
    env_base.par.size = "input1"
except Exception:
    pass

water_over_bg.inputConnectors[0].connect(env_base)
water_over_bg.inputConnectors[1].connect(water_caustic)
try:
    water_over_bg.par.operand = "add"
    water_over_bg.par.size = "input1"
except Exception:
    pass

bubble_level.inputConnectors[0].connect(bubble_noise)
bubble_merge.inputConnectors[0].connect(water_over_bg)
bubble_merge.inputConnectors[1].connect(bubble_level)
try:
    bubble_merge.par.operand = "over"
    bubble_merge.par.size = "input1"
except Exception:
    pass

tank_scene.inputConnectors[0].connect(bubble_merge)
tank_scene.inputConnectors[1].connect(fish_position)
try:
    tank_scene.par.operand = "over"
    tank_scene.par.size = "input1"
except Exception:
    pass

installation_out.inputConnectors[0].connect(tank_scene)

bl = bubble_level
bl.par.opacity.expr = (
    '0.2 + abs(op("/project1/fish_tank_install/audio_analyze")[0, 0] or 0) * 0.55'
)

print("OK:", I.path, "repaired")
