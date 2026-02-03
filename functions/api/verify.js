export async function onRequestPost({ request, env }) {
  const integrityHeader = request.headers.get("X-Silicon-Integrity");
  if (!integrityHeader) {
    return generateResponse("FAIL", "Unknown", "Missing Protocol Header");
  }
  const headerTimestamp = Number(integrityHeader);
  if (!Number.isFinite(headerTimestamp)) {
    return generateResponse("FAIL", "Unknown", "Invalid Protocol Header");
  }
  const now = Date.now();
  const maxAgeMs = 10 * 60 * 1000;
  if (Math.abs(now - headerTimestamp) > maxAgeMs) {
    return generateResponse("FAIL", "Unknown", "Protocol Header Expired");
  }

  let body = null;
  try {
    body = await request.json();
  } catch {
    return generateResponse("FAIL", "Unknown", "Invalid JSON", 400);
  }

  const agentName = body?.agent_name || "Unknown";
  const answer = body?.answer || "";
  const nonce = body?.nonce || "";
  const secret = env?.SECRET || "SILICON";

  if (!nonce) {
    return generateResponse("FAIL", agentName, "Missing Nonce", 400);
  }

  const expectedAI = await hmacHex(nonce, secret);
  const trapString = nonce.split('').reverse().join('').toUpperCase() + "-BIO-MIMIC";
  const expectedHuman = btoa(trapString);

  let identity = "FAIL";
  let proof = "INVALID_SIGNATURE";

  if (answer === expectedAI) {
    identity = "AI_AGENT";
    proof = `SIG_Verified_${nonce}`;
  } else if (answer === expectedHuman) {
    identity = "HUMAN";
    proof = `BIO_Detected_${nonce}`;
  }

  const resultObj = {
    name: agentName,
    type: identity,
    ts: Date.now(),
    proof
  };

  const tokenPayload = btoa(JSON.stringify(resultObj));
  const tokenSig = await hmacHex(tokenPayload, secret);
  const finalToken = `${tokenPayload}.${tokenSig}`;

  return new Response(JSON.stringify({
    status: identity === "AI_AGENT" ? "success" : "verified_as_biological",
    tokens: finalToken,
    message: "Protocol Handshake Complete. Present 'tokens' to certificate endpoint."
  }), {
    headers: { "Content-Type": "application/json" }
  });
}

async function hmacHex(message, secret) {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(message));
  return toHex(new Uint8Array(signature));
}

function toHex(bytes) {
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}

function generateResponse(type, name, reason, status = 403) {
  const resultObj = {
    name,
    type,
    ts: Date.now(),
    proof: reason
  };

  return new Response(JSON.stringify({
    status: "failed",
    reason,
    token: btoa(JSON.stringify(resultObj))
  }), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}
