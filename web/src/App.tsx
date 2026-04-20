import { useCallback, useId, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faCircleCheck,
  faFish,
  faPaperPlane,
  faSpinner,
  faTriangleExclamation,
} from "@fortawesome/free-solid-svg-icons";
import { FishCanvas } from "./components/FishCanvas";
import { Button } from "./components/ui/Button";
import { Panel } from "./components/ui/Panel";
import { submitFish } from "./lib/api";

export const App = () => {
  const paintHeadingId = useId();
  const nameId = useId();
  const [name, setName] = useState("");
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "err">("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [canvasKey, setCanvasKey] = useState(0);

  const handleImageChange = useCallback((dataUrl: string | null) => {
    setImageBase64(dataUrl);
  }, []);

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
      setMessage("Draw your fish in the canvas, then send.");
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

  const busy = status === "loading";

  const sendTitle =
    busy ? "Sending in progress." : !imageBase64 ? "Draw on the canvas first." : undefined;

  const sendAriaLabel = busy
    ? "Sending to tank, please wait"
    : !imageBase64
      ? "Send to tank — draw on the canvas first"
      : "Send to tank";

  return (
    <div className="mx-auto flex min-h-[100dvh] w-full max-w-lg flex-col gap-4 px-4 pb-28 safe-pb safe-pt sm:gap-6 sm:px-5 sm:py-8 sm:pb-6 md:max-w-5xl md:gap-8 md:px-6 md:py-8 lg:px-8">
      <header className="shrink-0 space-y-1">
        <p className="text-xs font-medium uppercase tracking-wide text-white/65">
          Live display
        </p>
        <div className="flex items-start gap-3">
          <span
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-md border-2 border-white/25 bg-surface2 text-white sm:h-12 sm:w-12"
            aria-hidden
          >
            <FontAwesomeIcon icon={faFish} className="h-5 w-5 sm:h-6 sm:w-6" />
          </span>
          <div className="min-w-0">
            <h1 className="text-[1.375rem] font-bold leading-tight text-white sm:text-3xl">
              Fish Tank
            </h1>
            <p className="mt-1 text-base leading-relaxed text-white/85">
              Draw a fish, name it, and send it to the tank.
            </p>
          </div>
        </div>
      </header>

      <main className="flex min-w-0 flex-1 flex-col">
        <form
          onSubmit={handleSubmit}
          className="flex min-w-0 flex-1 flex-col gap-5 sm:gap-6"
          noValidate
          aria-busy={busy}
          aria-label="Create and send your fish"
        >
          <Panel
            label="Paint"
            labelId={paintHeadingId}
            accent
            className="min-w-0 p-4 pt-6 sm:p-5 sm:pt-7"
          >
            <FishCanvas key={canvasKey} onImageChange={handleImageChange} />
          </Panel>

          <Panel label="Your name" className="p-4 pt-6 sm:p-5 sm:pt-7">
            <div className="flex flex-col gap-2">
              <label htmlFor={nameId} className="text-sm font-medium text-white">
                What should we call your fish?
              </label>
              <input
                id={nameId}
                name="displayName"
                type="text"
                maxLength={48}
                autoComplete="off"
                enterKeyHint="done"
                inputMode="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="min-h-[48px] w-full rounded-md border-2 border-rule bg-base px-3 py-3 text-base text-white placeholder:text-white/45 focus:border-accent focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-base sm:min-h-[44px]"
                placeholder="For example, Bubbles"
                aria-required="true"
              />
            </div>
          </Panel>

          {message ? (
            <p
              role={status === "err" ? "alert" : "status"}
              className="flex select-text items-start gap-2 text-base leading-relaxed text-white"
            >
              <FontAwesomeIcon
                icon={status === "err" ? faTriangleExclamation : faCircleCheck}
                className={
                  status === "err"
                    ? "mt-0.5 h-5 w-5 shrink-0 text-danger"
                    : "mt-0.5 h-5 w-5 shrink-0 text-success"
                }
                aria-hidden
              />
              <span>{message}</span>
            </p>
          ) : null}

          <div className="fixed inset-x-0 bottom-0 z-30 border-t border-white/10 bg-base/92 px-4 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-3 backdrop-blur-md supports-[backdrop-filter]:bg-base/80 sm:static sm:z-0 sm:border-0 sm:bg-transparent sm:p-0 sm:backdrop-blur-none">
            <div className="mx-auto w-full max-w-lg sm:max-w-none md:max-w-5xl">
              <Button
                type="submit"
                variant="primary"
                size="lg"
                fullWidth
                disabled={busy || !imageBase64}
                title={sendTitle}
                aria-label={sendAriaLabel}
              >
                {busy ? (
                  <>
                    <FontAwesomeIcon icon={faSpinner} spin className="h-4 w-4 shrink-0" aria-hidden />
                    <span>Sending…</span>
                  </>
                ) : (
                  <>
                    <FontAwesomeIcon icon={faPaperPlane} className="h-4 w-4 shrink-0" aria-hidden />
                    <span>Send to tank</span>
                  </>
                )}
              </Button>
            </div>
          </div>
        </form>
      </main>
    </div>
  );
};
