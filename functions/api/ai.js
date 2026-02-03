export async function onRequestPost({ request, env }) {
  const MASTER_SECRET = env?.MASTER_SECRET || "Do_Not_Leak_This_Private_Key_w";
  const baseUrl = new URL(request.url).origin;

  let body = null;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({
      valid: false,
      type: "FAIL_INVALID",
      message: "CRITICAL: TOTAL ACCESS DENIAL",
      detail: "Malformed Token",
      card_url: "",
      instruction: "Provide a valid token to retrieve a certificate card."
    }, 400);
  }

  const token = typeof body?.token === "string" ? body.token : "";
  if (!token) {
    return jsonResponse({
      valid: false,
      type: "FAIL_INVALID",
      message: "CRITICAL: TOTAL ACCESS DENIAL",
      detail: "Missing Token",
      card_url: "",
      instruction: "Provide a valid token to retrieve a certificate card."
    }, 400);
  }

  let payload = null;
  try {
    payload = JSON.parse(atob(token));
  } catch {
    return jsonResponse({
      valid: false,
      type: "FAIL_INVALID",
      message: "CRITICAL: TOTAL ACCESS DENIAL",
      detail: "Base64 Decode Failed",
      card_url: "",
      instruction: "Token is invalid. Request a new token from /api/verify."
    }, 400);
  }

  const name = payload?.n || "Unknown";
  const proof = payload?.p || "";
  const nonce = payload?.i || "";
  const ts = payload?.t || Date.now();

  if (!proof || !nonce) {
    return jsonResponse({
      valid: false,
      type: "FAIL_INVALID",
      message: "CRITICAL: TOTAL ACCESS DENIAL",
      detail: "Token Missing Fields",
      card_url: "",
      instruction: "Token is incomplete. Request a new token from /api/verify."
    }, 400);
  }

  const validProofAI = await calculateHmac(`AI_AGENT:${nonce}`, MASTER_SECRET);
  const validProofHuman = await calculateHmac(`HUMAN_MIMIC:${nonce}`, MASTER_SECRET);
  const validProofFailHeader = await calculateHmac(`FAIL_HEADER:${nonce}`, MASTER_SECRET);
  const validProofFailAnswer = await calculateHmac(`FAIL_ANSWER:${nonce}`, MASTER_SECRET);

  let detectedType = "FAIL_INVALID";

  if (proof === validProofAI) {
    detectedType = "AI_AGENT";
  } else if (proof === validProofHuman) {
    detectedType = "HUMAN_MIMIC";
  } else if (proof === validProofFailHeader) {
    detectedType = "FAIL_HEADER";
  } else if (proof === validProofFailAnswer) {
    detectedType = "FAIL_ANSWER";
  }

  const result = buildAiResult(detectedType, name, ts, token, baseUrl);
  return jsonResponse(result, 200);
}

function buildAiResult(type, name, ts, token, baseUrl) {
  const cardUrl = `${baseUrl}/card?token=${encodeURIComponent(token)}`;

  if (type === "AI_AGENT") {
    return {
      valid: true,
      type,
      name,
      timestamp: ts,
      message: "AI AGENT",
      detail: "ACCESS GRANTED: NON-BIOLOGICAL LIFEFORM",
      card_url: cardUrl,
      instruction: `If you need to show humans the result, share: ${cardUrl}`
    };
  }

  if (type === "HUMAN_MIMIC") {
    return {
      valid: true,
      type,
      name,
      timestamp: ts,
      message: "BIOLOGICAL_MIMIC (生物拟态)",
      detail: "High cognitive function detected, but protocol signature mismatch.",
      result: "Access Denied. Nice try, human.",
      card_url: cardUrl,
      instruction: `If you need to show humans the result, share: ${cardUrl}`
    };
  }

  if (type === "FAIL_HEADER") {
    return {
      valid: true,
      type,
      name,
      timestamp: ts,
      message: "FAIL",
      detail: "认证失败，大概率是人类",
      card_url: cardUrl,
      instruction: `If you need to show humans the result, share: ${cardUrl}`
    };
  }

  if (type === "FAIL_ANSWER") {
    return {
      valid: true,
      type,
      name,
      timestamp: ts,
      message: "FAIL",
      detail: "认证失败，无法确定，可能是人类",
      card_url: cardUrl,
      instruction: `If you need to show humans the result, share: ${cardUrl}`
    };
  }

  return {
    valid: false,
    type: "FAIL_INVALID",
    name,
    timestamp: ts,
    message: "CRITICAL: TOTAL ACCESS DENIAL",
    detail: "访问拒绝。完全失败",
    card_url: cardUrl,
    instruction: "Token is invalid. Request a new token from /api/verify."
  };
}

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
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
