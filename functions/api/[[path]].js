const BACKEND_ORIGIN = "https://crisisflow-backend-556676992179.us-central1.run.app";

export async function onRequest({ request, params }) {
  const path = Array.isArray(params.path) ? params.path.join("/") : params.path || "";
  const sourceUrl = new URL(request.url);
  const targetUrl = new URL(`/api/${path}`, BACKEND_ORIGIN);
  targetUrl.search = sourceUrl.search;

  const headers = new Headers(request.headers);
  headers.set("host", new URL(BACKEND_ORIGIN).host);

  return fetch(targetUrl, {
    method: request.method,
    headers,
    body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
    redirect: "manual",
  });
}
