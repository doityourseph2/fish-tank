import type { Handler } from "@netlify/functions";
import { getServiceClient, corsHeaders } from "./_shared/env";

type Body = { id?: string; ids?: string[] };

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
  if (event.httpMethod !== "POST") {
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

  let body: Body;
  try {
    body = JSON.parse(event.body || "{}") as Body;
  } catch {
    return {
      statusCode: 400,
      headers: corsHeaders,
      body: JSON.stringify({ error: "Invalid JSON body" }),
    };
  }

  const ids: string[] = [];
  if (Array.isArray(body.ids)) {
    for (const raw of body.ids) {
      if (typeof raw === "string") {
        const t = raw.trim();
        if (t.length > 0) {
          ids.push(t);
        }
      }
    }
  }
  if (ids.length === 0 && typeof body.id === "string") {
    const t = body.id.trim();
    if (t.length > 0) {
      ids.push(t);
    }
  }

  if (ids.length === 0) {
    return {
      statusCode: 400,
      headers: corsHeaders,
      body: JSON.stringify({ error: "id or ids[] is required" }),
    };
  }

  if (ids.length > 64) {
    return {
      statusCode: 400,
      headers: corsHeaders,
      body: JSON.stringify({ error: "Too many ids (max 64)" }),
    };
  }

  const supabase = getServiceClient();
  const { data, error } = await supabase
    .from("fish_submissions")
    .update({
      status: "consumed",
      consumed_at: new Date().toISOString(),
    })
    .in("id", ids)
    .eq("status", "pending")
    .select("id");

  if (error) {
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({ error: error.message }),
    };
  }

  const updated = (data ?? []).map((row) => row.id as string);

  return {
    statusCode: 200,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
    body: JSON.stringify({ ok: true, ids: updated, count: updated.length }),
  };
};
