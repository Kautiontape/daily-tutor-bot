import logging
import subprocess

from sqlalchemy.orm import Session
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CallbackContext

from src.db import get_db


def error_handler(update, context):
    logging.error(f"Update {update} caused error {context.error}")


# Dependency for the database session
def get_db_context() -> Session:
    # We may choose to use the CallbackContext to get the database session
    # For now, though, we expect only one database
    return next(get_db())


async def send_typing(update: Update, context: CallbackContext) -> None:
    # Send that the bot is typing so the user knows to wait
    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)


def get_git_commit_hash() -> str:
    """Get the current git commit hash from VERSION file or git."""
    from pathlib import Path

    # Try to read from VERSION file first (production)
    version_file = Path(__file__).parent.parent / "VERSION"
    if version_file.exists():
        try:
            return version_file.read_text().strip()
        except Exception as e:
            logging.warning(f"Failed to read VERSION file: {e}")

    # Fallback to git command (development)
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT, text=True).strip()
        return commit_hash
    except subprocess.CalledProcessError:
        return "Unknown (not a git repository)"
    except FileNotFoundError:
        return "Unknown (git not available)"
    except Exception as e:
        return f"Unknown (error: {str(e)})"
