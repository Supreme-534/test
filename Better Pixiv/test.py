import os
from config import FIXED_FOLDER_PATH, SUPPORTED_VIDEO_EXTS

def check_video_files():
    print("=== CHECKING FOR VIDEO FILES ===")
    print(f"Folder: {FIXED_FOLDER_PATH}")
    
    if not os.path.exists(FIXED_FOLDER_PATH):
        print("ERROR: Folder does not exist!")
        return
    
    files = os.listdir(FIXED_FOLDER_PATH)
    video_files = []
    
    for f in files:
        f_lower = f.lower()
        if any(f_lower.endswith(ext) for ext in SUPPORTED_VIDEO_EXTS):
            video_files.append(f)
    
    print(f"\nFound {len(video_files)} video files:")
    for video in video_files:
        print(f"  - {video}")
    
    if video_files:
        print(f"\nFirst video: {video_files[0]}")
        print(f"Full path: {os.path.join(FIXED_FOLDER_PATH, video_files[0])}")
    else:
        print("\nNO VIDEO FILES FOUND!")
    
    return video_files

if __name__ == "__main__":
    check_video_files()
