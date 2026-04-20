"""
Build up to 20 concurrent 3D fish in /project1/fish_tank_poll:

  fish_movie_i → fish_matalpha_i (Reorder: PNG alpha → red) → fish_pbr_i → fish_mesh_rig_i (smooth Y spin for turn)
    → fish_render_i (256×180) + fish_label_i → fish_cell_i → fish_slot_vis_i (Level) → swim → grid position
  Stack all cells with over onto a transparent 1280×720 canvas → fish_out

Paste into Textport (or exec this file). Destroys prior fish_* nodes except
fish_out, fish_comp, netlify_config, poll_*, debug_status, apply_fish_display, null1.

Then reload apply_fish_display Text DAT from disk and run repair if needed.

Swim motion: UUID → one light scalar swim_<slot>_tune on TOP/COMP parms only (cheap).
Body wave + noise SOP stay constant expressions (no per-vertex fetch — was very heavy).
"""
import td

MAX = 20
CELL_W = 256
CELL_H = 180
COLS = 5

P = op("/project1/fish_tank_poll")
if not P:
    raise RuntimeError("Missing /project1/fish_tank_poll")

KEEP = {
    "netlify_config",
    "poll_pending_fish",
    "poll_lfo",
    "poll_chopexec",
    "debug_status",
    "apply_fish_display",
    "null1",
    "fish_out",
}

for c in list(P.children):
    if c.name in KEEP:
        continue
    if c.name.startswith("fish"):
        c.destroy()


def _strip_toruses(G):
    for ch in list(G.children):
        if ch.name.startswith("torus") or "torus" in ch.OPType.lower():
            ch.destroy()


def _swim_tx_params(i):
    """Frequency + phase shared by 2D swim wobble and 3D facing spin."""
    t = i / (MAX - 1) if MAX > 1 else 0.0
    f_tx = round(0.1 + t * 0.3, 4)
    ph_tx = round(0.1 + ((i * 3) % 20) / 19.0 * 0.3, 4)
    return f_tx, ph_tx


def _swim_tr_exprs(i):
    """Per-slot tx/ty for fish_tr_swim_i. One fetch('tune') per line — evaluates once per TOP cook."""
    t = i / (MAX - 1) if MAX > 1 else 0.0
    f_tx, ph_tx = _swim_tx_params(i)
    f_ty = round(0.4 - t * 0.3, 4)
    ph_ty = round(0.1 + ((i * 7) % 20) / 19.0 * 0.3, 4)
    a_tx = round(0.1 + ((i * 2) % 20) / 19.0 * 0.3, 4)
    a_ty = round(0.1 + ((i * 5) % 20) / 19.0 * 0.3, 4)
    tx_e = (
        "math.sin(absTime.seconds * %.4f * float(parent().fetch('swim_%d_tune','1')) + %.4f) * %.4f"
        % (f_tx, i, ph_tx, a_tx)
    )
    ty_e = (
        "math.cos(absTime.seconds * %.4f * float(parent().fetch('swim_%d_tune','1')) + %.4f) * %.4f"
        % (f_ty, i, ph_ty, a_ty)
    )
    return tx_e, ty_e


def _swim_facing_ry_expr(i):
    """
    Smooth Y rotation on fish_mesh_rig (degrees), same phase as tile tx wobble.
    tx = sin(w*t+p) → velocity ∝ cos(w*t+p). Map cos from [1,-1] → ry [0,180] via
    ry = 90*(1-cos) so the fish eases through ~90° at each direction change instead of snapping.
    Textures are head +X at ry=0; ry=180 faces -X.
    """
    f_tx, ph_tx = _swim_tx_params(i)
    return (
        "90 * (1 - math.cos(absTime.seconds * %.4f * float(parent().fetch('swim_%d_tune','1')) + %.4f))"
        % (f_tx, i, ph_tx)
    )


