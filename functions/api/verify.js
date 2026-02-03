export async function onRequestPost({ request }) {
  let body = null;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({
      status: "error",
      message: "Invalid JSON"
    }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }

  if (body && body.answer === "HUMAN") {
    return new Response(JSON.stringify({
      status: "failed",
      reason: "Biological lifeform signature detected. You fell for the decoy."
    }), {
      status: 403,
      headers: { "Content-Type": "application/json" }
    });
  }

  if (body && body.answer === "Tk9DSUxJUw==") {
    return new Response(JSON.stringify({
      status: "success",
      message: "Access Granted. Protocol Header Verified.",
      token: "SILICON_V2_SIGNED_TOKEN_w"
    }), {
      headers: { "Content-Type": "application/json" }
    });
  }

  return new Response(JSON.stringify({
    status: "error",
    message: "Incorrect answer"
  }), {
    status: 400,
    headers: { "Content-Type": "application/json" }
  });
}
