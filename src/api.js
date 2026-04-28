async function parseResponse(response) {
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};

  if (!response.ok) {
    const detail = data.detail || data.message || response.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return data;
}

export async function apiGet(path) {
  const response = await fetch(path);
  return parseResponse(response);
}

export async function apiPost(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  return parseResponse(response);
}