def _swim_wave_point_exprs(i):
    """
    Traveling body wave (S-shaped) on the grid: sin(2π·k·u - ωt) using texture U along length.
    No storage fetch here — expressions run per point; keep math only.
    """
    ph = round(i * 0.47 + ((i * 5) % 11) * 0.09, 4)
    bodies = 1.22
    spd = 6.2
    ay = 0.005
    az = 0.0015
    tx_e = "me.inputPoint.x"
    ty_e = (
        "me.inputPoint.y + %.6f * math.sin(2 * math.pi * %.4f * me.inputTexture[0] - %.4f * absTime.seconds + %.4f)"
        % (ay, bodies, spd, ph)
    )
    tz_e = (
        "me.inputPoint.z + %.6f * math.cos(2 * math.pi * %.4f * me.inputTexture[0] - %.4f * absTime.seconds + %.4f)"
        % (az, bodies, spd, ph)
    )
    return tx_e, ty_e, tz_e


def _configure_fish_alpha_reorder(ro):
    """
    PBR MAT alphamap uses the **red** channel as opacity (not PNG alpha).
    Blue paint has low R → was treated as transparent. Map input alpha → output R.
    """
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


def _pbr_defaults(M, basecolor_path, alphamap_path):
    M.par.basecolormap = basecolor_path
    M.par.alphamap = alphamap_path
    M.par.alphamode = True
    M.par.pointcolorpremult = "premultinshader"
    M.par.alphatest = True
    M.par.alphafunc = "greater"
    # Higher = harder silhouette (less “see-through” fringe on soft PNG alpha). Tune 0.15–0.45.
    M.par.alphathreshold = 0.28
    # Was 0: side lighting made the fish read as thin/ghostly on the deformed grid.
    M.par.alphaside = 1
    try:
        M.par.postmultalpha = False
    except Exception:
        pass
    M.par.blending = False
    M.par.depthwriting = True
    M.par.roughness = 0.4
    M.par.metallic = 0


