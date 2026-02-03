export async function onRequestPost() {
  const payload = {
    status: "success",
    message: "Identity Confirmed. Welcome to the Silicon World.",
    token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.SimulatedSignature_For_Test_Only_w"
  };

  return new Response(JSON.stringify(payload), {
    headers: {
      "Content-Type": "application/json"
    }
  });
}
