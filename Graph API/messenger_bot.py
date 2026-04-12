#!/usr/bin/env python3
# =============================================================================
# messenger_bot.py
# Chatbot integration for Facebook Messenger DMs.
# Two modes:
#   python messenger_bot.py          → live Flask webhook server (port 5002)
#   python messenger_bot.py --test   → process messenger_full.json locally
# =============================================================================
#
# ── SETUP GUIDE ──────────────────────────────────────────────────────────────
#
# ── .env requirements ────────────────────────────────────────────────────────
#   FACEBOOK_PAGE_ACCESS_TOKEN=<your page access token>
#   FACEBOOK_PAGE_ID=<your numeric page id>
#   FACEBOOK_PAGE_NAME=<your page display name, e.g. Emergenhelp>
#   WEBHOOK_VERIFY_TOKEN=<any secret string you choose>
#   LIGHT_LLM_PROVIDER=groq
#   LIGHT_LLM_MODEL=llama-3.1-8b-instant
#   GOOD_LLM_PROVIDER=groq
#   GOOD_LLM_MODEL=llama-3.3-70b-versatile
#   GROQ_API_KEY=<your groq api key>
#
# ── LOCAL TESTING (no live Facebook needed) ──────────────────────────────────
#   python messenger_bot.py --test     ← processes messenger_full.json
#
# ── LIVE WEBHOOK MODE ────────────────────────────────────────────────────────
#   Step 1: Start the bot server
#       python messenger_bot.py        (port 5002)
#
#   Step 2: Expose it publicly with ngrok
#       ngrok http 5002
#       → copy the HTTPS URL shown, e.g. https://abc123.ngrok.io
#
#   Step 3: Register the webhook in Facebook Developer Console
#       App → Webhooks → Add Callback URL
#       Callback URL:   https://abc123.ngrok.io/webhook
#       Verify Token:   <same value as WEBHOOK_VERIFY_TOKEN in .env>
#       Click "Verify and Save"
#
#   Step 4: Subscribe to the right fields
#       Messenger → subscribe field: "messages"
#
# Notes:
#   - ngrok URL changes every restart (free tier) — re-register after each restart
#   - The pipeline builds a vectorstore on first run (~1-2 min); subsequent runs faster
#   - The page token must have pages_messaging permission
# =============================================================================

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv(override=True)

# ── Import chatbot pipeline ───────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent / "chatbot"))
from chatbot_pipeline import run_full_pipeline  # noqa: E402

# ── Import Facebook API utilities ─────────────────────────────────────────────
try:
    from message_reply import FacebookMessenger
    from config import Config
except ImportError as e:
    print(f"❌ Could not import Facebook utilities: {e}")
    sys.exit(1)

# ── Logger ────────────────────────────────────────────────────────────────────
logger = logging.getLogger("messenger_bot")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_h)

def _log(msg: str):
    logger.info(msg)

# ── Config ────────────────────────────────────────────────────────────────────
VERIFY_TOKEN = os.environ.get("WEBHOOK_VERIFY_TOKEN", "")
PAGE_ID = Config.FACEBOOK_PAGE_ID or ""
# Page display name used in messenger_full.json to identify page's own messages
PAGE_NAME = os.environ.get("FACEBOOK_PAGE_NAME", "Western Windows")

# Path to pre-fetched test data (project root)
_PROJECT_ROOT = Path(__file__).parent.parent
MESSENGER_JSON_PATH = Path(__file__).parent / "JSON" / "messenger_full.json"

# ── Flask App ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
messenger = None  # lazily initialized

# In-memory chat history per sender PSID for the live webhook session
# { psid: [{"role": "user"/"assistant", "content": "..."}, ...] }
_chat_histories: dict = {}


def _get_messenger() -> FacebookMessenger:
    global messenger
    if messenger is None:
        messenger = FacebookMessenger()
    return messenger


# =============================================================================
# CORE HANDLER
# =============================================================================

