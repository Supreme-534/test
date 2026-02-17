import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import time
from config import *
from utils.zoom_engine import SmoothZoomEngine

class MediaViewer:
    def __init__(self, root, main_window=None):
        self.root = root
        self.main_window = main_window
        self.canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        
        # Media state
        self.current_image = None
        self.thumbnail = None  # Cached low-res version for instant preview
        self.tk_image = None
        self.current_is_video = False
        self.current_render_id = 0  # Track render versions
        
        # Video playback state
        self.video_capture = None
        self.video_playing = False
        self.video_thread = None
        self.current_video_path = None
        self.video_fps = 30
        self.video_total_frames = 0
        self.video_current_frame = 0
        
        # Video thread control
        self.video_thread_active = False
        
        # Video controls UI
        self.video_controls_frame = None
        self.play_pause_btn = None
        self.video_slider = None
        self.time_label = None
        self.slider_dragging = False
        
        # Zoom engine
        self.zoom_engine = SmoothZoomEngine(self.canvas, self.get_image_size)
        self.zoom_engine.update_display = self.render
        
        # Mouse wheel zoom
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        self.canvas.bind('<Button-4>', self.on_mouse_wheel)
        self.canvas.bind('<Button-5>', self.on_mouse_wheel)
        
        # Left-click drag for panning
        self.canvas.bind('<Button-1>', self.on_pan_start)
        self.canvas.bind('<B1-Motion>', self.on_pan_drag)
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.is_dragging = False

    def on_mouse_wheel(self, event):
        """Mouse wheel zoom handler for Windows/Linux."""
        if not self.current_image or self.video_playing:
            return

        # Linux sends Button-4/Button-5 events, Windows uses delta
        if getattr(event, 'num', None) == 4:
            factor = ZOOM_FACTOR
        elif getattr(event, 'num', None) == 5:
            factor = 1 / ZOOM_FACTOR
        else:
            delta = getattr(event, 'delta', 0)
            factor = ZOOM_FACTOR if delta > 0 else (1 / ZOOM_FACTOR)

        self.zoom_engine.zoom_to_point(factor, event.x, event.y, animate=True)

    def on_pan_start(self, event):
        """Start image pan drag."""
        if not self.current_image or self.video_playing:
            return

        self.is_dragging = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def on_pan_drag(self, event):
        """Pan image while dragging mouse."""
        if not self.is_dragging or not self.current_image or self.video_playing:
            return

        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y

        self.pan_start_x = event.x
        self.pan_start_y = event.y

        self.zoom_engine.pan(dx, dy)
    
    def load_media(self, file_info):
        """Load image or video"""
        # Stop any playing video
        self.stop_video()
        
        path = file_info['full_path']
        filename = file_info['filename'].lower()
        
        # Check if it's a video
        self.current_is_video = any(filename.endswith(ext) for ext in SUPPORTED_VIDEO_EXTS)
        
        if self.current_is_video:
            return self.load_video_simple(path)
        else:
            return self.load_image(path)
    
    def load_image(self, path):
        """Load and display image with zoom"""
        try:
            self.current_image = Image.open(path).convert('RGB')
            
            # Hide video controls
            self.hide_video_controls()
            
            # Clear video indicator
            self.canvas.delete('video_indicator')
            
            # Show canvas
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # Instant fit to window
            self.root.update_idletasks()
            canvas_width = self.canvas.winfo_width() or 800
            canvas_height = self.canvas.winfo_height() or 600
            
            self.zoom_engine.instant_fit(canvas_width, canvas_height)
            return True
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return False
    
    def load_video_simple(self, path):
        """Simple video loader that shows first frame with play button"""
        self.current_video_path = path
        
        try:
            # Load first frame as image
            success = self.load_video_frame_as_image(path)
            
            if success:
                # Add small play button overlay
                self.add_video_indicator()
                self.canvas.update_idletasks()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error loading video {path}: {e}")
            return False
    
    def load_video_frame_as_image(self, path):
        """Load first frame of video as image"""
        try:
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            
            # Get video metadata
            self.video_fps = cap.get(cv2.CAP_PROP_FPS) or 30
            self.video_total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            cap.release()
            
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_image = Image.fromarray(frame_rgb)
                
                # Hide video controls initially
                self.hide_video_controls()
                
                # Show canvas
                self.canvas.pack(fill=tk.BOTH, expand=True)
                
                # Fit to window
                self.root.update_idletasks()
                canvas_width = self.canvas.winfo_width() or 800
                canvas_height = self.canvas.winfo_height() or 600
                
                self.zoom_engine.instant_fit(canvas_width, canvas_height)
                return True
        except Exception as e:
            print(f"Error loading video frame: {e}")
        
        return False
    
    def add_video_indicator(self):
        """Add a play button overlay in the center"""
        # Remove existing indicator
        self.canvas.delete('video_indicator')
        
        # Get canvas size
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        # Create a transparent play button in center with white outline
        indicator_size = 80
        x = (canvas_width - indicator_size) // 2
        y = (canvas_height - indicator_size) // 2
        
        # Draw transparent play button circle with white outline
        self.canvas.create_oval(
            x, y, x + indicator_size, y + indicator_size,
            fill='', outline='white', width=3,
            tags='video_indicator'
        )
        
        # Add play triangle (white)
        center_x = x + indicator_size // 2
        center_y = y + indicator_size // 2
        triangle_size = 30
        triangle_points = [
            center_x - 10, center_y - triangle_size // 2,
            center_x - 10, center_y + triangle_size // 2,
            center_x + triangle_size // 2, center_y
        ]
        self.canvas.create_polygon(
            triangle_points,
            fill='white', outline='white', width=2,
            tags='video_indicator'
        )
        
        # Make clickable
        self.canvas.tag_bind('video_indicator', '<Button-1>', 
                           lambda e: self.start_video_playback())
    
    def start_video_playback(self):
        """Start playing video in-canvas"""
        if not self.current_video_path:
            return
        
        # Remove play button
        self.canvas.delete('video_indicator')
        
        # Show video controls
        self.show_video_controls()
        
        # Start playback
        self.video_playing = True
        self.video_thread_active = True
        self.video_current_frame = 0
        
        # Start playback thread
        thread = threading.Thread(target=self.video_playback_thread, daemon=True)
        thread.start()
    
    def show_video_controls(self):
        """Show video playback controls at the bottom"""
        if self.video_controls_frame:
            self.video_controls_frame.pack(side=tk.BOTTOM, fill=tk.X)
            return
        
        # Create controls frame at the very bottom
        self.video_controls_frame = tk.Frame(self.root, bg='#1a1a1a', height=50)
        self.video_controls_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.video_controls_frame.pack_propagate(False)
        
        # Time label
        self.time_label = tk.Label(
            self.video_controls_frame,
            text="0:00 / 0:00",
            font=('Segoe UI', 9),
            bg='#1a1a1a',
            fg='white'
        )
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        # Play/Pause button
        self.play_pause_btn = tk.Button(
            self.video_controls_frame,
            text="⏸",
            font=('Segoe UI', 14),
            bg='#333333',
            fg='white',
            relief='flat',
            cursor='hand2',
            width=3,
            command=self.toggle_playback
        )
        self.play_pause_btn.pack(side=tk.LEFT, padx=5)
        
        # Video slider - light gray normally, white on hover
        self.video_slider = tk.Scale(
            self.video_controls_frame,
            from_=0,
            to=max(1, self.video_total_frames - 1),
            orient=tk.HORIZONTAL,
            bg='#1a1a1a',
            fg='#aaaaaa',  # Light gray normally
            highlightthickness=0,
            troughcolor='#333333',
            activebackground='white',  # White when hovering/dragging
            showvalue=0,
            sliderlength=15,
            sliderrelief='flat',
            bd=0,
            width=10,
            command=self.on_slider_change
        )
        self.video_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Bind slider events for hover effect
        self.video_slider.bind('<ButtonPress-1>', self.on_slider_press)
        self.video_slider.bind('<ButtonRelease-1>', self.on_slider_release)
        self.video_slider.bind('<Enter>', lambda e: self.video_slider.config(fg='white'))
        self.video_slider.bind('<Leave>', lambda e: self.video_slider.config(fg='#aaaaaa'))
    
    def hide_video_controls(self):
        """Hide video controls"""
        if self.video_controls_frame:
            self.video_controls_frame.pack_forget()
    
    def toggle_playback(self):
        """Toggle play/pause"""
        self.video_playing = not self.video_playing
        if self.video_playing:
            self.play_pause_btn.config(text="⏸")
        else:
            self.play_pause_btn.config(text="▶")
    
    def on_slider_press(self, event):
        """Handle slider press - pause playback while dragging"""
        self.slider_dragging = True
        self.video_playing = False
        self.play_pause_btn.config(text="▶")
    
    def on_slider_release(self, event):
        """Handle slider release - seek to position"""
        self.slider_dragging = False
        # Seek will happen automatically through on_slider_change
    
    def on_slider_change(self, value):
        """Handle slider value change"""
        if self.slider_dragging or not self.video_playing:
            # Update current frame when user drags slider
            self.video_current_frame = int(float(value))
    
    def video_playback_thread(self):
        """Video playback thread"""
        try:
            cap = cv2.VideoCapture(self.current_video_path)
            
            if not cap.isOpened():
                print(f"Cannot open video file: {self.current_video_path}")
                return
            
            # Use 60 FPS for smoother playback
            fps = 60
            frame_delay = 1.0 / fps
            
            # Calculate frame skip for target FPS
            video_fps = self.video_fps
            frame_skip = max(1, int(video_fps / fps))
            
            while self.video_thread_active:
                if self.video_playing and not self.slider_dragging:
                    # Set frame position
                    cap.set(cv2.CAP_PROP_POS_FRAMES, self.video_current_frame)
                    
                    # Read frame
                    ret, frame = cap.read()
                    
                    if not ret:
                        # Loop video
                        self.video_current_frame = 0
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    
                    # Convert frame to PIL Image
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.current_image = Image.fromarray(frame_rgb)
                    
                    # Update display
                    self.root.after(0, self.render_video_frame)
                    
                    # Update slider and time
                    self.root.after(0, self.update_video_ui)
                    
                    # Next frame with skip for target FPS
                    self.video_current_frame += frame_skip
                    
                    if self.video_current_frame >= self.video_total_frames:
                        self.video_current_frame = 0
                
                time.sleep(frame_delay)
                
        except Exception as e:
            print(f"Video playback error: {e}")
        finally:
            if 'cap' in locals():
                cap.release()
            self.video_thread_active = False
    
    def render_video_frame(self):
        """Render current video frame to canvas - preserve original quality, no downscaling"""
        if not self.current_image:
            return
        
        # Clear canvas
        self.canvas.delete('all')
        
        # Get canvas size
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        # Get original image size
        img_w, img_h = self.current_image.size
        
        # Calculate display size - NEVER downscale, only upscale if needed
        aspect = img_w / img_h
        
        if canvas_width / canvas_height > aspect:
            # Fit to height
            display_h = min(canvas_height, img_h)  # Don't exceed original height
            display_w = int(display_h * aspect)
        else:
            # Fit to width
            display_w = min(canvas_width, img_w)  # Don't exceed original width
            display_h = int(display_w / aspect)
        
        # Only upscale if canvas is bigger than video
        if display_w > img_w or display_h > img_h:
            # Upscale with high quality
            resized = self.current_image.resize((display_w, display_h), Image.Resampling.BICUBIC)
        else:
            # Use original quality - no downscaling
            resized = self.current_image
            display_w = img_w
            display_h = img_h
        
        self.tk_image = ImageTk.PhotoImage(resized)
        
        # Center image on canvas
        x = (canvas_width - display_w) // 2
        y = (canvas_height - display_h) // 2
        
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.tk_image)
    
    def update_video_ui(self):
        """Update video slider and time label"""
        if not self.slider_dragging:
            self.video_slider.set(self.video_current_frame)
        
        # Update time label
        current_time = self.video_current_frame / self.video_fps
        total_time = self.video_total_frames / self.video_fps
        
        current_min = int(current_time // 60)
        current_sec = int(current_time % 60)
        total_min = int(total_time // 60)
        total_sec = int(total_time % 60)
        
        time_str = f"{current_min}:{current_sec:02d} / {total_min}:{total_sec:02d}"
        self.time_label.config(text=time_str)
    
    def stop_video(self):
        """Stop video playback"""
        self.video_thread_active = False
        self.video_playing = False
        
        # Hide video controls
        self.hide_video_controls()
        
        # Remove video indicator
        self.canvas.delete('video_indicator')
        
        # Reset video flag
        self.current_is_video = False
    
    def render(self):
        """Render current image to canvas (for images only)"""
        if not self.current_image or self.video_playing:
            return
        
        # Clear canvas except video indicator
        all_items = self.canvas.find_all()
        for item in all_items:
            tags = self.canvas.gettags(item)
            if 'video_indicator' not in tags:
                self.canvas.delete(item)
        
        # Get view parameters
        params = self.zoom_engine.get_view_params()
        scale = params['scale']
        offset_x = params['offset_x']
        offset_y = params['offset_y']
        
        # Calculate display size
        img_w, img_h = self.current_image.size
        display_w = max(1, int(img_w * scale))
        display_h = max(1, int(img_h * scale))
        
        # Create resized image
        if scale >= 1.0:
            method = Image.Resampling.NEAREST
        else:
            method = Image.Resampling.LANCZOS
        
        resized = self.current_image.resize((display_w, display_h), method)
        self.tk_image = ImageTk.PhotoImage(resized)
        
        # Draw image
        self.canvas.create_image(offset_x, offset_y, anchor=tk.NW, image=self.tk_image)
        
        # Ensure video indicator is on top if present
        if self.current_is_video:
            self.canvas.tag_raise('video_indicator')
    
    def get_image_size(self):
        """Get current image size for zoom engine"""
        if self.current_image:
            return self.current_image.size
        return (0, 0)
    
    def zoom_in(self):
        """Zoom in centered with animation"""
        if not self.video_playing:
            self.zoom_engine.zoom_in_centered()
    
    def zoom_out(self):
        """Zoom out centered with animation"""
        if not self.video_playing:
            self.zoom_engine.zoom_out_centered()
    
    def reset_zoom(self):
        """Reset to fit window with animation"""
        if not self.video_playing:
            self.root.update_idletasks()
            canvas_width = self.canvas.winfo_width() or 800
            canvas_height = self.canvas.winfo_height() or 600
            
            if canvas_width > 1 and canvas_height > 1:
                self.zoom_engine.reset_view(canvas_width, canvas_height)
    
    def toggle_video_playback(self):
        """Toggle video play/pause - for spacebar compatibility"""
        if self.current_is_video:
            if self.video_playing or self.video_controls_frame:
                # Video is already playing or controls are visible, toggle playback
                self.toggle_playback()
            else:
                # Start video playback
                self.start_video_playback()
        else:
            # For images, reset zoom
            self.reset_zoom()
