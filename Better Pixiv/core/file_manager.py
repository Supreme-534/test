import os
import re
from collections import defaultdict
from config import *

def parse_filename(filename):
    """
    SUPER FLEXIBLE filename parser that handles:
    1. Standard: 12345678_p0-title-artist-12345.ext
    2. Variations: 12345678_p0-title-artist.ext
    3. Minimal: 12345678_p0.ext
    4. Video files with any pattern
    """
    name, ext = os.path.splitext(filename)
    ext_lower = ext.lower()
    
    # Check if it's a video FIRST
    is_video = any(ext_lower == video_ext.lower() for video_ext in SUPPORTED_VIDEO_EXTS)
    
    # Debug for video files
    if is_video and DEBUG_MODE:  # Only print in debug mode
        print(f"VIDEO DETECTED: {filename}")
    
    # Try multiple patterns in order of specificity
    patterns = [
        # Standard full pattern
        r'^(\d+)_p(\d+)-(.+)-(.+)-(\d+)$',
        # Missing artist_id
        r'^(\d+)_p(\d+)-(.+)-(.+)$',
        # Just title
        r'^(\d+)_p(\d+)-(.+)$',
        # Just post_id and page
        r'^(\d+)_p(\d+)$',
        # Just post_id
        r'^(\d+)_p',
        # Any pattern starting with numbers
        r'^(\d+)'
    ]
    
    for pattern_idx, pattern in enumerate(patterns):
        match = re.match(pattern, name)
        if match:
            groups = match.groups()
            
            # Extract data based on pattern
            if pattern_idx == 0:  # Full pattern: 123_p0-title-artist-12345
                return {
                    'post_id': groups[0],
                    'page': int(groups[1]),
                    'title': groups[2],
                    'artist': groups[3],
                    'artist_id': groups[4],
                    'filename': filename,
                    'full_path': os.path.join(FIXED_FOLDER_PATH, filename),
                    'is_video': is_video
                }
            elif pattern_idx == 1:  # 123_p0-title-artist
                return {
                    'post_id': groups[0],
                    'page': int(groups[1]),
                    'title': groups[2],
                    'artist': groups[3],
                    'artist_id': groups[3],  # Use artist name as ID
                    'filename': filename,
                    'full_path': os.path.join(FIXED_FOLDER_PATH, filename),
                    'is_video': is_video
                }
            elif pattern_idx == 2:  # 123_p0-title
                return {
                    'post_id': groups[0],
                    'page': int(groups[1]),
                    'title': groups[2],
                    'artist': 'Unknown',
                    'artist_id': 'unknown',
                    'filename': filename,
                    'full_path': os.path.join(FIXED_FOLDER_PATH, filename),
                    'is_video': is_video
                }
            elif pattern_idx == 3:  # 123_p0
                return {
                    'post_id': groups[0],
                    'page': int(groups[1]),
                    'title': 'Untitled',
                    'artist': 'Unknown',
                    'artist_id': 'unknown',
                    'filename': filename,
                    'full_path': os.path.join(FIXED_FOLDER_PATH, filename),
                    'is_video': is_video
                }
            elif pattern_idx == 4:  # 123_p (incomplete)
                return {
                    'post_id': groups[0],
                    'page': 0,
                    'title': 'Untitled',
                    'artist': 'Unknown',
                    'artist_id': 'unknown',
                    'filename': filename,
                    'full_path': os.path.join(FIXED_FOLDER_PATH, filename),
                    'is_video': is_video
                }
            elif pattern_idx == 5:  # Just numbers
                return {
                    'post_id': groups[0],
                    'page': 0,
                    'title': 'Untitled',
                    'artist': 'Unknown',
                    'artist_id': 'unknown',
                    'filename': filename,
                    'full_path': os.path.join(FIXED_FOLDER_PATH, filename),
                    'is_video': is_video
                }
    
    # If no pattern matches at all, create minimal entry
    print(f"WARNING: Could not parse filename: {filename}")
    return {
        'post_id': 'unknown',
        'page': 0,
        'title': 'Untitled',
        'artist': 'Unknown',
        'artist_id': 'unknown',
        'filename': filename,
        'full_path': os.path.join(FIXED_FOLDER_PATH, filename),
        'is_video': is_video
    }