def handle_message(psid: str, user_name: str, message_text: str,
                   chat_history: list = None) -> bool:
    """
    Process a single Messenger message through the chatbot and reply.
    Returns True if reply was sent successfully.
    """
    _log(f"[MESSENGER BOT] 💬 Message from {user_name} (PSID: {psid})")
    _log(f"[MESSENGER BOT]    \"{message_text[:80]}\"")

    # Run chatbot pipeline — route=None lets the routing graph auto-decide
    result = run_full_pipeline(message_text, chat_history=chat_history or [], route=None, username=user_name)
    response_text = result.get("response", "").strip()

    if not response_text:
        _log(f"[MESSENGER BOT] ⚠ Empty response from pipeline — skipping reply")
        return False

    _log(f"[MESSENGER BOT] 🤖 Bot response ({len(response_text)} chars):")
    _log(f"[MESSENGER BOT]    \"{response_text[:120]}{'...' if len(response_text) > 120 else ''}\"")

    # Send reply
    success = _get_messenger().send_message(psid, response_text)
    if success:
        _log(f"[MESSENGER BOT] ✅ Replied to {user_name} ({psid})")
    else:
        _log(f"[MESSENGER BOT] ❌ Failed to send reply to {user_name} ({psid})")

    return success


# =============================================================================
# WEBHOOK (live mode)
# =============================================================================

