import pyperclip

def copy_to_clipboard(text):
    """Copy text to clipboard with error handling"""
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False

def get_pixiv_url(post_id):
    """Generate Pixiv URL for a post ID"""
    return f"https://www.pixiv.net/en/artworks/{post_id}"