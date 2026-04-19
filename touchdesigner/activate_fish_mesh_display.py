"""
If fish_mesh_rig looks empty or fish_render is black: enable Display + Render on the
terminal material SOP (mat1). Run in Textport (or via MCP exec of this file).
"""
import td

G = op("/project1/fish_tank_poll/fish_mesh_rig")
if not G:
    raise RuntimeError("Missing fish_mesh_rig")

mat1 = G.op("mat1")
if not mat1:
    raise RuntimeError("Missing mat1 (material SOP)")

for ch in G.children:
    try:
        ch.display = ch == mat1
        ch.render = ch == mat1
    except Exception:
        pass

print("OK: display/render on", mat1.path)
