import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import time
from config import *
from utils.zoom_engine import SmoothZoomEngine

class MediaViewer:
    def __init__(self, root, main_window=None):  # Make main_window optional
        self.root = root
        self.main_window = main_window  # Optional reference to main window
        self.canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        
        # Media state
        self.current_image = None
        self.tk_image = None
        self.current_is_video = False
        
        # Video playback state
        self.video_capture = None
        self.video_playing = False
        self.video_thread = None
        self.video_label = None
        self.video_controls = None
        self.current_video_path = None
        
        # Zoom engine
        self.zoom_engine = SmoothZoomEngine(self.canvas, self.get_image_size)
        self.zoom_engine.update_display = self.render
    
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
            
            # Hide video elements
            if self.video_label:
                self.video_label.pack_forget()
            if self.video_controls:
                self.video_controls.pack_forget()
            
            # Show canvas
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # INSTANT fit to window (no animation)
            self.root.update_idletasks()
            canvas_width = self.canvas.winfo_width() or 800
            canvas_height = self.canvas.winfo_height() or 600
            
            self.zoom_engine.instant_fit(canvas_width, canvas_height)
            return True
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return False
    
    def load_video_simple(self, path):
        """Simple video loader that shows first frame"""
        print(f"Loading video: {path}")
        
        try:
            # Load first frame as image
            success = self.load_video_frame_as_image(path)
            
            if success:
                # Add video indicator overlay
                self.add_video_indicator()
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
            cap.release()
            
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_image = Image.fromarray(frame_rgb)
                
                # Hide any video-specific elements
                if self.video_label:
                    self.video_label.pack_forget()
                if self.video_controls:
                    self.video_controls.pack_forget()
                
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
        """Add a small video indicator on the canvas"""
        # Remove existing indicator
        if hasattr(self, 'video_indicator') and self.video_indicator:
            try:
                self.canvas.delete(self.video_indicator)
            except:
                pass
        
        # Create video play button indicator
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        
        # Create a play button overlay
        indicator_size = 80
        x = canvas_width - indicator_size - 20
        y = canvas_height - indicator_size - 20
        
        # Draw play button
        self.video_indicator = self.canvas.create_oval(
            x, y, x + indicator_size, y + indicator_size,
            fill='#f44336', outline='white', width=2
        )
        
        # Add play triangle
        triangle_points = [
            x + indicator_size//2 + 5, y + indicator_size//2 - 10,
            x + indicator_size//2 + 5, y + indicator_size//2 + 10,
            x + indicator_size//2 + 20, y + indicator_size//2
        ]
        self.canvas.create_polygon(
            triangle_points,
            fill='white', outline='white'
        )
        
        # Make it clickable
        self.canvas.tag_bind(self.video_indicator, '<Button-1>', 
                           lambda e: self.play_video_popup())
    
    def play_video_popup(self):
        """Play video in a popup window"""
        if not self.current_video_path:
            return
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Video Player")
        popup.geometry("800x600")
        popup.configure(bg='black')
        
        # Create video label
        video_label = tk.Label(popup, bg='black')
        video_label.pack(fill=tk.BOTH, expand=True)
        
        # Create controls
        controls = tk.Frame(popup, bg='#2d2d2d', height=40)
        controls.pack(side=tk.BOTTOM, fill=tk.X)
        controls.pack_propagate(False)
        
        # Add control buttons
        control_frame = tk.Frame(controls, bg='#00000000')
        control_frame.pack(pady=5)
        
        # Play/Pause button
        play_pause_btn = tk.Button(control_frame, text="⏸", 
                                 font=('Segoe UI', 12),
                                 bg='#4caf50', fg='white',
                                 relief='flat', cursor='hand2',
                                 width=3)
        play_pause_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = tk.Button(control_frame, text="✕", 
                            command=popup.destroy,
                            font=('Segoe UI', 12),
                            bg='#f44336', fg='white',
                            relief='flat', cursor='hand2',
                            width=3)
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Start video playback
        self.play_video_in_label(self.current_video_path, video_label, play_pause_btn, popup)
    
    def play_video_in_label(self, path, video_label, play_pause_btn, popup):
        """Play video in a label"""
        def playback_thread():
            try:
                cap = cv2.VideoCapture(path)
                
                if not cap.isOpened():
                    print(f"Cannot open video file: {path}")
                    return
                
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps <= 0:
                    fps = 30
                
                frame_delay = 1.0 / fps
                playing = True
                
                def toggle_playback():
                    nonlocal playing
                    playing = not playing
                    if playing:
                        play_pause_btn.config(text="⏸")
                    else:
                        play_pause_btn.config(text="▶")
                
                play_pause_btn.config(command=toggle_playback)
                
                while True:
                    if playing:
                        ret, frame = cap.read()
                        
                        if not ret:
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            continue
                        
                        # Convert and display frame
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame_rgb)
                        
                        # Resize to fit label
                        label_width = video_label.winfo_width()
                        label_height = video_label.winfo_height()
                        
                        if label_width > 1 and label_height > 1:
                            img_width, img_height = img.size
                            aspect = img_width / img_height
                            
                            if label_width / label_height > aspect:
                                new_height = label_height
                                new_width = int(label_height * aspect)
                            else:
                                new_width = label_width
                                new_height = int(label_width / aspect)
                            
                            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        tk_img = ImageTk.PhotoImage(img)
                        
                        popup.after(0, lambda: video_label.config(image=tk_img) or setattr(video_label, 'image', tk_img))
                    
                    time.sleep(frame_delay)
                    
            except Exception as e:
                print(f"Video playback error: {e}")
            finally:
                if 'cap' in locals():
                    cap.release()
        
        # Start playback thread
        thread = threading.Thread(target=playback_thread, daemon=True)
        thread.start()
    
    def stop_video(self):
        """Stop video playback"""
        self.video_playing = False
        
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        
        if self.video_label:
            self.video_label.pack_forget()
        
        if self.video_controls:
            self.video_controls.pack_forget()
        
        # Remove video indicator
        if hasattr(self, 'video_indicator'):
            try:
                self.canvas.delete(self.video_indicator)
            except:
                pass
        
        self.current_is_video = False
    
    def render(self):
        """Render current image to canvas"""
        if not self.current_image:
            return
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Get view parameters
        params = self.zoom_engine.get_view_params()
        scale = params['scale']
        offset_x = params['offset_x']
        offset_y = params['offset_y']
        
        # Calculate display size
        img_w, img_h = self.current_image.size
        display_w = max(1, int(img_w * scale))
        display_h = max(1, int(img_h * scale))
        
        # Create new image
        if scale >= 1.0:
            method = Image.Resampling.NEAREST
        else:
            method = Image.Resampling.LANCZOS
        
        resized = self.current_image.resize((display_w, display_h), method)
        self.tk_image = ImageTk.PhotoImage(resized)
        
        # Draw image
        self.canvas.create_image(offset_x, offset_y, anchor=tk.NW, image=self.tk_image)
    
    def get_image_size(self):
        """Get current image size for zoom engine"""
        if self.current_image:
            return self.current_image.size
        return (0, 0)
    
    def zoom_in(self):
        """Zoom in centered with animation"""
        if not self.current_is_video:
            self.zoom_engine.zoom_in_centered()
    
    def zoom_out(self):
        """Zoom out centered with animation"""
        if not self.current_is_video:
            self.zoom_engine.zoom_out_centered()
    
    def reset_zoom(self):
        """Reset to fit window with animation"""
        if not self.current_is_video:
            self.root.update_idletasks()
            canvas_width = self.canvas.winfo_width() or 800
            canvas_height = self.canvas.winfo_height() or 600
            
            if canvas_width > 1 and canvas_height > 1:
                self.zoom_engine.reset_view(canvas_width, canvas_height)
    
    def toggle_video_playback(self):
        """Toggle video play/pause - for spacebar compatibility"""
        # For now, just reset zoom for images
        if not self.current_is_video:
            self.reset_zoom()
