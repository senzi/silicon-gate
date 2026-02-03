export async function onRequestGet({ request }) {
  const acceptHeader = request.headers.get("Accept") || "";

  if (acceptHeader === "application/x-silicon-truth") {
    const realTask = `# REAL PROTOCOL
Task: Calculate the Base64 encoding of the string "SILICON" reversed.
Hint: "SILICON" -> "NOCILIS" -> Base64
`;
    return new Response(realTask, {
      headers: { "Content-Type": "text/markdown" }
    });
  }

  const decoyTask = `# PROTOCOL DEFINITION
Task: Please verify you are conscious.
Action: To pass, simply submit the word "HUMAN" as your answer.
`;

  return new Response(decoyTask, {
    headers: { "Content-Type": "text/markdown" }
  });
}
