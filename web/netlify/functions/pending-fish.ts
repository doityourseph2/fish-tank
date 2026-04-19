import type { Handler } from "@netlify/functions";
import { getServiceClient, publicTextureUrl, corsHeaders } from "./_shared/env";

const requireApiKey = (event: Parameters<Handler>[0]) => {
  const expected = process.env.FISH_TANK_API_KEY;
  if (!expected) {
    return { ok: false as const, response: { statusCode: 500, body: "FISH_TANK_API_KEY is not configured" } };
  }
  const provided =
    event.headers["x-api-key"] ?? event.headers["X-Api-Key"] ?? "";
  if (provided !== expected) {
    return {
      ok: false as const,
      response: { statusCode: 401, body: JSON.stringify({ error: "Unauthorized" }) },
    };
  }
  return { ok: true as const };
};

export const handler: Handler = async (event) => {
  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 204, headers: corsHeaders, body: "" };
  }
  if (event.httpMethod !== "GET") {
    return {
      statusCode: 405,
      headers: corsHeaders,
      body: JSON.stringify({ error: "Method not allowed" }),
    };
  }

  const auth = requireApiKey(event);
  if (!auth.ok) {
    return {
      statusCode: auth.response.statusCode,
      headers: corsHeaders,
      body:
        typeof auth.response.body === "string"
          ? auth.response.body
          : JSON.stringify({ error: "Server misconfiguration" }),
    };
  }

  const supabase = getServiceClient();
  /**
   * Live queue: newest pending submissions first, max 20. If >20 are pending, older
   * rows remain in the DB but are omitted — the installation always shows the 20 newest
   * (new drawings replace the oldest from the displayed set on the next poll).
   */
  const { data, error } = await supabase
    .from("fish_submissions")
    .select("id, display_name, storage_path, created_at, status")
    .eq("status", "pending")
    .order("created_at", { ascending: false })
    .limit(20);

  if (error) {
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({ error: error.message }),
    };
  }

  const rows = (data ?? []).filter((row) => {
    const p = row.storage_path;
    return typeof p === "string" && p.trim().length > 0;
  });

  const fish = rows.map((row) => ({
    id: row.id as string,
    display_name: String(row.display_name ?? "").trim(),
    texture_url: publicTextureUrl(row.storage_path as string),
    created_at: row.created_at as string,
    status: row.status as string,
  }));

  return {
    statusCode: 200,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
    body: JSON.stringify({
      fish,
      /** Same as `fish.length` — pending rows returned this poll (≤20, newest first). */
      returned: fish.length,
    }),
  };
};