class FileManager:
    def __init__(self):
        self.all_files = []
        self.all_posts = defaultdict(list)
        self.all_artists = defaultdict(list)
        self.video_posts = []
        self.load_files()
    
    def load_files(self):
        """Load and parse all files from the folder"""
        self.all_files.clear()
        self.video_posts.clear()
        
        print(f"Loading files from: {FIXED_FOLDER_PATH}")
        
        if not os.path.exists(FIXED_FOLDER_PATH):
            print(f"ERROR: Folder does not exist: {FIXED_FOLDER_PATH}")
            return
        
        files = os.listdir(FIXED_FOLDER_PATH)
        print(f"Found {len(files)} items in folder")
        
        video_count = 0
        image_count = 0
        failed_parse = 0
        
        for f in files:
            f_lower = f.lower()
            full_path = os.path.join(FIXED_FOLDER_PATH, f)
            
            if os.path.isfile(full_path):
                # Check file type
                is_image = any(f_lower.endswith(ext.lower()) for ext in SUPPORTED_IMAGE_EXTS)
                is_video = any(f_lower.endswith(ext.lower()) for ext in SUPPORTED_VIDEO_EXTS)
                
                if is_image or is_video:
                    parsed = parse_filename(f)
                    if parsed:
                        self.all_files.append(parsed)
                        
                        if parsed['is_video']:
                            video_count += 1
                            if parsed['post_id'] not in self.video_posts:
                                self.video_posts.append(parsed['post_id'])
                        else:
                            image_count += 1
                    else:
                        failed_parse += 1
                        print(f"FAILED TO PARSE: {f}")
        
        print(f"\n=== LOADING SUMMARY ===")
        print(f"Total files loaded: {len(self.all_files)}")
        print(f"  Videos: {video_count} files, {len(self.video_posts)} posts")
        print(f"  Images: {image_count} files")
        print(f"  Failed to parse: {failed_parse} files")
        
        if self.video_posts:
            print(f"\nFirst 10 video post IDs:")
            for i, post_id in enumerate(self.video_posts[:10]):
                print(f"  {i+1}. {post_id}")
        
        self.group_files()
    
    def group_files(self):
        """Group files by post ID and artist"""
        self.all_posts.clear()
        self.all_artists.clear()
        
        for file_info in self.all_files:
            self.all_posts[file_info['post_id']].append(file_info)
        
        for post_id in self.all_posts:
            self.all_posts[post_id].sort(key=lambda x: x['page'])
        
        for post_id, files in self.all_posts.items():
            if files:
                artist_info = {
                    'artist': files[0]['artist'],
                    'artist_id': files[0]['artist_id'],
                    'post_id': post_id,
                    'thumbnail': files[0],
                    'page_count': len(files)
                }
                self.all_artists[files[0]['artist_id']].append(artist_info)
        
        print(f"\nGrouped into {len(self.all_posts)} posts, {len(self.all_artists)} artists")
        
        # Debug: Count how many posts have videos
        video_post_count = 0
        for post_id, files in self.all_posts.items():
            if any(f['is_video'] for f in files):
                video_post_count += 1
        
        print(f"Posts containing videos: {video_post_count}")
    
    def get_video_posts(self):
        """Get all posts that contain videos"""
        print(f"\nDEBUG: Video posts found: {len(self.video_posts)}")
        if self.video_posts:
            print(f"Sample video post IDs: {self.video_posts[:5]}")
        return self.video_posts.copy()
    
    def delete_file(self, filename):
        """Delete a file and update groups"""
        path = os.path.join(FIXED_FOLDER_PATH, filename)
        if os.path.exists(path):
            os.remove(path)
            
            self.all_files = [f for f in self.all_files if f['filename'] != filename]
            self.group_files()
            return True
        return False
    
    def move_file(self, filename, target_folder):
        """Move file to target folder (SFW/Junko)"""
        src = os.path.join(FIXED_FOLDER_PATH, filename)
        dst = os.path.join(FIXED_FOLDER_PATH, target_folder, filename)
        
        try:
            import shutil
            shutil.move(src, dst)
            
            self.all_files = [f for f in self.all_files if f['filename'] != filename]
            self.group_files()
            return True
        except:
            return False
    
    def get_artist_works(self, artist_id):
        """Get all works by an artist"""
        return self.all_artists.get(artist_id, [])
    
    def get_post_files(self, post_id):
        """Get all files for a post"""
        return self.all_posts.get(post_id, [])
    
    def get_random_post(self, prefer_video=False):
        """Get a random post ID"""
        import random
        
        if not self.all_posts:
            return None
        
        if prefer_video and self.video_posts:
            print(f"DEBUG: Getting random video from {len(self.video_posts)} options")
            return random.choice(self.video_posts)
        else:
            return random.choice(list(self.all_posts.keys()))
