"""
TouchDesigner Non-Commercial: keep every generating TOP at or below 1280×1280.

Run once in Textport after editing networks, or when you see resolution-limit warnings.

Edit W/H below if you standardize on a smaller canvas (e.g. 1024×576).
"""
import td

W, H = 1280, 720  # both dimensions ≤ 1280; 16×9 full-frame under the cap

# 20-fish school uses small tile TOPs; do not force them to full-frame.
_SKIP_POLL_TOP_PREFIXES = (
    "fish_render_",
    "fish_movie_",
    "fish_label_",
    "fish_cell_",
    "fish_slot_vis_",
)


def _should_skip_poll_top(name: str) -> bool:
    return any(name.startswith(p) for p in _SKIP_POLL_TOP_PREFIXES)


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
    is_poll = container.name == "fish_tank_poll"
    for c in container.children:
        if not c.OPType.endswith("TOP"):
            continue
        if is_poll and _should_skip_poll_top(c.name):
            continue
        _cap(c)

mov = op("/project1/fish_tank_poll/fish_movie")
if mov:
    mov.par.outputresolution = "custom"
    mov.par.resolutionw = min(1024, W)
    mov.par.resolutionh = min(1024, H)

for i in range(20):
    m = op(f"/project1/fish_tank_poll/fish_movie_{i}")
    if m:
        m.par.outputresolution = "custom"
        m.par.resolutionw = min(1024, W)
        m.par.resolutionh = min(1024, H)

print("OK: capped TOPs to", W, "×", H, "(movie texture max 1024; tile TOPs in fish_tank_poll skipped)")
