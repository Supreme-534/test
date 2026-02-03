import tkinter as tk
import time
from config import ZOOM_ANIMATION_STEPS, ZOOM_ANIMATION_DELAY

class SmoothZoomEngine:
    def __init__(self, canvas, get_image_size_callback):
        self.canvas = canvas
        self.get_image_size = get_image_size_callback
        
        # State
        self.current_scale = 1.0
        self.target_scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.target_offset_x = 0
        self.target_offset_y = 0
        
        # Animation
        self.animating = False
        self.animation_steps = ZOOM_ANIMATION_STEPS
        self.animation_delay = 15  # Reduced for smoother animation
        
        # Performance optimization
        self.last_render_time = 0
        self.min_render_interval = 0.016  # ~60 FPS
        
    def zoom_to_point(self, factor, mouse_x, mouse_y, animate=True):
        """Zoom towards a specific point with SMOOTH animation"""
        # Calculate target scale with limits
        new_scale = self.current_scale * factor
        
        # Apply min/max limits
        from config import ZOOM_MIN, ZOOM_MAX
        new_scale = max(ZOOM_MIN, min(new_scale, ZOOM_MAX))
        
        if abs(new_scale - self.current_scale) < 0.01:
            return  # No significant change
        
        # Calculate new offsets for zoom-to-point
        # Convert mouse position to image coordinates
        img_x = (mouse_x - self.offset_x) / self.current_scale
        img_y = (mouse_y - self.offset_y) / self.current_scale
        
        # Calculate target offsets to keep the same image point under mouse
        self.target_offset_x = mouse_x - img_x * new_scale
        self.target_offset_y = mouse_y - img_y * new_scale
        self.target_scale = new_scale
        
        if animate:
            self.start_animation()
        else:
            self.current_scale = self.target_scale
            self.offset_x = self.target_offset_x
            self.offset_y = self.target_offset_y
            self.update_display()
    
    def start_animation(self):
        """Start smooth zoom animation"""
        if self.animating:
            return
        
        self.animating = True
        self.animation_step = 0
        self.start_scale = self.current_scale
        self.start_offset_x = self.offset_x
        self.start_offset_y = self.offset_y
        
        self.animate_step()
    
    def animate_step(self):
        """Perform one animation step - OPTIMIZED FOR SMOOTHNESS"""
        current_time = time.time()
        if current_time - self.last_render_time < self.min_render_interval:
            # Skip frame to maintain smoothness
            self.canvas.after(int(self.min_render_interval * 1000), self.animate_step)
            return
        
        if not self.animating or self.animation_step >= self.animation_steps:
            self.animating = False
            return
        
        # Calculate progress (ease-out cubic for smoothness)
        t = self.animation_step / self.animation_steps
        # Smoother easing function
        progress = 1 - (1 - t) ** 3
        
        # Interpolate values
        self.current_scale = self.start_scale + (self.target_scale - self.start_scale) * progress
        self.offset_x = self.start_offset_x + (self.target_offset_x - self.start_offset_x) * progress
        self.offset_y = self.start_offset_y + (self.target_offset_y - self.start_offset_y) * progress
        
        self.update_display()
        self.last_render_time = current_time
        
        self.animation_step += 1
        if self.animation_step < self.animation_steps:
            self.canvas.after(self.animation_delay, self.animate_step)
        else:
            self.animating = False
    
    def instant_fit(self, canvas_width, canvas_height):
        """INSTANT fit image to canvas (no animation)"""
        img_w, img_h = self.get_image_size()
        if img_w == 0 or img_h == 0:
            return
        
        # Calculate scale to fit with margin
        scale_w = canvas_width / img_w
        scale_h = canvas_height / img_h
        new_scale = min(scale_w, scale_h) * 0.95
        
        # Calculate centered offsets
        self.current_scale = new_scale
        self.target_scale = new_scale
        self.offset_x = (canvas_width - img_w * new_scale) / 2
        self.offset_y = (canvas_height - img_h * new_scale) / 2
        self.target_offset_x = self.offset_x
        self.target_offset_y = self.offset_y
        
        # Update display immediately
        if hasattr(self, 'update_display'):
            self.update_display()
    
    def reset_view(self, canvas_width, canvas_height):
        """Reset to fit image to canvas WITH smooth animation"""
        img_w, img_h = self.get_image_size()
        if img_w == 0 or img_h == 0:
            return
        
        # Calculate scale to fit with margin
        scale_w = canvas_width / img_w
        scale_h = canvas_height / img_h
        new_scale = min(scale_w, scale_h) * 0.95
        
        # Calculate centered offsets
        self.target_offset_x = (canvas_width - img_w * new_scale) / 2
        self.target_offset_y = (canvas_height - img_h * new_scale) / 2
        self.target_scale = new_scale
        
        self.start_animation()
    
    def pan(self, dx, dy):
        """Pan the image - OPTIMIZED"""
        self.offset_x += dx
        self.offset_y += dy
        self.target_offset_x = self.offset_x
        self.target_offset_y = self.offset_y
        
        # Throttle rendering during rapid panning
        current_time = time.time()
        if current_time - self.last_render_time >= self.min_render_interval:
            self.update_display()
            self.last_render_time = current_time
    
    def zoom_in_centered(self):
        """Zoom in centered on viewport"""
        from config import ZOOM_FACTOR
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.zoom_to_point(ZOOM_FACTOR, 
                         canvas_width // 2, 
                         canvas_height // 2, 
                         animate=True)
    
    def zoom_out_centered(self):
        """Zoom out centered on viewport"""
        from config import ZOOM_FACTOR
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        self.zoom_to_point(1/ZOOM_FACTOR, 
                         canvas_width // 2, 
                         canvas_height // 2, 
                         animate=True)
    
    def update_display(self):
        """Update the canvas display"""
        # This should be implemented in the media viewer
        pass
    
    def get_view_params(self):
        """Get current view parameters"""
        return {
            'scale': self.current_scale,
            'offset_x': self.offset_x,
            'offset_y': self.offset_y
        }