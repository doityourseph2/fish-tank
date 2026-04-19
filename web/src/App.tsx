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
    <div className="mx-auto flex min-h-[100dvh] w-full max-w-lg flex-col gap-5 px-4 pb-6 safe-pb safe-pt sm:gap-6 sm:px-5 sm:py-8 md:max-w-5xl md:gap-8 md:px-6 md:py-8 lg:px-8">
      <header className="shrink-0 space-y-1">
        <p className="text-xs text-ink3">Live display</p>
        <div className="flex items-start gap-3">
          <span
            className="flex h-12 w-12 shrink-0 items-center justify-center rounded-md border-2 border-accent/50 bg-surface2 text-accent"
            aria-hidden
          >
            <FontAwesomeIcon icon={faFish} className="h-6 w-6" />
          </span>
          <div>
            <h1 className="text-2xl font-bold leading-tight text-ink sm:text-3xl">
              Fish Tank
            </h1>
            <p className="mt-1 text-base leading-relaxed text-ink2">
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
              <label htmlFor={nameId} className="text-sm font-medium text-ink">
                What should we call your fish?
              </label>
              <input
                id={nameId}
                name="displayName"
                type="text"
                maxLength={48}
                autoComplete="off"
                enterKeyHint="done"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="min-h-[48px] w-full rounded-md border-2 border-rule bg-base px-3 py-3 text-base text-ink placeholder:text-ink3/60 focus:border-accent focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-base sm:min-h-[44px]"
                placeholder="For example, Bubbles"
                aria-required="true"
              />
            </div>
          </Panel>

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
        </form>

        {message ? (
          <p
            role={status === "err" ? "alert" : "status"}
            className={
              status === "err"
                ? "mt-2 flex select-text items-start gap-2 text-base leading-relaxed text-danger"
                : "mt-2 flex select-text items-start gap-2 text-base leading-relaxed text-success"
            }
          >
            <FontAwesomeIcon
              icon={status === "err" ? faTriangleExclamation : faCircleCheck}
              className="mt-0.5 h-5 w-5 shrink-0"
              aria-hidden
            />
            <span>{message}</span>
          </p>
        ) : null}
      </main>
    </div>
  );
};
