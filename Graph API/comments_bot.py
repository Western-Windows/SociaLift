#!/usr/bin/env python3
# =============================================================================
# comments_bot.py
# Chatbot integration for Facebook post comments.
# Two modes:
#   python comments_bot.py          → live Flask webhook server (port 5001)
#   python comments_bot.py --test   → process comments_all.json locally
# =============================================================================
#
# ── SETUP GUIDE ──────────────────────────────────────────────────────────────
#
# ── .env requirements ────────────────────────────────────────────────────────
#   FACEBOOK_PAGE_ACCESS_TOKEN=<your page access token>
#   FACEBOOK_PAGE_ID=<your numeric page id>
#   WEBHOOK_VERIFY_TOKEN=<any secret string you choose>
#   LIGHT_LLM_PROVIDER=groq
#   LIGHT_LLM_MODEL=llama-3.1-8b-instant
#   GOOD_LLM_PROVIDER=groq
#   GOOD_LLM_MODEL=llama-3.3-70b-versatile
#   GROQ_API_KEY=<your groq api key>
#
# ── LOCAL TESTING (no live Facebook needed) ──────────────────────────────────
#   python comments_bot.py --test     ← processes comments_all.json
#
# ── LIVE WEBHOOK MODE ────────────────────────────────────────────────────────
#   Step 1: Start the bot server
#       python comments_bot.py        (port 5001)
#
#   Step 2: Expose it publicly with ngrok
#       ngrok http 5001
#       → copy the HTTPS URL shown, e.g. https://abc123.ngrok.io
#
#   Step 3: Register the webhook in Facebook Developer Console
#       App → Webhooks → Add Callback URL
#       Callback URL:   https://abc123.ngrok.io/webhook
#       Verify Token:   <same value as WEBHOOK_VERIFY_TOKEN in .env>
#       Click "Verify and Save"
#
#   Step 4: Subscribe to the right fields
#       Page → subscribe field: "feed"
#
# Notes:
#   - ngrok URL changes every restart (free tier) — re-register after each restart
#   - The pipeline builds a vectorstore on first run (~1-2 min); subsequent runs faster
#   - The page token must have pages_read_engagement + pages_manage_posts permissions
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
from chatbot_pipeline import run_full_pipeline, _ColorFormatter  # noqa: E402

# ── Import Facebook API utilities ─────────────────────────────────────────────
try:
    from comment_reply import FacebookBot
    from config import Config
except ImportError as e:
    print(f"[ERR] Could not import Facebook utilities: {e}")
    sys.exit(1)

# ── Logger ────────────────────────────────────────────────────────────────────
logger = logging.getLogger("comments_bot")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(_ColorFormatter("%(message)s"))
    logger.addHandler(_h)

def _log(msg: str):
    logger.info(msg)

# ── Config ────────────────────────────────────────────────────────────────────
VERIFY_TOKEN = os.environ.get("WEBHOOK_VERIFY_TOKEN", "")
PAGE_ID = Config.FACEBOOK_PAGE_ID or ""
PAGE_NAME = os.environ.get("FACEBOOK_PAGE_NAME", "Fashion Hub")

# Path to pre-fetched test data (project root)
_PROJECT_ROOT = Path(__file__).parent.parent
COMMENTS_JSON_PATH = Path(__file__).parent / "JSON" / "comments_all.json"

# ── Flask App ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
bot = None  # lazily initialized to avoid errors at import time


def _get_bot() -> FacebookBot:
    global bot
    if bot is None:
        bot = FacebookBot()
    return bot


# =============================================================================
# CORE HANDLER
# =============================================================================

def _strip_page_mention(message: str) -> str:
    """Remove leading page name mention (e.g. 'Western Windows ') from comment text."""
    if PAGE_NAME and message.lower().startswith(PAGE_NAME.lower()):
        message = message[len(PAGE_NAME):].lstrip(" ,")
    return message.strip()


