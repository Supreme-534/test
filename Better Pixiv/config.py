# Application configuration
import os

# Paths
FIXED_FOLDER_PATH = "D:/pixiv"
JUNKO_FOLDER = "Junko"
SFW_FOLDER = "sfw"

# Files
POINTS_FILE = "points.json"
NICE_FILE = "nice.json"

# Supported formats
SUPPORTED_IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
SUPPORTED_VIDEO_EXTS = ('.webm', '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.m4v', '.3gp')

# UI Settings
THUMBNAIL_SIZE = 120
SIDEBAR_WIDTH = 150
MAIN_WINDOW_SIZE = "1600x900"

# Zoom settings
ZOOM_MIN = 0.1
ZOOM_MAX = 5.0
ZOOM_FACTOR = 1.1
ZOOM_ANIMATION_STEPS = 10
ZOOM_ANIMATION_DELAY = 20

# Video settings
VIDEO_FPS = 30
VIDEO_BUFFER_SIZE = 10

# Debug settings - SET TO FALSE TO REDUCE CONSOLE OUTPUT
DEBUG_MODE = False
PRINT_VIDEO_INFO = False  # Set to False to reduce video messages
PRINT_LOAD_INFO = True    # Keep basic loading info

# Create special folders
os.makedirs(os.path.join(FIXED_FOLDER_PATH, JUNKO_FOLDER), exist_ok=True)
os.makedirs(os.path.join(FIXED_FOLDER_PATH, SFW_FOLDER), exist_ok=True)
