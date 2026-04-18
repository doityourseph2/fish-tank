import { useCallback, useId, useState } from "react";
import { FishCanvas } from "./components/FishCanvas";
import { submitFish } from "./lib/api";

export const App = () => {
  const nameId = useId();
  const fileId = useId();
  const [name, setName] = useState("");
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "err">("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [canvasKey, setCanvasKey] = useState(0);

  const handleImageChange = useCallback((dataUrl: string | null) => {
    setImageBase64(dataUrl);
  }, []);

  const handleFile = (ev: React.ChangeEvent<HTMLInputElement>) => {
    const file = ev.target.files?.[0];
    if (!file) {
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const r = reader.result;
      if (typeof r === "string") {
        setImageBase64(r);
        setMessage("Image loaded from file.");
      }
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (ev: React.FormEvent) => {
    ev.preventDefault();
    const trimmed = name.trim();
    if (trimmed.length < 1 || trimmed.length > 48) {
      setStatus("err");
      setMessage("Enter a name between 1 and 48 characters.");
      return;
    }
    if (!imageBase64) {
      setStatus("err");
      setMessage("Draw a fish or upload an image.");
      return;
    }
    setStatus("loading");
    setMessage(null);
    try {
      await submitFish(trimmed, imageBase64);
      setStatus("ok");
      setMessage("Saved. Your fish will appear in the tank shortly.");
      setName("");
      setImageBase64(null);
      setCanvasKey((k) => k + 1);
    } catch (e) {
      setStatus("err");
      setMessage(e instanceof Error ? e.message : "Something went wrong.");
    }
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-lg flex-col gap-8 px-4 py-10">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-50">
          Fish Tank
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Name your fish, draw a texture or upload an image, then send it to the
          live tank.
        </p>
      </header>

      <form onSubmit={handleSubmit} className="flex flex-col gap-6" noValidate>
        <div className="flex flex-col gap-2">
          <label htmlFor={nameId} className="text-sm font-medium text-slate-200">
            Fish name
          </label>
          <input
            id={nameId}
            name="displayName"
            type="text"
            maxLength={48}
            autoComplete="off"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="rounded-md border border-slate-600 bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-cyan-500 focus:ring-2"
            aria-required="true"
          />
        </div>

        <div className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-200">Texture</span>
          <FishCanvas key={canvasKey} onImageChange={handleImageChange} />
          <div className="flex flex-col gap-2">
            <label
              htmlFor={fileId}
              className="text-sm text-slate-400"
            >
              Or upload PNG / JPEG / WebP
            </label>
            <input
              id={fileId}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              onChange={handleFile}
              className="text-sm text-slate-300 file:mr-3 file:rounded file:border-0 file:bg-slate-700 file:px-3 file:py-1.5 file:text-slate-100"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={status === "loading" || !imageBase64}
          className="rounded-md bg-cyan-600 px-4 py-3 text-sm font-medium text-white hover:bg-cyan-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {status === "loading" ? "Sending…" : "Send to tank"}
        </button>
      </form>

      {message ? (
        <p
          role={status === "err" ? "alert" : "status"}
          className={
            status === "err" ? "text-sm text-rose-400" : "text-sm text-emerald-400"
          }
        >
          {message}
        </p>
      ) : null}
    </div>
  );
};
