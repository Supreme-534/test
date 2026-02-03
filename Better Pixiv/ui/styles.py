import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk

class ModernStyle:
    def __init__(self, root):
        self.root = root
        self.setup_style()
    
    def setup_style(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        # Use 'clam' theme as base for more customization
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Modern.TButton',
                       padding=8,
                       relief='flat',
                       background='#4a4a4a',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Modern.TButton',
                 background=[('active', '#5a5a5a'), ('pressed', '#3a3a3a')],
                 foreground=[('active', '#ffffff')])
        
        # Special button styles
        style.configure('Points.TButton',
                       background='#00bcd4',
                       foreground='white')
        
        style.map('Points.TButton',
                 background=[('active', '#00acc1'), ('pressed', '#0097a7')])
        
        style.configure('Nice.TButton',
                       background='#ff9800',
                       foreground='white')
        
        style.map('Nice.TButton',
                 background=[('active', '#f57c00'), ('pressed', '#ef6c00')])
        
        style.configure('Delete.TButton',
                       background='#f44336',
                       foreground='white')
        
        style.map('Delete.TButton',
                 background=[('active', '#e53935'), ('pressed', '#d32f2f')])
        
        style.configure('Move.TButton',
                       background='#4caf50',
                       foreground='white')
        
        style.map('Move.TButton',
                 background=[('active', '#43a047'), ('pressed', '#388e3c')])
    
    def create_modern_button(self, parent, text, command, style='Modern.TButton'):
        """Create a modern styled button"""
        btn = ttk.Button(parent, text=text, command=command, style=style)
        return btn
    
    def create_emoji_button(self, parent, emoji, command, style_class):
        """Create button with proper emoji rendering using image icons"""
        # Create emoji as image for consistent rendering
        if emoji == "💦":
            bg_color = '#00bcd4'  # Blue for Points
            emoji_img = self.create_emoji_image("💦", bg_color)
        elif emoji == "😭":
            bg_color = '#ff9800'  # Orange for Nice
            emoji_img = self.create_emoji_image("😭", bg_color)
        else:
            bg_color = '#4a4a4a'
            emoji_img = self.create_emoji_image(emoji, bg_color)
        
        frame = tk.Frame(parent, bg='#2d2d2d', highlightthickness=0)
        
        # Create button with image
        btn = tk.Button(frame, image=emoji_img,
                       command=command,
                       bg=bg_color, activebackground=bg_color,
                       relief='flat', borderwidth=0,
                       cursor='hand2')
        btn.image = emoji_img  # Keep reference
        btn.pack(padx=10, pady=5)
        
        # Hover effects
        btn.bind('<Enter>', lambda e: self.on_button_hover(e, style_class, True))
        btn.bind('<Leave>', lambda e: self.on_button_hover(e, style_class, False))
        
        return frame
    
    def create_emoji_image(self, emoji, bg_color):
        """Create an image with emoji for consistent rendering"""
        # Try to render using system font first
        try:
            # Create image with emoji
            from PIL import Image, ImageDraw, ImageFont
            
            img_size = 32
            img = Image.new('RGBA', (img_size, img_size), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Try different emoji fonts
            font_names = [
                'Segoe UI Emoji',
                'Apple Color Emoji',
                'Noto Color Emoji',
                'DejaVu Sans',
                'Arial'
            ]
            
            font = None
            for font_name in font_names:
                try:
                    font = ImageFont.truetype(font_name, 24)
                    break
                except:
                    continue
            
            if font:
                # Calculate text position
                text_bbox = draw.textbbox((0, 0), emoji, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                x = (img_size - text_width) // 2
                y = (img_size - text_height) // 2
                
                # Draw emoji
                draw.text((x, y), emoji, font=font, fill='white')
            
            return ImageTk.PhotoImage(img)
        except:
            # Fallback: create colored circle with text
            from PIL import Image, ImageDraw, ImageFont
            
            img_size = 32
            img = Image.new('RGBA', (img_size, img_size), color=bg_color)
            draw = ImageDraw.Draw(img)
            
            # Draw circle
            draw.ellipse([2, 2, img_size-2, img_size-2], fill=bg_color, outline='white', width=1)
            
            # Draw text (emoji might not render, use fallback)
            if emoji == "💦":
                draw.text((8, 6), "P", fill='white', font=ImageFont.load_default())
            elif emoji == "😭":
                draw.text((8, 6), "N", fill='white', font=ImageFont.load_default())
            else:
                draw.text((8, 6), emoji, fill='white', font=ImageFont.load_default())
            
            return ImageTk.PhotoImage(img)
    
    def on_button_hover(self, event, style_class, is_hover):
        """Handle button hover effects"""
        btn = event.widget
        
        # Define hover colors based on button type
        hover_colors = {
            'Points': ('#00acc1', '#00bcd4'),  # (hover, normal)
            'Nice': ('#f57c00', '#ff9800'),
            'Delete': ('#e53935', '#f44336'),
            'Move': ('#43a047', '#4caf50'),
            'Modern': ('#5a5a5a', '#4a4a4a')
        }
        
        if is_hover and style_class in hover_colors:
            btn.config(bg=hover_colors[style_class][0])
        elif style_class in hover_colors:
            btn.config(bg=hover_colors[style_class][1])
    
    def create_counter_label(self, parent, initial_value="0"):
        """Create modern counter label"""
        label = tk.Label(parent, text=initial_value,
                        font=('Segoe UI', 12, 'bold'),
                        bg='#2d2d2d', fg='white',
                        width=4, height=1)
        return label
    
    def create_info_label(self, parent, text, font_size=10, fg_color='white'):
        """Create clickable info label"""
        label = tk.Label(parent, text=text,
                        font=('Segoe UI', font_size),
                        bg='#2d2d2d', fg=fg_color,
                        cursor='hand2',
                        wraplength=400)
        return label