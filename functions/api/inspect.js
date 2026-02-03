export async function onRequestPost({ request, env }) {
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
  if (!token || !token.includes('.')) {
    return new Response(JSON.stringify({ valid: false, error: "Missing Token" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }

  const secret = env?.SECRET || "SILICON";
  const [payload, sig] = token.split('.');

  const expectedSig = await hmacHex(payload, secret);
  if (sig !== expectedSig) {
    return new Response(JSON.stringify({ valid: false, error: "Tampered Token" }), {
      status: 403,
      headers: { "Content-Type": "application/json" }
    });
  }

  let data = null;
  try {
    data = JSON.parse(atob(payload));
  } catch {
    return new Response(JSON.stringify({ valid: false, error: "Invalid Payload" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }

  return new Response(JSON.stringify({
    valid: true,
    data
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
