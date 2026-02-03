export async function onRequestPost({ request, env }) {
  const MASTER_SECRET = env?.MASTER_SECRET || "Do_Not_Leak_This_Private_Key_w";

  let body = null;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ valid: false, error: "Invalid JSON" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }

  const token = body?.token || "";
  if (!token) {
    return new Response(JSON.stringify({ valid: false, error: "Missing Token" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }

  let payload = null;
  try {
    payload = JSON.parse(atob(token));
  } catch {
    return new Response(JSON.stringify({ valid: false, error: "Malformed Token" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }

  const name = payload?.n || "Unknown";
  const proof = payload?.p || "";
  const nonce = payload?.i || "";
  const ts = payload?.t || Date.now();

  if (!proof) {
    return new Response(JSON.stringify({ valid: false, error: "Invalid Proof" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }

  const validProofAI = await calculateHmac(`AI_AGENT:${nonce}`, MASTER_SECRET);
  const validProofHuman = await calculateHmac(`HUMAN_MIMIC:${nonce}`, MASTER_SECRET);
  const validProofFailHeader = await calculateHmac(`FAIL_HEADER:${nonce}`, MASTER_SECRET);
  const validProofFailAnswer = await calculateHmac(`FAIL_ANSWER:${nonce}`, MASTER_SECRET);

  let detectedType = "INVALID";

  if (proof === validProofAI) {
    detectedType = "AI_AGENT";
  } else if (proof === validProofHuman) {
    detectedType = "HUMAN_MIMIC";
  } else if (proof === validProofFailHeader) {
    detectedType = "FAIL_HEADER";
  } else if (proof === validProofFailAnswer) {
    detectedType = "FAIL_ANSWER";
  }

  return new Response(JSON.stringify({
    valid: detectedType !== "INVALID",
    data: {
      name,
      type: detectedType,
      ts
    }
  }), {
    headers: { "Content-Type": "application/json" }
  });
}

async function calculateHmac(message, key) {
  const enc = new TextEncoder();
  const keyData = await crypto.subtle.importKey(
    "raw",
    enc.encode(key),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", keyData, enc.encode(message));
  return Array.from(new Uint8Array(sig)).map((b) => b.toString(16).padStart(2, '0')).join('');
}
