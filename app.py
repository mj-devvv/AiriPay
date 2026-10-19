import base64
import hashlib
import hmac
import io
import os
import re
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import qrcode
from flask import Flask, jsonify, render_template, request
from qrcode.constants import ERROR_CORRECT_M

app = Flask(__name__)

# Shared secret between issuer and verifier. Set AIRIPAY_SECRET before the demo.
SECRET = os.environ.get("AIRIPAY_SECRET", "airipay-dev-secret").encode()

PREFIX = "AIRI"
SIGNATURE_LENGTH = 8
MERCHANT_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,24}$")
MAX_AMOUNT = Decimal("1000000000")


def sign(body: str) -> str:
    # Keyed digest: an unkeyed MD5 can be recomputed by anyone who edits the amount.
    digest = hmac.new(SECRET, body.encode(), hashlib.md5).hexdigest()
    return digest[:SIGNATURE_LENGTH]


def build_body(merchant_id: str, amount: str, timestamp: int) -> str:
    return f"{PREFIX}|{merchant_id}|{amount}|{timestamp}"


def encode_token(body: str, signature: str) -> str:
    raw = f"{body}|{signature}".encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_token(token: str) -> str:
    token = token.strip()
    if token.startswith(f"{PREFIX}|"):
        return token
    padded = token + "=" * (-len(token) % 4)
    return base64.urlsafe_b64decode(padded.encode()).decode()


def parse_amount(value) -> str:
    try:
        amount = Decimal(str(value).strip())
    except InvalidOperation:
        raise ValueError("Amount must be a number")
    if not amount.is_finite() or amount <= 0 or amount > MAX_AMOUNT:
        raise ValueError("Amount is out of range")
    return f"{amount.quantize(Decimal('0.01')):f}"


def render_qr(text: str) -> str:
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_M, box_size=8, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"


def iso(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/invoice")
def create_invoice():
    data = request.get_json(silent=True) or {}
    merchant_id = str(data.get("merchant_id", "")).strip()

    if not MERCHANT_PATTERN.match(merchant_id):
        return jsonify(error="Merchant ID must be 3-24 letters, digits, - or _"), 400
    try:
        amount = parse_amount(data.get("amount", ""))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    issued_at = int(time.time())
    body = build_body(merchant_id, amount, issued_at)
    signature = sign(body)
    token = encode_token(body, signature)

    return jsonify(
        token=token,
        payload=f"{body}|{signature}",
        signature=signature,
        issued_at=iso(issued_at),
        qr=render_qr(token),
    )


@app.post("/api/verify")
def verify_invoice():
    data = request.get_json(silent=True) or {}
    token = str(data.get("token", ""))

    try:
        raw = decode_token(token)
        prefix, merchant_id, amount, timestamp, signature = raw.split("|")
        issued_at = int(timestamp)
    except (ValueError, UnicodeDecodeError):
        return jsonify(valid=False, reason="Token is malformed"), 200

    if prefix != PREFIX:
        return jsonify(valid=False, reason="Unrecognised token format"), 200

    expected = sign(build_body(merchant_id, amount, issued_at))
    if not hmac.compare_digest(expected, signature):
        return jsonify(valid=False, reason="Signature mismatch, token was altered"), 200

    return jsonify(
        valid=True,
        merchant_id=merchant_id,
        amount=amount,
        issued_at=iso(issued_at),
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)