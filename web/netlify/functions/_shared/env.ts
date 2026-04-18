import { createClient } from "@supabase/supabase-js";

export const getServiceClient = () => {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) {
    throw new Error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY");
  }
  return createClient(url, key);
};

export const publicTextureUrl = (storagePath: string) => {
  const base = process.env.SUPABASE_URL?.replace(/\/$/, "");
  if (!base) {
    throw new Error("Missing SUPABASE_URL");
  }
  const encoded = storagePath
    .split("/")
    .map((segment) => encodeURIComponent(segment))
    .join("/");
  return `${base}/storage/v1/object/public/fish-textures/${encoded}`;
};

export const corsHeaders: Record<string, string> = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type, x-api-key",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};
