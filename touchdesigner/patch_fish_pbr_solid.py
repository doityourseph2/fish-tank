# Run in TouchDesigner Textport (or MCP):
#   exec(open(r"/Users/seph/Desktop/FishTank/V1/fish-tank/touchdesigner/patch_fish_pbr_solid.py", encoding="utf-8").read())
#
# Makes fish_pbr_0..19 read more opaque: higher alpha test, full side alpha, no post-mult.

MAX = 20
P = op("/project1/fish_tank_poll")
if not P:
    raise RuntimeError("Missing /project1/fish_tank_poll")

# Raise for harder edges; lower (e.g. 0.12) if strokes look too “eaten”.
ALPHATEST_THRESHOLD = 0.28

for i in range(MAX):
    M = P.op("fish_pbr_%d" % i)
    if not M:
        print("skip missing:", "fish_pbr_%d" % i)
        continue
    M.par.alphathreshold = ALPHATEST_THRESHOLD
    try:
        M.par.alphaside = 1
    except Exception:
        pass
    try:
        M.par.postmultalpha = False
    except Exception:
        pass
    M.par.blending = False
    M.par.depthwriting = True
    print("OK", M.path)

# Legacy single material name
M1 = P.op("fish_pbr")
if M1:
    M1.par.alphathreshold = ALPHATEST_THRESHOLD
    try:
        M1.par.alphaside = 1
    except Exception:
        pass
    try:
        M1.par.postmultalpha = False
    except Exception:
        pass
    print("OK", M1.path)

print("Done: patch_fish_pbr_solid (threshold=%s)" % ALPHATEST_THRESHOLD)
