import type { Handler } from "@netlify/functions";
import { randomUUID } from "node:crypto";
import { getServiceClient, corsHeaders } from "./_shared/env";

type SubmitBody = {
  displayName?: string;
  imageBase64?: string;
};

const parseBase64Image = (raw: string) => {
  const trimmed = raw.trim();
  const dataUrl = trimmed.match(
    /^data:image\/(png|jpeg|webp);base64,(.+)$/i,
  );
  if (dataUrl) {
    const ext = dataUrl[1].toLowerCase() === "jpeg" ? "jpg" : dataUrl[1].toLowerCase();
    const buf = Buffer.from(dataUrl[2], "base64");
    return { buffer: buf, ext, mime: `image/${dataUrl[1].toLowerCase()}` };
  }
  const buf = Buffer.from(trimmed, "base64");
  return { buffer: buf, ext: "png", mime: "image/png" };
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

  let body: SubmitBody;
  try {
    body = JSON.parse(event.body || "{}") as SubmitBody;
  } catch {
    return {
      statusCode: 400,
      headers: corsHeaders,
      body: JSON.stringify({ error: "Invalid JSON body" }),
    };
  }

  const displayName = (body.displayName ?? "").trim();
  if (displayName.length < 1 || displayName.length > 48) {
    return {
      statusCode: 400,
      headers: corsHeaders,
      body: JSON.stringify({ error: "displayName must be 1–48 characters" }),
    };
  }

  if (!body.imageBase64) {
    return {
      statusCode: 400,
      headers: corsHeaders,
      body: JSON.stringify({ error: "imageBase64 is required" }),
    };
  }

  let image: { buffer: Buffer; ext: string; mime: string };
  try {
    image = parseBase64Image(body.imageBase64);
  } catch {
    return {
      statusCode: 400,
      headers: corsHeaders,
      body: JSON.stringify({ error: "Could not decode image" }),
    };
  }

  if (image.buffer.length < 32 || image.buffer.length > 2_097_152) {
    return {
      statusCode: 400,
      headers: corsHeaders,
      body: JSON.stringify({ error: "Image must be between 32 bytes and 2MB" }),
    };
  }

  const supabase = getServiceClient();
  const id = randomUUID();
  const storagePath = `pending/${id}.${image.ext}`;

  const { error: uploadError } = await supabase.storage
    .from("fish-textures")
    .upload(storagePath, image.buffer, {
      contentType: image.mime,
      upsert: false,
    });

  if (uploadError) {
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({ error: uploadError.message }),
    };
  }

  const { data: row, error: insertError } = await supabase
    .from("fish_submissions")
    .insert({
      id,
      display_name: displayName,
      storage_path: storagePath,
      status: "pending",
    })
    .select("id, display_name, storage_path, created_at")
    .single();

  if (insertError) {
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({ error: insertError.message }),
    };
  }

  return {
    statusCode: 200,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
    body: JSON.stringify({ ok: true, submission: row }),
  };
};
