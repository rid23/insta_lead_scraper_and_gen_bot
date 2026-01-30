"""
Simple test to verify the Unicode fix works
"""


def test_unicode_fix():
    """Test that the Unicode characters have been properly replaced"""
    print("[TEST] Testing Unicode fix...")

    # Read the main file and check for problematic Unicode characters
    with open("instagram_discovery_bot.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Check that emojis have been replaced
    if "🤖" in content or "✅" in content:
        print("[ERROR] Unicode emojis still present in the file")
        return False

    # Check that replacements are present
    if "[BOT]" in content and "[SUCCESS]" in content:
        print("[SUCCESS] Unicode characters have been properly replaced")
        return True
    else:
        print("[ERROR] Replacement text not found")
        return False


if __name__ == "__main__":
    success = test_unicode_fix()
    if success:
        print("[SUCCESS] Unicode fix verification completed successfully")
    else:
        print("[ERROR] Unicode fix verification failed")