def handle_comment(comment_id: str, message: str, post_snippet: str = "",
                   username: str = "") -> bool:
    """
    Process a single comment through the chatbot and reply.
    Returns True if reply was sent successfully.
    """
    message = _strip_page_mention(message)

    _log(f"[COMMENTS BOT] [MSG] Comment {comment_id}")
    _log(f"[COMMENTS BOT]    From: {username or 'unknown'}")
    _log(f"[COMMENTS BOT]    Post: \"{post_snippet[:60]}\"")
    _log(f"[COMMENTS BOT]    Message: \"{message[:80]}\"")

    # Run chatbot pipeline — route=None lets the routing graph auto-decide
    result = run_full_pipeline(message, route=None, username=username)
    response_text = result.get("response", "").strip()

    if not response_text:
        _log(f"[COMMENTS BOT] [WARN] Empty response from pipeline — skipping reply")
        return False

    _log(f"[COMMENTS BOT] [LLM] Bot response ({len(response_text)} chars):")
    _log(f"[COMMENTS BOT]    \"{response_text[:120]}{'...' if len(response_text) > 120 else ''}\"")

    # Send reply
    success = _get_bot().send_reply(comment_id, response_text)
    if success:
        _log(f"[COMMENTS BOT] [OK] Replied to comment {comment_id}")
    else:
        _log(f"[COMMENTS BOT] [ERR] Failed to send reply to comment {comment_id}")

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
        _log("[COMMENTS BOT] [OK] Webhook verified by Facebook")
        return challenge, 200
    else:
        _log("[COMMENTS BOT] [ERR] Webhook verification failed — check WEBHOOK_VERIFY_TOKEN in .env")
        return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook_receive():
    """Receive and process Facebook feed events."""
    payload = request.get_json(silent=True)
    if not payload:
        return "Bad Request", 400

    # Always return 200 immediately — Facebook requires fast ack
    # Process asynchronously (for production, use a task queue like Celery)
    _process_feed_payload(payload)
    return "EVENT_RECEIVED", 200


def _process_feed_payload(payload: dict):
    """Parse a Facebook feed webhook payload and handle new comments."""
    if payload.get("object") != "page":
        return

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") != "feed":
                continue

            value = change.get("value", {})
            item = value.get("item")
            verb = value.get("verb")

            # Only handle new comments
            if item != "comment" or verb != "add":
                continue

            # Skip page's own comments
            sender_id = value.get("from", {}).get("id", "")
            if sender_id == PAGE_ID:
                _log("[COMMENTS BOT] [SKIP] Skipping own page comment")
                continue

            comment_id = value.get("comment_id", "")
            message = value.get("message", "").strip()
            post_id = value.get("post_id", "")
            parent_id = value.get("parent_id", "")

            if not comment_id or not message:
                continue

            _log(f"[COMMENTS BOT] [SEARCH] parent_id={parent_id!r} post_id={post_id!r} tags={value.get('message_tags')!r}")

            # Skip replies to other users' comments (parent_id is a comment, not the post)
            # This catches user-to-user threads where the page shouldn't interfere.
            is_reply_to_comment = parent_id and parent_id != post_id
            if is_reply_to_comment:
                _log(f"[COMMENTS BOT] [SKIP] Skipping reply to another comment (parent={parent_id})")
                continue

            # Skip comments that tag other users but not the page.
            # message_tags is a list of dicts: {id, name, type, offset, length}
            # type "user" = another person, type "page" = a page (could be ours)
            message_tags = value.get("message_tags") or []
            if message_tags:
                tagged_ids = {tag.get("id", "") for tag in message_tags}
                mentions_page = PAGE_ID in tagged_ids
                if not mentions_page:
                    sender_name = value.get("from", {}).get("name", "someone")
                    _log(f"[COMMENTS BOT] [SKIP] Skipping user-to-user comment from {sender_name} (tags others, not page)")
                    continue

            sender_name = value.get("from", {}).get("name", "")
            _log(f"[COMMENTS BOT] [IN] New comment event | post={post_id} | from={sender_name}")
            handle_comment(comment_id, message, post_snippet=f"Post {post_id}", username=sender_name)