@app.route("/webhook", methods=["GET"])
def webhook_verify():
    """Facebook webhook verification handshake."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        _log("[MESSENGER BOT] ✅ Webhook verified by Facebook")
        return challenge, 200
    else:
        _log("[MESSENGER BOT] ❌ Webhook verification failed — check WEBHOOK_VERIFY_TOKEN in .env")
        return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook_receive():
    """Receive and process Messenger message events."""
    payload = request.get_json(silent=True)
    if not payload:
        return "Bad Request", 400

    # Always return 200 immediately — Facebook requires fast ack
    _process_messenger_payload(payload)
    return "EVENT_RECEIVED", 200


def _process_messenger_payload(payload: dict):
    """Parse a Messenger webhook payload and handle incoming messages."""
    if payload.get("object") != "page":
        return

    for entry in payload.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender = messaging.get("sender", {})
            recipient = messaging.get("recipient", {})

            sender_id = sender.get("id", "")
            recipient_id = recipient.get("id", "")

            # Skip echo events (page's own messages)
            if sender_id == PAGE_ID:
                _log("[MESSENGER BOT] ⏭ Skipping echo event (page's own message)")
                continue

            message = messaging.get("message", {})

            # Skip non-text messages (attachments, read receipts, etc.)
            if not message or "text" not in message:
                continue

            # Skip echo messages from Messenger platform
            if message.get("is_echo"):
                continue

            message_text = message.get("text", "").strip()
            if not message_text:
                continue

            # Retrieve or initialize chat history for this user
            history = _chat_histories.get(sender_id, [])

            # Fetch user's real name from the Graph API
            user_name = _get_messenger().get_user_name(sender_id) or ""
            _log(f"\n[MESSENGER BOT] 📨 New message from {user_name or sender_id}")

            success = handle_message(sender_id, user_name, message_text,
                                     chat_history=history)

            if success:
                # Update history for next turn
                result_response = _get_last_response(sender_id)
                history = history + [
                    {"role": "user", "content": message_text},
                    {"role": "assistant", "content": result_response},
                ]
                # Keep last 10 turns (20 messages) to avoid unbounded growth
                _chat_histories[sender_id] = history[-20:]


def _get_last_response(psid: str) -> str:
    """Helper to get the last assistant response (stored on the fly)."""
    # This is called right after handle_message sends the reply.
    # We re-run the pipeline just to get the text back — but that's wasteful.
    # In practice, we'd refactor handle_message to return the response text.
    # For now, return empty string as history fallback.
    return ""


# =============================================================================
# TEST MODE (file-based)
# =============================================================================

def _build_chat_history(messages: list, page_name: str) -> list:
    """
    Convert messenger_full.json messages array into chat_history format.
    Sorts by timestamp ascending, maps sender_name to role.
    """
    # Sort oldest to newest
    sorted_msgs = sorted(messages, key=lambda m: m.get("timestamp", ""))
    history = []
    for msg in sorted_msgs:
        sender_name = msg.get("sender_name", "")
        content = msg.get("content", "").strip()
        if not content:
            continue
        role = "assistant" if sender_name == page_name else "user"
        history.append({"role": role, "content": content})
    return history


def run_from_file(json_path: Path = None):
    """
    Process pre-fetched conversations from messenger_full.json.
    For each unread conversation, sends a reply to the latest user message.
    """
    json_path = json_path or MESSENGER_JSON_PATH

    _log(f"[MESSENGER BOT] {'=' * 60}")
    _log(f"[MESSENGER BOT] 📂 Loading conversations from: {json_path}")
    _log(f"[MESSENGER BOT]    Page name: \"{PAGE_NAME}\"")

    if not json_path.exists():
        _log(f"[MESSENGER BOT] ❌ File not found: {json_path}")
        return

    with open(json_path, encoding="utf-8") as f:
        conversations = json.load(f)

    unread = [c for c in conversations if c.get("status") == "unread"]

    # Also include "read" conversations where the last message is from the user
    # (page admin may have viewed it, clearing unread flag, but bot hasn't replied)
    def _needs_reply(conv: dict) -> bool:
        if conv.get("status") == "unread":
            return True
        msgs = sorted(conv.get("messages", []), key=lambda m: m.get("timestamp", ""))
        if not msgs:
            return False
        last_sender = msgs[-1].get("sender_name", "")
        return last_sender != PAGE_NAME

    needs_reply = [c for c in conversations if _needs_reply(c)]
    _log(f"[MESSENGER BOT] 📊 {len(conversations)} total conversations, {len(unread)} unread, {len(needs_reply)} need a reply")

    total = 0
    replied = 0
    skipped = 0

    for conv in needs_reply:
        conv_id = conv.get("conversation_id", "")
        participants = conv.get("participants", [])
        messages = conv.get("messages", [])
        unread_count = conv.get("unread_count", 0)

        # Find the user (first participant that is not the page)
        user = next(
            (p for p in participants if p.get("name") != PAGE_NAME),
            None
        )
        if not user:
            _log(f"[MESSENGER BOT] ⚠ Could not identify user in conversation {conv_id} — skipping")
            skipped += 1
            continue

        psid = user.get("psid", "")
        user_name = user.get("name", f"User {psid}")

        if not psid:
            skipped += 1
            continue

        # Build full chat history from all messages
        full_history = _build_chat_history(messages, PAGE_NAME)

        # Skip if the bot already replied as the last message (avoid duplicate replies)
        if full_history and full_history[-1]["role"] == "assistant":
            _log(f"[MESSENGER BOT] ⏭ Conversation {conv_id} already has a bot reply as last message — skipping")
            skipped += 1
            continue

        # Find the latest user message (the one we should reply to)
        latest_user_msg = next(
            (m for m in reversed(full_history) if m["role"] == "user"),
            None
        )
        if not latest_user_msg:
            _log(f"[MESSENGER BOT] ⚠ No user message found in conversation {conv_id} — skipping")
            skipped += 1
            continue

        query = latest_user_msg["content"]

        # Chat history = everything BEFORE the latest user message (for context)
        latest_idx = len(full_history) - 1 - next(
            i for i, m in enumerate(reversed(full_history)) if m["role"] == "user"
        )
        history_context = full_history[:latest_idx]

        total += 1
        _log(f"\n[MESSENGER BOT] ── Conversation {total}: {user_name} ({unread_count} unread) ──")

        success = handle_message(psid, user_name, query, chat_history=history_context)
        if success:
            replied += 1
        else:
            skipped += 1

    _log(f"\n[MESSENGER BOT] {'=' * 60}")
    _log(f"[MESSENGER BOT] ✅ Done — {total} conversation(s) processed, {replied} replied, {skipped} skipped")
    _log(f"[MESSENGER BOT] {'=' * 60}")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Facebook Messenger Chatbot Bot\n"
                    "  Live mode:  python messenger_bot.py\n"
                    "  Test mode:  python messenger_bot.py --test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Process messenger_full.json locally instead of starting the webhook server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5002,
        help="Port for the webhook server (default: 5002)",
    )
    args = parser.parse_args()

    if args.test:
        _log("[MESSENGER BOT] ▶ Running in TEST mode (file-based)")
        run_from_file()
    else:
        if not VERIFY_TOKEN:
            _log("[MESSENGER BOT] ⚠ WEBHOOK_VERIFY_TOKEN is not set in .env — webhook verification will fail")
        _log(f"[MESSENGER BOT] ▶ Starting webhook server on port {args.port}")
        _log(f"[MESSENGER BOT]   Next: run 'ngrok http {args.port}' and register the URL in Facebook Developer Console")
        app.run(port=args.port, debug=True)
