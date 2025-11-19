#!/usr/bin/env python3
"""
Test script to verify OpenAI API connection and model access.
Run this to check if your API key and model configuration are working.

Usage:
    uv run python test_openai_connection.py
"""

import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import after loading env (intentionally after load_dotenv to ensure env vars are loaded)
from src.openai_handler import (  # noqa: E402
    FALLBACK_MODEL,
    OPENAI_API_KEY,
    PRIMARY_MODEL,
    chat_with_history,
)


def test_connection():
    """Test OpenAI API connection with current configuration."""
    print("=" * 60)
    print("OpenAI Connection Test")
    print("=" * 60)

    # Check API key
    if not OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        print("   Please set it in your .env file")
        return False

    api_key_preview = f"{OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]}"
    print(f"✓ API Key found: {api_key_preview}")
    print(f"✓ Primary model: {PRIMARY_MODEL}")
    print(f"✓ Fallback model: {FALLBACK_MODEL}")
    print()

    # Test with simple message
    print("Testing connection with simple message...")
    print("-" * 60)

    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello! API connection successful.' and nothing else."}
    ]

    try:
        response = chat_with_history(test_messages, model=PRIMARY_MODEL)
        print(f"✓ SUCCESS with {PRIMARY_MODEL}!")
        print(f"  Response: {response}")
        print()
        return True

    except Exception as e:
        print(f"❌ ERROR with {PRIMARY_MODEL}:")
        print(f"  {str(e)}")
        print()

        # Check if it's a quota error
        error_str = str(e).lower()
        if "quota" in error_str or "insufficient_quota" in error_str:
            print("💡 DIAGNOSIS: Quota Error")
            print("   This means your OpenAI account has exceeded its usage limits.")
            print("   Possible causes:")
            print("   1. You haven't added billing information to your OpenAI account")
            print("   2. You've exceeded your spending limit")
            print("   3. Your free trial credits have expired")
            print()
            print("   Solutions:")
            print("   1. Visit https://platform.openai.com/account/billing")
            print("   2. Add a payment method if you haven't already")
            print("   3. Check your usage and limits")
            print("   4. Increase your spending limit if needed")

        elif "invalid" in error_str and "model" in error_str:
            print("💡 DIAGNOSIS: Invalid Model")
            print(f"   The model '{PRIMARY_MODEL}' is not accessible with your API key.")
            print("   Possible causes:")
            print("   1. Your account doesn't have access to this model")
            print("   2. The model name is incorrect")
            print()
            print("   Solutions:")
            print("   1. Try setting OPENAI_MODEL=gpt-4o-mini in your .env (cheaper tier)")
            print("   2. Check available models at https://platform.openai.com/docs/models")
            print("   3. Verify your account tier and permissions")

        elif "connection" in error_str or "network" in error_str:
            print("💡 DIAGNOSIS: Connection Error")
            print("   Unable to reach OpenAI servers.")
            print("   Solutions:")
            print("   1. Check your internet connection")
            print("   2. Check if OpenAI services are down: https://status.openai.com")
            print("   3. Try again in a few moments")

        print()
        return False


if __name__ == "__main__":
    print()
    success = test_connection()
    print("=" * 60)

    if success:
        print("✅ All tests passed! Your OpenAI configuration is working.")
        sys.exit(0)
    else:
        print("❌ Tests failed. Please fix the issues above and try again.")
        sys.exit(1)
