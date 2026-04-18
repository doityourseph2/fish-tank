import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";

type FishCanvasProps = {
  onImageChange: (dataUrl: string | null) => void;
};

const CANVAS_SIZE = 320;

export const FishCanvas = ({ onImageChange }: FishCanvasProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawing = useRef(false);
  const [hasInk, setHasInk] = useState(false);

  const emitSnapshot = useCallback(() => {
    const el = canvasRef.current;
    if (!el) {
      return;
    }
    setHasInk(true);
    onImageChange(el.toDataURL("image/png"));
  }, [onImageChange]);

  useEffect(() => {
    const el = canvasRef.current;
    if (!el) {
      return;
    }
    const ctx = el.getContext("2d");
    if (!ctx) {
      return;
    }
    ctx.fillStyle = "rgba(15, 23, 42, 0.95)";
    ctx.fillRect(0, 0, el.width, el.height);
    ctx.strokeStyle = "#f8fafc";
    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
  }, []);

  const posFromClient = (clientX: number, clientY: number) => {
    const el = canvasRef.current;
    if (!el) {
      return { x: 0, y: 0 };
    }
    const r = el.getBoundingClientRect();
    return { x: clientX - r.left, y: clientY - r.top };
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

  const handlePointerDown = (
    ev: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>,
  ) => {
    ev.preventDefault();
    drawing.current = true;
    const el = canvasRef.current;
    const ctx = el?.getContext("2d");
    if (!ctx) {
      return;
    }
    const { clientX, clientY } = clientCoords(ev);
    const { x, y } = posFromClient(clientX, clientY);
    ctx.beginPath();
    ctx.moveTo(x, y);
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
    if (!ctx) {
      return;
    }
    const { clientX, clientY } = clientCoords(ev);
    const { x, y } = posFromClient(clientX, clientY);
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const handlePointerUp = () => {
    if (drawing.current) {
      drawing.current = false;
      emitSnapshot();
    }
  };

  const handleClear = () => {
    const el = canvasRef.current;
    const ctx = el?.getContext("2d");
    if (!ctx || !el) {
      return;
    }
    ctx.fillStyle = "rgba(15, 23, 42, 0.95)";
    ctx.fillRect(0, 0, el.width, el.height);
    ctx.strokeStyle = "#f8fafc";
    setHasInk(false);
    onImageChange(null);
  };

  const handleKeyDown = (ev: KeyboardEvent<HTMLCanvasElement>) => {
    if (ev.key === "Escape") {
      handleClear();
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <canvas
        ref={canvasRef}
        width={CANVAS_SIZE}
        height={CANVAS_SIZE}
        role="img"
        aria-label="Draw your fish texture here. Use mouse or touch. Press Escape to clear."
        tabIndex={0}
        className="touch-none cursor-crosshair rounded-lg border border-slate-700 bg-slate-900 outline-none ring-cyan-500 focus:ring-2"
        onMouseDown={handlePointerDown}
        onMouseMove={handlePointerMove}
        onMouseUp={handlePointerUp}
        onMouseLeave={handlePointerUp}
        onTouchStart={handlePointerDown}
        onTouchMove={handlePointerMove}
        onTouchEnd={handlePointerUp}
        onKeyDown={handleKeyDown}
      />
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={handleClear}
          className="rounded-md border border-slate-600 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800"
        >
          Clear canvas
        </button>
        {!hasInk ? (
          <span className="text-sm text-slate-500">Draw something to enable submit.</span>
        ) : null}
      </div>
    </div>
  );
};