# =============================================================================
# TEST MODE (file-based)
# =============================================================================

def run_from_file(json_path: Path = None):
    """
    Process pre-fetched comments from comments_all.json.
    Filters to unreplied top-level comments and replies to each.
    """
    json_path = json_path or COMMENTS_JSON_PATH

    _log(f"[COMMENTS BOT] {'=' * 60}")
    _log(f"[COMMENTS BOT] [LOAD] Loading comments from: {json_path}")

    if not json_path.exists():
        _log(f"[COMMENTS BOT] [ERR] File not found: {json_path}")
        return

    with open(json_path, encoding="utf-8") as f:
        posts = json.load(f)

    _log(f"[COMMENTS BOT] [STATS] Found {len(posts)} posts")

    total_comments = 0
    replied = 0
    skipped = 0

    for post in posts:
        post_id = post.get("post_id", "")
        post_snippet = post.get("post_snippet", "")
        comments = post.get("comments", [])

        # Build a set of comment IDs that the page has already replied to
        replied_to_ids = {
            c.get("reply_to_id")
            for c in comments
            if c.get("is_by_page") and c.get("is_reply") and c.get("reply_to_id")
        }

        # Collect top-level comments from users (not by page, not a reply)
        unreplied = [
            c for c in comments
            if not c.get("is_by_page")
            and not c.get("is_reply")
            and c.get("id") not in replied_to_ids
        ]

        _log(f"\n[COMMENTS BOT] [DOCS] Post: \"{post_snippet[:60]}\"")
        _log(f"[COMMENTS BOT]    {len(unreplied)} unreplied comment(s) out of {len(comments)} total")

        for comment in unreplied:
            comment_id = comment.get("id", "")
            message = comment.get("message", "").strip()
            if not message:
                skipped += 1
                continue

            # Skip user-to-user comments (tags someone other than the page)
            message_tags = comment.get("message_tags", [])
            if message_tags:
                tagged_ids = {tag.get("id", "") for tag in message_tags}
                if PAGE_ID not in tagged_ids:
                    _log(f"\n[COMMENTS BOT] [SKIP] Skipping user-to-user comment: \"{message[:60]}\"")
                    skipped += 1
                    continue

            username = comment.get("from", {}).get("name", "") or comment.get("user_name", "")
            total_comments += 1
            _log(f"\n[COMMENTS BOT] ── Comment {total_comments} ──────────────────────────")
            success = handle_comment(comment_id, message, post_snippet=post_snippet, username=username)
            if success:
                replied += 1
            else:
                skipped += 1

    _log(f"\n[COMMENTS BOT] {'=' * 60}")
    _log(f"[COMMENTS BOT] [OK] Done — {total_comments} comment(s) processed, {replied} replied, {skipped} skipped")
    _log(f"[COMMENTS BOT] {'=' * 60}")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Facebook Comments Chatbot Bot\n"
                    "  Live mode:  python comments_bot.py\n"
                    "  Test mode:  python comments_bot.py --test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Process comments_all.json locally instead of starting the webhook server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5001,
        help="Port for the webhook server (default: 5001)",
    )
    args = parser.parse_args()

    if args.test:
        _log("[COMMENTS BOT] >> Running in TEST mode (file-based)")
        run_from_file()
    else:
        if not VERIFY_TOKEN:
            _log("[COMMENTS BOT] [WARN] WEBHOOK_VERIFY_TOKEN is not set in .env — webhook verification will fail")
        _log(f"[COMMENTS BOT] >> Starting webhook server on port {args.port}")
        _log(f"[COMMENTS BOT]   Next: run 'ngrok http {args.port}' and register the URL in Facebook Developer Console")
        app.run(port=args.port, debug=True)
