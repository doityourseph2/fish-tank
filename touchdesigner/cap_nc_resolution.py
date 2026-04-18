"""
TouchDesigner Non-Commercial: keep every generating TOP at or below 1280×1280.

Run once in Textport after editing networks, or when you see resolution-limit warnings.

Edit W/H below if you standardize on a smaller canvas (e.g. 1024×576).
"""
import td

W, H = 1280, 720  # both dimensions ≤ 1280; 16×9 full-frame under the cap


def _cap(o):
    if not hasattr(o.par, "resolutionw"):
        return
    try:
        o.par.outputresolution = "custom"
    except Exception:
        pass
    o.par.resolutionw = W
    o.par.resolutionh = H


for container in (op("/project1/fish_tank_install"), op("/project1/fish_tank_poll")):
    if not container:
        continue
    for c in container.children:
        if c.OPType.endswith("TOP"):
            _cap(c)

mov = op("/project1/fish_tank_poll/fish_movie")
if mov:
    mov.par.outputresolution = "custom"
    mov.par.resolutionw = min(1024, W)
    mov.par.resolutionh = min(1024, H)

print("OK: capped TOPs to", W, "×", H, "(movie texture max 1024 for sampling)")
