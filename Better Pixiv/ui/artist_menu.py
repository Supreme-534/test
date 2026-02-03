import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from config import *

class ArtistMenu:
    def __init__(self, root, on_back, on_work_select):
        self.root = root
        self.on_back = on_back
        self.on_work_select = on_work_select
        
        self.frame = None
        self.canvas = None
        self.thumbnail_frame = None
        self.thumbnails = []
        
        # Navigation state
        self.current_artist_id = None
        self.current_works = []
        self.current_index = 0
    
    def show(self, artist_id, artist_name, works):
        """Show artist menu WITHOUT scrollbars and WITHOUT back button"""
        self.current_artist_id = artist_id
        self.current_works = works
        self.current_index = 0
        
        # Create main frame
        self.frame = tk.Frame(self.root, bg='#2d2d2d')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Artist name (centered top)
        artist_label = tk.Label(self.frame, text=artist_name,
                              font=('Segoe UI', 20, 'bold'),
                              bg='#2d2d2d', fg='white')
        artist_label.pack(pady=20)
        
        # Works count
        count_label = tk.Label(self.frame, 
                              text=f"{len(works)} works",
                              font=('Segoe UI', 10),
                              bg='#2d2d2d', fg='#aaaaaa')
        count_label.pack()
        
        # Create thumbnail grid WITHOUT scrollbars
        self.create_thumbnail_grid(works)
    
    def create_thumbnail_grid(self, works):
        """Create grid of artist's works - NO SCROLLBARS, EXPANDED WIDTH"""
        # Create main container that fills available space
        self.thumbnail_frame = tk.Frame(self.frame, bg='#2d2d2d')
        self.thumbnail_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Calculate grid layout - use more columns for wider display
        self.thumbnails = []
        cols = 8  # Increased for better horizontal fill
        thumb_size = THUMBNAIL_SIZE + 20
        
        # Create thumbnails in grid directly (no canvas)
        for idx, work in enumerate(works):
            row = idx // cols
            col = idx % cols
            
            # Create thumbnail frame
            thumb_frame = tk.Frame(self.thumbnail_frame, bg='#2d2d2d')
            thumb_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nw')
            
            # Load thumbnail
            thumb_img = self.load_work_thumbnail(work['thumbnail'])
            
            # Clickable thumbnail button
            btn = tk.Button(thumb_frame, image=thumb_img,
                          command=lambda p=work['post_id']: self.on_work_select(p),
                          bg='#3d3d3d', relief='flat',
                          cursor='hand2')
            btn.image = thumb_img
            btn.pack()
            
            # Page count badge
            if work.get('page_count', 1) > 1:
                badge = tk.Label(thumb_frame, 
                               text=f"{work['page_count']}p",
                               bg='#f44336', fg='white',
                               font=('Segoe UI', 8))
                badge.place(relx=1.0, rely=0.0, anchor='ne')
            
            # Work title
            title = work['thumbnail'].get('title', 'Untitled')
            if len(title) > 25:
                title = title[:25] + "..."
            
            title_label = tk.Label(thumb_frame, text=title,
                                 bg='#2d2d2d', fg='white',
                                 font=('Segoe UI', 8),
                                 wraplength=thumb_size)
            title_label.pack()
            
            self.thumbnails.append({
                'frame': thumb_frame,
                'button': btn,
                'work': work
            })
        
        # Configure grid to expand
        for i in range(cols):
            self.thumbnail_frame.columnconfigure(i, weight=1)
    
    def load_work_thumbnail(self, thumbnail_info):
        """Load thumbnail for a work"""
        from config import FIXED_FOLDER_PATH
        path = thumbnail_info['full_path']
        
        try:
            if thumbnail_info['filename'].lower().endswith(SUPPORTED_IMAGE_EXTS):
                img = Image.open(path)
                img.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE))
                return ImageTk.PhotoImage(img)
        except:
            pass
        
        # Fallback thumbnail
        return ImageTk.PhotoImage(
            Image.new('RGB', (THUMBNAIL_SIZE, THUMBNAIL_SIZE), '#3d3d3d')
        )
    
    def next_work(self):
        """Navigate to next work in artist mode"""
        if self.current_works:
            self.current_index = (self.current_index + 1) % len(self.current_works)
            return self.current_works[self.current_index]['post_id']
        return None
    
    def prev_work(self):
        """Navigate to previous work in artist mode"""
        if self.current_works:
            self.current_index = (self.current_index - 1) % len(self.current_works)
            return self.current_works[self.current_index]['post_id']
        return None
    
    def hide(self):
        """Hide artist menu"""
        if self.frame and self.frame.winfo_exists():
            self.frame.destroy()
        
        self.frame = None
        self.canvas = None
        self.thumbnail_frame = None
        self.thumbnails = []
    
    def is_visible(self):
        """Check if artist menu is visible"""
        return self.frame is not None and self.frame.winfo_exists()