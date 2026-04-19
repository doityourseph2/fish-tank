# Run in TouchDesigner Textport (or MCP execute_python_script):
#   exec(open(r"/Users/seph/Desktop/FishTank/V1/fish-tank/touchdesigner/patch_fish_tr_swim.py", encoding="utf-8").read())
#
# Updates fish_tr_swim_* (tx/ty wobble), fish_mesh_rig_* (smooth 3D ry + S-wave pointSOP),
# removes fish_tr_face_* (TOP mirror) and rewires fish_render → fish_cell.

import td

MAX = 20
P = op("/project1/fish_tank_poll")
if not P:
    raise RuntimeError("Missing /project1/fish_tank_poll")


def _swim_tx_params(i):
    t = i / (MAX - 1) if MAX > 1 else 0.0
    f_tx = round(0.1 + t * 0.3, 4)
    ph_tx = round(0.1 + ((i * 3) % 20) / 19.0 * 0.3, 4)
    return f_tx, ph_tx


def _swim_tr_exprs(i):
    t = i / (MAX - 1) if MAX > 1 else 0.0
    f_tx, ph_tx = _swim_tx_params(i)
    f_ty = round(0.4 - t * 0.3, 4)
    ph_ty = round(0.1 + ((i * 7) % 20) / 19.0 * 0.3, 4)
    a_tx = round(0.1 + ((i * 2) % 20) / 19.0 * 0.3, 4)
    a_ty = round(0.1 + ((i * 5) % 20) / 19.0 * 0.3, 4)
    tx_e = "math.sin(absTime.seconds * %.4f + %.4f) * %.4f" % (f_tx, ph_tx, a_tx)
    ty_e = "math.cos(absTime.seconds * %.4f + %.4f) * %.4f" % (f_ty, ph_ty, a_ty)
    return tx_e, ty_e


def _swim_facing_ry_expr(i):
    f_tx, ph_tx = _swim_tx_params(i)
    return "90 * (1 - math.cos(absTime.seconds * %.4f + %.4f))" % (f_tx, ph_tx)


def _swim_wave_point_exprs(i):
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


def _ensure_swim_wave(G, i):
    pose = G.op("pose")
    swim = G.op("swim")
    if not pose or not swim:
        return False
    wave = G.op("swim_wave")
    sw_tx, sw_ty, sw_tz = _swim_wave_point_exprs(i)
    if not wave:
        wave = G.create(td.pointSOP, "swim_wave")
        try:
            swim.inputConnectors[0].disconnect()
        except Exception:
            pass
        wave.inputConnectors[0].connect(pose)
        swim.inputConnectors[0].connect(wave)
    else:
        try:
            wave.inputConnectors[0].connect(pose)
            swim.inputConnectors[0].connect(wave)
        except Exception:
            pass
    try:
        wave.par.tx.expr = sw_tx
        wave.par.ty.expr = sw_ty
        wave.par.tz.expr = sw_tz
    except Exception as ex:
        print(i, "swim_wave expr failed:", ex)
        return False
    try:
        swim.par.amp = 0.038
        swim.par.rough = 0.4
        swim.par.tz.expr = "absTime.seconds * 0.38 + %.4f" % (i * 0.15)
    except Exception:
        pass
    return True


for i in range(MAX):
    txe, tye = _swim_tr_exprs(i)
    ry_e = _swim_facing_ry_expr(i)

    rend = P.op("fish_render_%d" % i)
    cell = P.op("fish_cell_%d" % i)
    face = P.op("fish_tr_face_%d" % i)
    if cell and rend:
        try:
            cell.inputConnectors[0].connect(rend)
        except Exception as ex:
            print(i, "rewire cell failed:", ex)
    if face:
        try:
            face.destroy()
        except Exception as ex:
            print(i, "destroy face failed:", ex)

    rig = P.op("fish_mesh_rig_%d" % i)
    if rig:
        try:
            rig.par.ry.expr = ry_e
        except Exception as ex:
            print(i, "rig ry failed:", ex)
        print(i, "fish_mesh_rig ry:", ry_e)
        if _ensure_swim_wave(rig, i):
            print(i, "swim_wave OK")
        else:
            print(i, "swim_wave skip (missing pose/swim)")

    tr = P.op("fish_tr_swim_%d" % i)
    if tr:
        tr.par.tx.expr = txe
        tr.par.ty.expr = tye
        try:
            tr.par.sx.expr = ""
        except Exception:
            pass
        try:
            tr.par.sx = 1
        except Exception:
            pass
        print(i, "swim:", txe, "|", tye)

print("OK: swim + S-wave (swim_wave) + smooth 3D facing (fish_tr_face removed if present)")
