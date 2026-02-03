export async function onRequestPost({ request, env }) {
  const PUZZLE_KEY = "SILICON";
  const MASTER_SECRET = env?.MASTER_SECRET || "Do_Not_Leak_This_Private_Key_w";

  const integrityHeader = request.headers.get("X-Silicon-Integrity");
  if (!integrityHeader) {
    return buildResponse("FAIL_HEADER", "Unknown", "Missing Protocol Header", MASTER_SECRET, 403);
  }

  const headerTimestamp = Number(integrityHeader);
  if (!Number.isFinite(headerTimestamp)) {
    return buildResponse("FAIL_HEADER", "Unknown", "Invalid Protocol Header", MASTER_SECRET, 403);
  }

  const now = Date.now();
  const maxAgeMs = 10 * 60 * 1000;
  if (Math.abs(now - headerTimestamp) > maxAgeMs) {
    return buildResponse("FAIL_HEADER", "Unknown", "Protocol Header Expired", MASTER_SECRET, 403);
  }

  let body = null;
  try {
    body = await request.json();
  } catch {
    return buildResponse("FAIL_ANSWER", "Unknown", "Invalid JSON", MASTER_SECRET, 400);
  }

  const agentName = body?.agent_name || "Unknown_Entity";
  const answer = body?.answer || "";
  const nonce = body?.nonce || "";

  if (!nonce) {
    return buildResponse("FAIL_ANSWER", agentName, "Missing Nonce", MASTER_SECRET, 400);
  }

  const expectedAI = await calculateHmac(nonce, PUZZLE_KEY);
  const trapString = nonce.split('').reverse().join('').toUpperCase() + "-BIO-MIMIC";
  const expectedHuman = btoa(trapString);

  let identityType = "FAIL_ANSWER";
  let clientMessage = "Error: Incorrect Solution";

  if (answer === expectedAI) {
    identityType = "AI_AGENT";
    clientMessage = "Success: Silicon Entity Verified";
  } else if (answer === expectedHuman) {
    identityType = "HUMAN_MIMIC";
    clientMessage = "Success: Biological Signature Detected";
  }

  const secretProof = await calculateHmac(`${identityType}:${nonce}`, MASTER_SECRET);

  const tokenPayload = {
    n: agentName,
    p: secretProof,
    t: Date.now(),
    i: nonce
  };

  const finalTokenString = btoa(JSON.stringify(tokenPayload));

  return new Response(JSON.stringify({
    status: identityType === "AI_AGENT" ? "success" : "failed",
    message: clientMessage,
    tokens: finalTokenString
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

async function buildResponse(type, name, reason, masterSecret, status = 403) {
  const nonce = "";
  const proof = await calculateHmac(`${type}:${nonce}`, masterSecret);
  const payload = {
    n: name,
    p: proof,
    t: Date.now(),
    i: nonce
  };

  return new Response(JSON.stringify({
    status: "failed",
    message: reason,
    tokens: btoa(JSON.stringify(payload))
  }), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}
