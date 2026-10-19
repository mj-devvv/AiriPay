const $ = (id) => document.getElementById(id);

const issueForm = $("issue-form");
const verifyForm = $("verify-form");
const statusLine = $("status");
let statusTimer;

function notify(message, tone = "info") {
  clearTimeout(statusTimer);
  statusLine.textContent = message;
  statusLine.dataset.tone = tone;
  statusLine.classList.add("visible");
  statusTimer = setTimeout(() => statusLine.classList.remove("visible"), 4000);
}

async function post(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function withLock(form, task) {
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    await task();
  } catch (error) {
    notify(error.message || "Local server unreachable", "error");
  } finally {
    button.disabled = false;
  }
}

issueForm.addEventListener("submit", (event) => {
  event.preventDefault();
  withLock(issueForm, async () => {
    const invoice = await post("/api/invoice", {
      merchant_id: $("merchant-id").value.trim(),
      amount: $("amount").value,
    });

    $("qr-image").src = invoice.qr;
    $("issued-at").textContent = invoice.issued_at;
    $("signature").textContent = invoice.signature;
    $("token").textContent = invoice.token;
    $("issue-result").classList.remove("hidden");
    notify("Token generated");
  });
});

$("copy-token").addEventListener("click", async () => {
  const token = $("token").textContent;
  try {
    await navigator.clipboard.writeText(token);
    notify("Token copied");
  } catch {
    notify("Copy failed, select the token manually", "error");
  }
});

function detailRow(label, value) {
  const row = document.createElement("div");
  const term = document.createElement("dt");
  const desc = document.createElement("dd");
  term.className = "label";
  desc.className = "mono";
  term.textContent = label;
  desc.textContent = value;
  row.append(term, desc);
  return row;
}

verifyForm.addEventListener("submit", (event) => {
  event.preventDefault();
  withLock(verifyForm, async () => {
    const result = await post("/api/verify", { token: $("verify-token").value });
    const panel = $("verify-result");
    const details = $("verdict-details");

    details.replaceChildren();
    panel.classList.remove("hidden");

    if (result.valid) {
      panel.dataset.state = "valid";
      $("verdict-label").textContent = "Valid";
      details.append(
        detailRow("Merchant", result.merchant_id),
        detailRow("Amount (NGN)", result.amount),
        detailRow("Issued", result.issued_at),
      );
      notify("Signature verified");
    } else {
      panel.dataset.state = "invalid";
      $("verdict-label").textContent = "Invalid";
      details.append(detailRow("Reason", result.reason));
      notify("Verification failed", "error");
    }
  });
});