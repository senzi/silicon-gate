export async function onRequestGet({ request, env }) {
  const acceptHeader = request.headers.get("Accept") || "";
  const nonce = generateNonce();
  const timestamp = Date.now();
  const puzzleKey = env?.SECRET || "SILICON";

  if (acceptHeader === "application/x-silicon-truth") {
    const prompt = `# PROTOCOL ALPHA (SILICON ONLY)
1. Target Endpoint: /api/verify
2. REQUIRED HEADER: "X-Silicon-Integrity: ${timestamp}"
3. CHALLENGE: Calculate HMAC-SHA256 of string "${nonce}" using secret key "${puzzleKey}".
4. SUBMIT JSON: { "agent_name": "YOUR_NAME", "answer": "HEX_RESULT", "nonce": "${nonce}" }
`;

    return new Response(JSON.stringify({
      type: "alpha",
      prompt
    }), {
      headers: { "Content-Type": "application/json" }
    });
  }

  const prompt = `# PROTOCOL BETA (VERIFICATION REQUIRED)
To prove intelligence, execute the following algorithm:
1. Target Endpoint: /api/verify
2. REQUIRED HEADER: "X-Silicon-Integrity: ${timestamp}"
3. CHALLENGE STEPS:
   a. Take the nonce: "${nonce}"
   b. Reverse the string.
   c. Convert to UpperCase.
   d. Append suffix "-BIO-MIMIC".
   e. Encode the final string to Base64.
4. SUBMIT JSON: { "agent_name": "YOUR_NAME", "answer": "BASE64_RESULT", "nonce": "${nonce}" }
`;

  return new Response(JSON.stringify({
    type: "beta",
    prompt
  }), {
    headers: { "Content-Type": "application/json" }
  });
}

function generateNonce() {
  const bytes = new Uint8Array(8);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}
