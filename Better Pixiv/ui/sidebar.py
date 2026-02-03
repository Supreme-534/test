import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from config import *
import os

class Sidebar:
    def __init__(self, root, on_page_select, on_page_delete):
        self.root = root
        self.on_page_select = on_page_select
        self.on_page_delete = on_page_delete
        
        self.frame = None
        self.canvas = None
        self.thumb_frame = None
        self.thumb_buttons = []
        self.thumb_images = []
    
    def create(self, work_files, current_page_idx):
        """Create sidebar with properly sized thumbnails"""
        self.destroy()
        
        if len(work_files) <= 1:
            return None
        
        # Create main frame
        self.frame = tk.Frame(self.root, bg='#2d2d2d', width=SIDEBAR_WIDTH)
        self.frame.place(relx=1.0, rely=0.1, anchor='ne', x=-10, y=0, relheight=0.7)
        self.frame.pack_propagate(False)
        
        # Canvas WITHOUT scrollbar
        self.canvas = tk.Canvas(self.frame, bg='#2d2d2d', 
                               highlightthickness=0, width=SIDEBAR_WIDTH)
        self.thumb_frame = tk.Frame(self.canvas, bg='#2d2d2d')
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.create_window((0, 0), window=self.thumb_frame, anchor=tk.NW)
        
        # Create thumbnails with proper size
        self.thumb_buttons = []
        self.thumb_images = []
        
        for idx, page_info in enumerate(work_files):
            self.create_thumbnail(idx, page_info)
        
        # Bind mouse wheel for scrolling
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel_linux)
        self.canvas.bind("<Button-5>", self.on_mousewheel_linux)
        
        self.thumb_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.highlight_thumbnail(current_page_idx)
        
        return self.frame
    
    def create_thumbnail(self, idx, page_info):
        """Create a thumbnail with proper size (120x120)"""
        # Create container frame with fixed width
        container = tk.Frame(self.thumb_frame, bg='#2d2d2d', 
                           width=SIDEBAR_WIDTH-20, height=140)
        container.pack(pady=5, padx=5, fill=tk.X)
        container.pack_propagate(False)
        
        # Create inner frame for content
        content_frame = tk.Frame(container, bg='#2d2d2d')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Load thumbnail
        thumb_img = self.load_thumbnail(page_info['filename'])
        
        # Create thumbnail button
        btn_frame = tk.Frame(content_frame, bg='#3d3d3d', relief='sunken', bd=1)
        btn_frame.pack(side=tk.LEFT, padx=(0, 5))
        
        btn = tk.Button(btn_frame, image=thumb_img,
                       command=lambda i=idx: self.on_page_select(i),
                       bg='#3d3d3d', relief='flat',
                       cursor='hand2', bd=0)
        btn.image = thumb_img
        btn.pack(padx=2, pady=2)
        
        # Info frame
        info_frame = tk.Frame(content_frame, bg='#2d2d2d')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Page number
        page_label = tk.Label(info_frame, text=f"Page {page_info['page']}",
                             bg='#2d2d2d', fg='white', 
                             font=('Segoe UI', 9, 'bold'))
        page_label.pack(anchor='w', pady=(0, 5))
        
        # Delete button
        del_btn = tk.Button(info_frame, text="❌ Delete",
                           command=lambda f=page_info['filename']: self.on_page_delete(f),
                           bg='#f44336', fg='white',
                           font=('Segoe UI', 8), width=8, height=1)
        del_btn.pack(anchor='w')
        
        self.thumb_buttons.append(btn)
        self.thumb_images.append(thumb_img)
    
    def load_thumbnail(self, filename):
        """Load or create thumbnail image with proper size"""
        from config import FIXED_FOLDER_PATH
        path = os.path.join(FIXED_FOLDER_PATH, filename)
        
        try:
            if filename.lower().endswith(SUPPORTED_IMAGE_EXTS):
                img = Image.open(path)
                # Resize to fixed thumbnail size
                img.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            elif filename.lower().endswith(SUPPORTED_VIDEO_EXTS):
                return self.create_video_thumbnail()
        except Exception as e:
            print(f"Error loading thumbnail {filename}: {e}")
        
        # Fallback thumbnail
        return self.create_fallback_thumbnail()
    
    def create_video_thumbnail(self):
        """Create a video icon thumbnail"""
        from PIL import Image, ImageDraw
        
        img = Image.new('RGB', (THUMBNAIL_SIZE, THUMBNAIL_SIZE), '#3d3d3d')
        draw = ImageDraw.Draw(img)
        
        # Draw a play button triangle
        size = THUMBNAIL_SIZE
        triangle_size = size // 3
        x1 = (size - triangle_size) // 2
        y1 = (size - triangle_size) // 2
        x2 = x1 + triangle_size
        y2 = y1 + triangle_size
        
        draw.polygon([(x1, y1), (x1, y2), (x2, (y1+y2)//2)], fill='#ff0000')
        
        # Add "VIDEO" text
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("arial.ttf", 10)
            draw.text((5, 5), "VIDEO", fill='white', font=font)
        except:
            draw.text((5, 5), "VIDEO", fill='white')
        
        return ImageTk.PhotoImage(img)
    
    def create_fallback_thumbnail(self):
        """Create a fallback thumbnail"""
        img = Image.new('RGB', (THUMBNAIL_SIZE, THUMBNAIL_SIZE), '#3d3d3d')
        return ImageTk.PhotoImage(img)
    
    def highlight_thumbnail(self, idx):
        """Highlight the current page's thumbnail"""
        for btn in self.thumb_buttons:
            btn.config(bg='#3d3d3d')
        
        if 0 <= idx < len(self.thumb_buttons):
            self.thumb_buttons[idx].config(bg='#ffeb3b')
    
    def destroy(self):
        """Destroy sidebar"""
        if self.frame and self.frame.winfo_exists():
            self.frame.destroy()
        
        self.frame = None
        self.canvas = None
        self.thumb_frame = None
        self.thumb_buttons = []
        self.thumb_images = []
    
    def exists(self):
        """Check if sidebar exists"""
        return self.frame is not None and self.frame.winfo_exists()
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if self.canvas:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_mousewheel_linux(self, event):
        """Handle Linux mouse wheel"""
        if self.canvas:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")