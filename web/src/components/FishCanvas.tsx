import {
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faEraser,
  faFillDrip,
  faPaintbrush,
  faTrashCan,
  faUndo,
} from "@fortawesome/free-solid-svg-icons";
import {
  DEFAULT_FISH_BODY_ID,
  FISH_BODY_MODELS,
  getFishBodyModel,
  type FishBodyModel,
} from "../lib/fishBodyModels";

type FishCanvasProps = {
  onImageChange: (dataUrl: string | null) => void;
};

/** CSS pixels; backing store matches for predictable export size. */
const CANVAS_PX = 400;

const MAX_UNDO = 40;

type PaletteSwatch = { hex: string; label: string };

const PALETTE: readonly PaletteSwatch[] = [
  { hex: "#f8fafc", label: "Off white" },
  { hex: "#e2e8f0", label: "Light grey" },
  { hex: "#cbd5e1", label: "Grey" },
  { hex: "#94a3b8", label: "Slate" },
  { hex: "#fecaca", label: "Pale pink" },
  { hex: "#fda4af", label: "Pink" },
  { hex: "#fb7185", label: "Rose" },
  { hex: "#f43f5e", label: "Red pink" },
  { hex: "#fdba74", label: "Peach" },
  { hex: "#fb923c", label: "Orange" },
  { hex: "#fed7aa", label: "Apricot" },
  { hex: "#fde047", label: "Lemon" },
  { hex: "#facc15", label: "Yellow" },
  { hex: "#bef264", label: "Lime" },
  { hex: "#86efac", label: "Mint" },
  { hex: "#4ade80", label: "Green" },
  { hex: "#22c55e", label: "Emerald" },
  { hex: "#166534", label: "Forest" },
  { hex: "#5eead4", label: "Aqua" },
  { hex: "#2dd4bf", label: "Teal" },
  { hex: "#67e8f9", label: "Sky" },
  { hex: "#22d3ee", label: "Cyan" },
  { hex: "#38bdf8", label: "Light blue" },
  { hex: "#0ea5e9", label: "Blue" },
  { hex: "#0284c7", label: "Deep blue" },
  { hex: "#60a5fa", label: "Periwinkle" },
  { hex: "#1e40af", label: "Indigo" },
  { hex: "#0e7490", label: "Ocean teal" },
  { hex: "#a5b4fc", label: "Lilac" },
  { hex: "#c4b5fd", label: "Lavender" },
  { hex: "#e879f9", label: "Bright purple" },
  { hex: "#a855f7", label: "Purple" },
  { hex: "#000000", label: "Black" },
] as const;

const buildFishClipPath = (w: number, h: number, model: FishBodyModel): Path2D => {
  const { pathD, viewW, viewH } = model;
  const pad = 0.06;
  const maxW = w * (1 - 2 * pad);
  const maxH = h * (1 - 2 * pad);
  const s = Math.min(maxW / viewW, maxH / viewH);
  const ox = (w - viewW * s) / 2;
  const oy = (h - viewH * s) / 2;
  const unit = new Path2D(pathD);
  const out = new Path2D();
  out.addPath(unit, new DOMMatrix([s, 0, 0, s, ox, oy]));
  return out;
};

