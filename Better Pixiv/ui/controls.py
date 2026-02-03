import tkinter as tk
import pyperclip
from config import *
from ui.styles import ModernStyle

class ControlPanel:
    def __init__(self, root, file_manager, database, state, 
                 on_points_add, on_nice_add, on_delete, on_move, on_artist_click):
        self.root = root
        self.file_manager = file_manager
        self.database = database
        self.state = state
        self.on_points_add = on_points_add
        self.on_nice_add = on_nice_add
        self.on_delete = on_delete
        self.on_move = on_move
        self.on_artist_click = on_artist_click
        
        self.style = ModernStyle(root)
        
        # UI elements
        self.info_frame = None
        self.title_label = None
        self.artist_label = None
        self.points_label = None
        self.nice_label = None
        self.points_btn = None
        self.nice_btn = None
        self.delete_btn = None
        self.sfw_btn = None
        self.junko_btn = None
        
        self.create_controls()
    
    def create_controls(self):
        """Create all control elements"""
        # Top-left: Artwork info
        self.create_info_panel()
        
        # Top-right: Delete button
        self.create_delete_button()
        
        # Bottom-right: Points/Nice buttons (HORIZONTAL)
        self.create_counter_panel_horizontal()
        
        # Bottom-left: SFW/Junko buttons
        self.create_move_buttons()
    
    def create_info_panel(self):
        """Create clickable artwork info panel"""
        self.info_frame = tk.Frame(self.root, bg='#2d2d2d')
        self.info_frame.place(relx=0.0, rely=0.0, anchor='nw', x=10, y=10)
        
        # Artwork title
        self.title_label = tk.Label(self.info_frame, text="",
                                   font=('Segoe UI', 10),
                                   bg='#2d2d2d', fg='white',
                                   cursor='hand2',
                                   wraplength=400)
        self.title_label.pack(anchor='w')
        self.title_label.bind('<Button-1>', self.copy_artwork_link)
        
        # Artist name
        self.artist_label = tk.Label(self.info_frame, text="",
                                   font=('Segoe UI', 8),
                                   bg='#2d2d2d', fg='#aaaaaa',
                                   cursor='hand2')
        self.artist_label.pack(anchor='w')
        self.artist_label.bind('<Button-1>', lambda e: self.on_artist_click())
    
    def create_delete_button(self):
        """Create delete button"""
        self.delete_btn = tk.Button(self.root, text="🗑️ Delete", 
                                   command=self.on_delete,
                                   font=('Segoe UI', 10),
                                   bg='#f44336', fg='white',
                                   relief='flat', cursor='hand2')
        self.delete_btn.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
    
    def create_counter_panel_horizontal(self):
        """Create points and nice counter panel HORIZONTALLY"""
        # Main container frame
        counter_container = tk.Frame(self.root, bg='#2d2d2d')
        counter_container.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)
        
        # Points section (left side)
        points_frame = tk.Frame(counter_container, bg='#2d2d2d')
        points_frame.pack(side=tk.LEFT, padx=10)
        
        # Points label
        self.points_label = tk.Label(points_frame, text="0",
                                    font=('Segoe UI', 14, 'bold'),
                                    bg='#2d2d2d', fg='white',
                                    width=3, height=1)
        self.points_label.pack()
        
        # Points button
        self.points_btn = tk.Button(points_frame, text="💦",
                                   command=self.on_points_add,
                                   font=('Segoe UI', 16),
                                   bg='#00bcd4', fg='white',
                                   relief='flat', cursor='hand2',
                                   width=3, height=1)
        self.points_btn.pack(pady=5)
        
        # Nice section (right side)
        nice_frame = tk.Frame(counter_container, bg='#2d2d2d')
        nice_frame.pack(side=tk.LEFT, padx=10)
        
        # Nice label
        self.nice_label = tk.Label(nice_frame, text="0",
                                  font=('Segoe UI', 14, 'bold'),
                                  bg='#2d2d2d', fg='white',
                                  width=3, height=1)
        self.nice_label.pack()
        
        # Nice button
        self.nice_btn = tk.Button(nice_frame, text="😭",
                                 command=self.on_nice_add,
                                 font=('Segoe UI', 16),
                                 bg='#ff9800', fg='white',
                                 relief='flat', cursor='hand2',
                                 width=3, height=1)
        self.nice_btn.pack(pady=5)
        
        # Store container reference
        self.counter_container = counter_container
    
    def create_move_buttons(self):
        """Create SFW and Junko move buttons"""
        move_container = tk.Frame(self.root, bg='#2d2d2d')
        move_container.place(relx=0.0, rely=1.0, anchor='sw', x=10, y=-10)
        
        # SFW button (green)
        self.sfw_btn = tk.Button(move_container, text="SFW", 
                                command=lambda: self.on_move('sfw'),
                                font=('Segoe UI', 10),
                                bg='#4caf50', fg='white',
                                relief='flat', cursor='hand2',
                                width=6, height=1)
        self.sfw_btn.pack(pady=2)
        
        # Junko button (RED)
        self.junko_btn = tk.Button(move_container, text="Junko", 
                                  command=lambda: self.on_move('junko'),
                                  font=('Segoe UI', 10),
                                  bg='#f44336', fg='white',
                                  relief='flat', cursor='hand2',
                                  width=6, height=1)
        self.junko_btn.pack(pady=2)
    
    def copy_artwork_link(self, event=None):
        """Copy Pixiv artwork link to clipboard"""
        url = self.state.get_pixiv_url()
        if url:
            pyperclip.copy(url)
            
            original_text = self.title_label.cget('text')
            self.title_label.config(text="✓ Copied!", fg='#4caf50')
            
            self.root.after(1000, lambda: self.update_info())
    
    def update_info(self):
        """Update artwork info labels and counters"""
        current_file = self.state.get_current_file()
        if not current_file:
            return
        
        # Update title
        title = current_file.get('title', 'Untitled')
        if len(title) > 50:
            title = title[:50] + "..."
        self.title_label.config(text=title, fg='white')
        
        # Update artist
        artist = current_file.get('artist', 'Unknown')
        self.artist_label.config(text=f"by {artist}", fg='#aaaaaa')
        
        # Update counters for the POST
        post_id = self.state.current_post_id
        if post_id:
            points = self.database.get_points(post_id)
            nice = self.database.get_nice(post_id)
            
            self.points_label.config(text=str(points))
            self.nice_label.config(text=str(nice))
    
    def show_delete_button(self, show=True):
        """Show or hide delete button"""
        if show:
            self.delete_btn.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
        else:
            self.delete_btn.place_forget()
    
    def hide_all(self):
        """Hide all controls (for artist menu)"""
        self.info_frame.place_forget()
        self.delete_btn.place_forget()
        self.counter_container.place_forget()
        self.sfw_btn.master.place_forget()
    
    def show_all(self):
        """Show all controls (return from artist menu)"""
        self.info_frame.place(relx=0.0, rely=0.0, anchor='nw', x=10, y=10)
        self.delete_btn.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
        self.counter_container.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)
        self.sfw_btn.master.place(relx=0.0, rely=1.0, anchor='sw', x=10, y=-10)
    
    def show_for_video(self):
        """Show controls optimized for video mode (overlay)"""
        # Keep all controls visible but adjust positions
        self.info_frame.place(relx=0.0, rely=0.0, anchor='nw', x=10, y=10)
        self.delete_btn.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
        self.counter_container.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)
        self.sfw_btn.master.place(relx=0.0, rely=1.0, anchor='sw', x=10, y=-10)
    
    def hide_for_video_fullscreen(self):
        """Hide controls during fullscreen video"""
        # Hide all controls during fullscreen video
        self.info_frame.place_forget()
        self.delete_btn.place_forget()
        self.counter_container.place_forget()
        self.sfw_btn.master.place_forget()
    
    def show_after_video(self):
        """Show controls after exiting video mode"""
        self.show_all()  # Use existing show_all method
    
    def set_video_mode(self, is_video):
        """Adjust controls for video mode"""
        if is_video:
            # For videos, ensure delete button is visible
            self.delete_btn.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
        else:
            # For images, use normal positioning
            self.show_all()
