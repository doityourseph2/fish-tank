const fnBase = () =>
  (import.meta.env.VITE_FUNCTIONS_ORIGIN ?? "").replace(/\/$/, "");

export const submitFish = async (displayName: string, imageBase64: string) => {
  const base = fnBase();
  const url = `${base}/.netlify/functions/submit-fish`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ displayName, imageBase64 }),
  });
  const text = await res.text();
  let data: unknown;
  try {
    data = JSON.parse(text) as unknown;
  } catch {
    throw new Error(text || `Request failed (${res.status})`);
  }
  if (!res.ok) {
    const err = data as { error?: string };
    throw new Error(err.error ?? `Request failed (${res.status})`);
  }
  return data as { ok: boolean; submission: Record<string, unknown> };
};