export const FishCanvas = ({ onImageChange }: FishCanvasProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fishClipRef = useRef<Path2D | null>(null);
  const drawing = useRef(false);
  const movedWhileDown = useRef(false);
  const lastRef = useRef<{ x: number; y: number } | null>(null);
  const [hasInk, setHasInk] = useState(false);
  const [brushColor, setBrushColor] = useState<string>(PALETTE[18].hex);
  const [brushSize, setBrushSize] = useState(10);
  const [tool, setTool] = useState<"brush" | "eraser">("brush");
  const [bodyModelId, setBodyModelId] = useState<string>(DEFAULT_FISH_BODY_ID);
  const [canUndo, setCanUndo] = useState(false);
  const undoStackRef = useRef<ImageData[]>([]);
  const bodyHeadingId = useId();
  const bodyHintId = useId();
  const coloursHeadingId = useId();
  const brushHeadingId = useId();
  const brushRangeId = useId();
  const paintIntroId = useId();
  const paintHelpId = useId();

  const activeModel = getFishBodyModel(bodyModelId);

  const emitSnapshot = useCallback(() => {
    const el = canvasRef.current;
    if (!el) {
      return;
    }
    const ctx = el.getContext("2d");
    if (!ctx) {
      return;
    }
    const { data } = ctx.getImageData(0, 0, el.width, el.height);
    let anyPixel = false;
    for (let i = 3; i < data.length; i += 4) {
      if (data[i] !== 0) {
        anyPixel = true;
        break;
      }
    }
    if (!anyPixel) {
      setHasInk(false);
      onImageChange(null);
      return;
    }
    setHasInk(true);
    onImageChange(el.toDataURL("image/png"));
  }, [onImageChange]);

  const pushUndoSnapshot = useCallback(() => {
    const el = canvasRef.current;
    const ctx = el?.getContext("2d");
    if (!el || !ctx) {
      return;
    }
    const snap = ctx.getImageData(0, 0, el.width, el.height);
    undoStackRef.current.push(snap);
    if (undoStackRef.current.length > MAX_UNDO) {
      undoStackRef.current.shift();
    }
    setCanUndo(true);
  }, []);

  const handleUndo = useCallback(() => {
    const el = canvasRef.current;
    const ctx = el?.getContext("2d");
    if (!el || !ctx) {
      return;
    }
    const stack = undoStackRef.current;
    if (stack.length === 0) {
      return;
    }
    const prev = stack.pop();
    if (!prev) {
      return;
    }
    ctx.putImageData(prev, 0, 0);
    setCanUndo(stack.length > 0);
    emitSnapshot();
  }, [emitSnapshot]);

  useEffect(() => {
    const el = canvasRef.current;
    if (!el) {
      return;
    }
    el.width = CANVAS_PX;
    el.height = CANVAS_PX;
    fishClipRef.current = buildFishClipPath(CANVAS_PX, CANVAS_PX, activeModel);
    const ctx = el.getContext("2d", { alpha: true });
    if (!ctx) {
      return;
    }
    ctx.clearRect(0, 0, el.width, el.height);
    undoStackRef.current = [];
    setCanUndo(false);
    setHasInk(false);
    onImageChange(null);
  }, [activeModel, onImageChange]);

  const posFromClient = (clientX: number, clientY: number) => {
    const el = canvasRef.current;
    if (!el) {
      return { x: 0, y: 0 };
    }
    const r = el.getBoundingClientRect();
    const scaleX = el.width / r.width;
    const scaleY = el.height / r.height;
    return {
      x: (clientX - r.left) * scaleX,
      y: (clientY - r.top) * scaleY,
    };
  };

  const clientCoords = (
    ev: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>,
  ) => {
    if ("touches" in ev && ev.touches.length > 0) {
      return { clientX: ev.touches[0].clientX, clientY: ev.touches[0].clientY };
    }
    const m = ev as React.MouseEvent<HTMLCanvasElement>;
    return { clientX: m.clientX, clientY: m.clientY };
  };

  const strokeSegment = (
    ctx: CanvasRenderingContext2D,
    x0: number,
    y0: number,
    x1: number,
    y1: number,
  ) => {
    const clip = fishClipRef.current;
    if (!clip) {
      return;
    }
    ctx.save();
    ctx.clip(clip);
    ctx.globalCompositeOperation =
      tool === "eraser" ? "destination-out" : "source-over";
    ctx.strokeStyle = tool === "eraser" ? "rgba(0,0,0,1)" : brushColor;
    ctx.lineWidth = brushSize;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
    ctx.restore();
  };

  const drawDot = (ctx: CanvasRenderingContext2D, x: number, y: number) => {
    const clip = fishClipRef.current;
    if (!clip) {
      return;
    }
    ctx.save();
    ctx.clip(clip);
    ctx.globalCompositeOperation =
      tool === "eraser" ? "destination-out" : "source-over";
    ctx.fillStyle = tool === "eraser" ? "#000" : brushColor;
    ctx.beginPath();
    ctx.arc(x, y, brushSize / 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  };

  const handlePointerDown = (
    ev: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>,
  ) => {
    ev.preventDefault();
    const el = canvasRef.current;
    const ctx = el?.getContext("2d");
    if (!ctx || !el) {
      return;
    }
    pushUndoSnapshot();
    drawing.current = true;
    movedWhileDown.current = false;
    const { clientX, clientY } = clientCoords(ev);
    const { x, y } = posFromClient(clientX, clientY);
    lastRef.current = { x, y };
  };

  const handlePointerMove = (
    ev: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>,
  ) => {
    if (!drawing.current) {
      return;
    }
    ev.preventDefault();
    const el = canvasRef.current;
    const ctx = el?.getContext("2d");
    if (!ctx || !lastRef.current) {
      return;
    }
    const { clientX, clientY } = clientCoords(ev);
    const { x, y } = posFromClient(clientX, clientY);
    const last = lastRef.current;
    movedWhileDown.current = true;
    strokeSegment(ctx, last.x, last.y, x, y);
    lastRef.current = { x, y };
  };

  const handlePointerUp = () => {
    if (!drawing.current) {
      return;
    }
    drawing.current = false;
    const el = canvasRef.current;
    const ctx = el?.getContext("2d");
    if (ctx && lastRef.current && !movedWhileDown.current) {
      const p = lastRef.current;
      drawDot(ctx, p.x, p.y);
    }
    lastRef.current = null;
    emitSnapshot();
  };

  const handleClear = () => {
    const el = canvasRef.current;
    const ctx = el?.getContext("2d");
    if (!ctx || !el) {
      return;
    }
    pushUndoSnapshot();
    ctx.clearRect(0, 0, el.width, el.height);
    setHasInk(false);
    onImageChange(null);
  };

  const handleFillFishBase = () => {
    const el = canvasRef.current;
    const ctx = el?.getContext("2d");
    const clip = fishClipRef.current;
    if (!ctx || !el || !clip) {
      return;
    }
    pushUndoSnapshot();
    setTool("brush");
    ctx.save();
    ctx.clip(clip);
    ctx.globalCompositeOperation = "source-over";
    ctx.fillStyle = brushColor;
    ctx.fillRect(0, 0, el.width, el.height);
    ctx.restore();
    emitSnapshot();
  };

  const handleKeyDown = (ev: KeyboardEvent<HTMLCanvasElement>) => {
    if (ev.key === "Escape") {
      handleClear();
      return;
    }
    if (ev.key.toLowerCase() === "z" && (ev.ctrlKey || ev.metaKey)) {
      ev.preventDefault();
      handleUndo();
    }
  };

  return (
    <div className="flex min-w-0 flex-col gap-4 text-white md:gap-6">
      <p
        id={paintIntroId}
        className="text-sm font-medium leading-relaxed text-white md:text-base"
      >
        Choose a body shape, then paint inside the light blue outline. Only that area is
        saved; the rest stays see-through in the tank.
      </p>
      <p id={paintHelpId} className="sr-only">
        Drawing surface: paint inside the fish outline. Press Escape to clear everything.
        When this area is focused, Control Z or Command Z undoes the last stroke.
      </p>

      <div className="grid min-w-0 grid-cols-1 gap-5 md:grid-cols-[minmax(0,1fr)_min(17.5rem,30vw)] md:items-start md:gap-6 lg:grid-cols-[minmax(0,1fr)_min(20rem,28vw)] lg:gap-8">
        <div className="flex min-w-0 flex-col gap-4 md:gap-5">
          <div className="relative mx-auto w-full max-w-[min(100%,420px)] md:mx-0 md:max-w-[min(100%,520px)] lg:max-w-none">
            <canvas
              ref={canvasRef}
              width={CANVAS_PX}
              height={CANVAS_PX}
              role="img"
              aria-label="Fish drawing area"
              aria-describedby={`${paintIntroId} ${paintHelpId}`}
              tabIndex={0}
              className="aspect-square h-auto w-full touch-none cursor-crosshair select-none rounded-md border-2 border-rule bg-[url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2210%22 height=%2210%22%3E%3Cpath fill=%22%230f3048%22 d=%22M0 0h5v5H0zm5 5h5v5H5z%22/%3E%3C/svg%3E')] outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-base"
              onMouseDown={handlePointerDown}
              onMouseMove={handlePointerMove}
              onMouseUp={handlePointerUp}
              onMouseLeave={handlePointerUp}
              onTouchStart={handlePointerDown}
              onTouchMove={handlePointerMove}
              onTouchEnd={handlePointerUp}
              onTouchCancel={handlePointerUp}
              onKeyDown={handleKeyDown}
            />
            <svg
              className="pointer-events-none absolute inset-0 h-full w-full"
              viewBox={`0 0 ${activeModel.viewW} ${activeModel.viewH}`}
              preserveAspectRatio="xMidYMid meet"
              aria-hidden
            >
              <path
                d={activeModel.pathD}
                fill="none"
                stroke="rgba(56, 189, 248, 0.85)"
                strokeWidth={2.25}
                vectorEffect="non-scaling-stroke"
              />
            </svg>
          </div>

          <div className="mx-auto flex w-full max-w-[min(100%,420px)] flex-col gap-3 md:mx-0 md:max-w-[min(100%,520px)] lg:max-w-none">
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={handleUndo}
                disabled={!canUndo}
                className="flex min-h-[48px] items-center justify-center gap-2 rounded-md border-2 border-rule bg-surface px-3 text-sm font-semibold text-white hover:bg-surface2 disabled:cursor-not-allowed disabled:opacity-40"
                aria-label="Undo last change"
              >
                <FontAwesomeIcon icon={faUndo} className="h-4 w-4 shrink-0" aria-hidden />
                Undo
              </button>
              <button
                type="button"
                onClick={handleClear}
                className="flex min-h-[48px] items-center justify-center gap-2 rounded-md border-2 border-rule bg-surface px-3 text-sm font-semibold text-white hover:bg-surface2"
                aria-label="Clear all paint from the canvas"
              >
                <FontAwesomeIcon icon={faTrashCan} className="h-4 w-4 shrink-0" aria-hidden />
                Clear
              </button>
            </div>
            <p className="text-sm leading-snug text-white/70">
              Tip: Tap the square above, then use{" "}
              <kbd className="rounded border border-white/25 bg-base px-1.5 py-0.5 font-mono text-xs text-white/90">
                Ctrl+Z
              </kbd>{" "}
              or{" "}
              <kbd className="rounded border border-white/25 bg-base px-1.5 py-0.5 font-mono text-xs text-white/90">
                ⌘Z
              </kbd>{" "}
              to undo.
            </p>
            {!hasInk ? (
              <p className="text-sm text-white/75" role="status">
                Add paint to turn on Send.
              </p>
            ) : null}
          </div>
        </div>

        <aside className="flex min-w-0 flex-col gap-6 rounded-xl border border-rule/80 bg-surface2/25 p-4 md:sticky md:top-4 md:z-10 md:max-h-[min(calc(100dvh-4rem),56rem)] md:gap-6 md:overflow-y-auto md:overflow-x-hidden md:overscroll-y-contain md:rounded-md md:border-rule md:bg-surface2/40 md:p-4 md:pt-5 lg:p-5">
          <div className="min-w-0">
            <h3 id={bodyHeadingId} className="text-base font-semibold text-ink">
              Body shape
            </h3>
            <p id={bodyHintId} className="mt-1 text-sm leading-snug text-white/80">
              Changing shape clears the canvas.
            </p>
            <div
              className="mt-3 grid grid-cols-3 gap-2 sm:grid-cols-6 md:grid-cols-2 lg:grid-cols-3"
              role="radiogroup"
              aria-labelledby={bodyHeadingId}
              aria-describedby={bodyHintId}
            >
              {FISH_BODY_MODELS.map((m) => {
                const selected = bodyModelId === m.id;
                return (
                  <button
                    key={m.id}
                    type="button"
                    role="radio"
                    aria-checked={selected}
                    aria-label={`${m.name}. ${m.description}`}
                    onClick={() => setBodyModelId(m.id)}
                    className={
                      selected
                        ? "flex min-h-[48px] flex-col items-center justify-center gap-1 rounded-md border-2 border-accent bg-surface p-2 text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-base"
                        : "flex min-h-[48px] flex-col items-center justify-center gap-1 rounded-md border-2 border-rule bg-base/80 p-2 text-white hover:border-white/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-base"
                    }
                  >
                    <svg
                      className="h-8 w-full text-ink2"
                      viewBox={`0 0 ${m.viewW} ${m.viewH}`}
                      aria-hidden
                    >
                      <path
                        d={m.pathD}
                        fill="currentColor"
                        fillOpacity={0.35}
                        stroke="rgba(56, 189, 248, 0.9)"
                        strokeWidth={2}
                        vectorEffect="non-scaling-stroke"
                      />
                    </svg>
                    <span className="text-center text-xs font-medium leading-tight">{m.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="min-w-0">
            <h3 id={coloursHeadingId} className="text-base font-semibold text-ink">
              Colours
            </h3>
            <div
              className="mt-3 grid grid-cols-6 gap-2.5 rounded-md border border-rule bg-base/50 p-2 sm:grid-cols-8 sm:gap-2 md:grid-cols-6 lg:grid-cols-8"
              role="group"
              aria-labelledby={coloursHeadingId}
            >
              {PALETTE.map((c) => {
                const selected = brushColor === c.hex && tool === "brush";
                return (
                  <button
                    key={c.hex}
                    type="button"
                    aria-label={`${c.label}. Set as paint colour.`}
                    aria-pressed={selected}
                    onClick={() => {
                      setTool("brush");
                      setBrushColor(c.hex);
                    }}
                    className={
                      selected
                        ? "aspect-square w-full max-h-[3rem] min-h-[48px] rounded-full border-2 border-white ring-2 ring-accent ring-offset-2 ring-offset-base focus-visible:outline-none sm:max-h-12 sm:min-h-[44px]"
                        : "aspect-square w-full max-h-[3rem] min-h-[48px] rounded-full border-2 border-rule hover:border-white/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-base sm:max-h-12 sm:min-h-[44px]"
                    }
                    style={{ backgroundColor: c.hex }}
                  />
                );
              })}
            </div>
          </div>

          <div className="min-w-0">
            <h3 id={brushHeadingId} className="text-base font-semibold text-ink">
              Brush
            </h3>
            <div className="mt-3 flex flex-col gap-4">
              <div>
                <label
                  htmlFor={brushRangeId}
                  className="block text-sm font-medium text-white/90"
                >
                  Thickness
                </label>
                <div className="mt-2 flex items-center gap-3">
                  <input
                    id={brushRangeId}
                    type="range"
                    min={2}
                    max={28}
                    value={brushSize}
                    onChange={(e) => setBrushSize(Number(e.target.value))}
                    className="brush-range min-h-[44px] min-w-0 flex-1 py-2"
                    aria-valuemin={2}
                    aria-valuemax={28}
                    aria-valuenow={brushSize}
                    aria-valuetext={`${brushSize} pixels`}
                  />
                  <span
                    className="flex h-11 min-w-[2.75rem] items-center justify-center rounded-md border border-rule bg-surface2 text-sm tabular-nums text-ink"
                    aria-hidden
                  >
                    {brushSize}
                  </span>
                </div>
              </div>

              <div
                className="flex min-h-[52px] rounded-md border-2 border-rule bg-base p-1"
                role="group"
                aria-labelledby={brushHeadingId}
              >
                <button
                  type="button"
                  aria-pressed={tool === "brush"}
                  onClick={() => setTool("brush")}
                  className={
                    tool === "brush"
                      ? "flex min-h-[44px] flex-1 items-center justify-center gap-2 rounded-[4px] bg-surface2 px-3 text-sm font-semibold text-white"
                      : "flex min-h-[44px] flex-1 items-center justify-center gap-2 rounded-[4px] px-3 text-sm text-white/75 hover:bg-surface2/60 hover:text-white"
                  }
                >
                  <FontAwesomeIcon icon={faPaintbrush} className="h-4 w-4 shrink-0" aria-hidden />
                  Paint
                </button>
                <button
                  type="button"
                  aria-pressed={tool === "eraser"}
                  onClick={() => setTool("eraser")}
                  className={
                    tool === "eraser"
                      ? "flex min-h-[44px] flex-1 items-center justify-center gap-2 rounded-[4px] bg-surface2 px-3 text-sm font-semibold text-white"
                      : "flex min-h-[44px] flex-1 items-center justify-center gap-2 rounded-[4px] px-3 text-sm text-white/75 hover:bg-surface2/60 hover:text-white"
                  }
                >
                  <FontAwesomeIcon icon={faEraser} className="h-4 w-4 shrink-0" aria-hidden />
                  Erase
                </button>
              </div>

              <button
                type="button"
                onClick={handleFillFishBase}
                className="flex min-h-[48px] w-full items-center justify-center gap-2 rounded-md border-2 border-accent/70 bg-surface2 px-4 text-sm font-semibold text-white hover:bg-surface2/90"
                aria-label={`Fill the whole fish with ${PALETTE.find((p) => p.hex === brushColor)?.label ?? "selected"} colour`}
              >
                <FontAwesomeIcon icon={faFillDrip} className="h-4 w-4 shrink-0 text-accent" aria-hidden />
                Fill fish
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
};