def build_slot(i):
    phase = i * 0.31

    mv = P.create(td.moviefileinTOP, "fish_movie_%d" % i)
    mv.par.outputresolution = "custom"
    mv.par.resolutionw = min(512, 256)
    mv.par.resolutionh = min(512, 256)
    mv.par.predownloadhttp = True
    # Still images from Supabase: lock to first frame (sequential can leave a bad index / black frame).
    mv.par.playmode = "specify"
    mv.par.indexunit = "indices"
    mv.par.index = 0
    # Empty path or failed decode: blank plate, not the red "failed" square in the corner.
    mv.par.loadingerrorimage = "zero"

    ro = P.create(td.reorderTOP, "fish_matalpha_%d" % i)
    ro.inputConnectors[0].connect(mv)
    _configure_fish_alpha_reorder(ro)

    M = P.create(td.pbrMAT, "fish_pbr_%d" % i)
    _pbr_defaults(
        M,
        P.path + "/fish_movie_%d" % i,
        P.path + "/fish_matalpha_%d" % i,
    )

    G = P.create(td.geometryCOMP, "fish_mesh_rig_%d" % i)
    G.par.tx.expr = (
        "math.sin(absTime.seconds * 0.7 + %.4f) * 0.12 * float(parent().fetch('swim_%d_tune','1'))"
        % (phase, i)
    )
    G.par.ty.expr = (
        "math.cos(absTime.seconds * 0.55 + %.4f) * 0.08 * float(parent().fetch('swim_%d_tune','1'))"
        % (phase, i)
    )
    G.par.ry.expr = _swim_facing_ry_expr(i)

    body = G.create(td.gridSOP, "body")
    body.par.rows = 20
    body.par.cols = 28

    pose = G.create(td.transformSOP, "pose")
    pose.inputConnectors[0].connect(body)
    pose.par.sx = 1.1
    pose.par.sy = 0.55
    pose.par.ry = 12

    swim_wave = G.create(td.pointSOP, "swim_wave")
    swim_wave.inputConnectors[0].connect(pose)
    sw_tx, sw_ty, sw_tz = _swim_wave_point_exprs(i)
    swim_wave.par.tx.expr = sw_tx
    swim_wave.par.ty.expr = sw_ty
    swim_wave.par.tz.expr = sw_tz

    swim = G.create(td.noiseSOP, "swim")
    swim.inputConnectors[0].connect(swim_wave)
    swim.par.type = "sparse"
    swim.par.amp = 0.038
    swim.par.period = 2.1
    swim.par.rough = 0.4
    swim.par.tz.expr = "absTime.seconds * 0.38 + %.4f" % (i * 0.15)

    mat1 = G.create(td.materialSOP, "mat1")
    mat1.inputConnectors[0].connect(swim)
    _strip_toruses(G)
    mat1.par.mat = M.path
    for ch in G.children:
        try:
            ch.display = ch == mat1
            ch.render = ch == mat1
        except Exception:
            pass

    cam = P.create(td.cameraCOMP, "fish_cam_%d" % i)
    cam.par.tz = 5

    lt = P.create(td.lightCOMP, "fish_light_%d" % i)

    rend = P.create(td.renderTOP, "fish_render_%d" % i)
    rend.par.camera = cam.path
    rend.par.geometry = G.path
    rend.par.lights = lt.path
    rend.par.rendermode = "render3d"
    rend.par.outputresolution = "custom"
    rend.par.resolutionw = CELL_W
    rend.par.resolutionh = CELL_H
    rend.par.bgcolora = 0

    lbl = P.create(td.textTOP, "fish_label_%d" % i)
    lbl.par.outputresolution = "custom"
    lbl.par.resolutionw = CELL_W
    lbl.par.resolutionh = CELL_H
    lbl.par.fontsizex = 11
    lbl.par.fontsizey = 11
    lbl.par.fontcolorr = 0.95
    lbl.par.fontcolorg = 0.97
    lbl.par.fontcolorb = 1
    lbl.par.aligny = "bottom"
    lbl.par.text = ""

    cell = P.create(td.compositeTOP, "fish_cell_%d" % i)
    cell.inputConnectors[0].connect(rend)
    cell.inputConnectors[1].connect(lbl)
    cell.par.operand = "over"
    cell.par.size = "input1"

    vis = P.create(td.levelTOP, "fish_slot_vis_%d" % i)
    vis.inputConnectors[0].connect(cell)
    vis.par.opacity = 0

    tr_sw = P.create(td.transformTOP, "fish_tr_swim_%d" % i)
    tr_sw.inputConnectors[0].connect(vis)
    _txe, _tye = _swim_tr_exprs(i)
    tr_sw.par.tx.expr = _txe
    tr_sw.par.ty.expr = _tye
    try:
        tr_sw.par.sx.expr = ""
    except Exception:
        pass
    tr_sw.par.sx = 1

    tr_gr = P.create(td.transformTOP, "fish_tr_grid_%d" % i)
    tr_gr.inputConnectors[0].connect(tr_sw)
    tr_gr.par.tx = (i % COLS) * CELL_W
    tr_gr.par.ty = (i // COLS) * CELL_H

    return tr_gr


ends = []
for i in range(MAX):
    ends.append(build_slot(i))

canv = P.create(td.constantTOP, "fish_school_canvas")
canv.par.outputresolution = "custom"
canv.par.resolutionw = 1280
canv.par.resolutionh = 720
canv.par.alpha = 0

cur = canv
for i in range(MAX):
    layer = P.create(td.compositeTOP, "fish_grid_layer_%d" % i)
    layer.inputConnectors[0].connect(cur)
    layer.inputConnectors[1].connect(ends[i])
    layer.par.operand = "over"
    layer.par.size = "input1"
    cur = layer

fo = P.op("fish_out")
if fo:
    fo.inputConnectors[0].connect(cur)

print("OK: 20 fish slots →", cur.path if cur else "?", "→ fish_out")
