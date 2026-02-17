import tkinter as tk
from tkinter import ttk
from config import *
from core.file_manager import FileManager
from core.database import Database
from core.state_manager import AppState
from ui.media_viewer import MediaViewer
from ui.sidebar import Sidebar
from ui.artist_menu import ArtistMenu
from ui.controls import ControlPanel
from ui.styles import ModernStyle
import random

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Core components
        self.file_manager = FileManager()
        self.database = Database()
        self.state = AppState()
        
        # Navigation system
        self.random_list = []
        self.current_random_index = 0
        
        # Track modes
        self.in_artist_menu = False
        self.back_button = None
        
        # Generate random list
        self.generate_random_list()
        
        # UI components
        self.style = ModernStyle(root)
        self.media_viewer = MediaViewer(root, self)  # Pass self as second argument
        self.sidebar = Sidebar(root, self.on_page_select, self.on_page_delete)
        self.artist_menu = ArtistMenu(root, self.on_back_from_artist, self.on_artist_work_select)
        
        # Control panel
        self.controls = ControlPanel(
            root, self.file_manager, self.database, self.state,
            on_points_add=self.add_points,
            on_nice_add=self.add_nice,
            on_delete=self.delete_current,
            on_move=self.move_current,
            on_artist_click=self.show_artist_menu
        )
        
        # Bind shortcuts BEFORE loading first media
        self.bind_shortcuts()
        
        # Load first media AFTER UI is ready
        self.root.after(100, self.load_first_media)
    
    def setup_window(self):
        """Setup main window"""
        self.root.title("Pixiv Offline Viewer")
        self.root.state('zoomed')
        self.root.minsize(800, 600)
        self.root.configure(bg='black')
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<space>', self.handle_spacebar)
        self.root.bind('<Right>', lambda e: self.handle_right_arrow())
        self.root.bind('<Left>', lambda e: self.handle_left_arrow())
        self.root.bind('<Up>', lambda e: self.prev_page())
        self.root.bind('<Down>', lambda e: self.next_page())
        self.root.bind('+', lambda e: self.media_viewer.zoom_in())
        self.root.bind('-', lambda e: self.media_viewer.zoom_out())
        self.root.bind('0', lambda e: self.media_viewer.reset_zoom())
    
    def handle_spacebar(self, event):
        """Handle spacebar without triggering buttons"""
        focused = self.root.focus_get()
        if isinstance(focused, (tk.Button, ttk.Button)):
            focused.focus_set()
            return
        self.media_viewer.toggle_video_playback()
    
    def generate_random_list(self):
        """Generate fixed random list at startup"""
        if self.file_manager.all_posts:
            all_posts = list(self.file_manager.all_posts.keys())
            random.shuffle(all_posts)
            self.random_list = all_posts
            self.current_random_index = 0
            print(f"Generated random list with {len(self.random_list)} posts")
    
    def load_first_media(self):
        """Load first media - ENFORCE VIDEO-FIRST RULE"""
        print("\n" + "="*60)
        print("LOADING FIRST MEDIA")
        print("="*60)
        
        if not self.random_list:
            print("ERROR: No files found!")
            return
        
        # Get ALL video posts
        video_posts = self.file_manager.get_video_posts()
        print(f"\nVideo posts from file manager: {len(video_posts)}")
        
        if video_posts:
            print(f"\nLooking for videos in random list...")
            print(f"Random list has {len(self.random_list)} posts")
            
            # Find ALL videos in random list
            video_indices = []
            for i, post_id in enumerate(self.random_list):
                if post_id in video_posts:
                    video_indices.append(i)
            
            if video_indices:
                # Pick first video in random list
                first_video_index = video_indices[0]
                self.current_random_index = first_video_index
                post_id = self.random_list[first_video_index]
                
                print(f"\n✓ Loading video: {post_id} (index {first_video_index})")
                self.load_work(post_id)
                return
            else:
                print("\n⚠ WARNING: Video posts exist but none found in random list!")
                print("This means random list was generated before videos were loaded.")
        else:
            print("\nNo video posts found (0 videos in database)")
        
        # Fallback: Load first random post
        print(f"\nLoading first random post: {self.random_list[0]}")
        self.load_work(self.random_list[0])
    
    def handle_right_arrow(self):
        """Right arrow - next in current mode"""
        if self.in_artist_menu:
            # We're viewing the artist thumbnail grid - arrows do NOTHING
            return
        elif self.state.mode == 'artist' and self.state.artist_works:
            # We selected a work from artist menu and are browsing that artist's works
            next_post_id = self.state.next_in_artist_mode()
            if next_post_id:
                self.load_work(next_post_id)
            return
        else:
            # Random mode
            if not self.random_list:
                return
            
            self.current_random_index = (self.current_random_index + 1) % len(self.random_list)
            self.load_work(self.random_list[self.current_random_index])
    
    def handle_left_arrow(self):
        """Left arrow - previous in current mode"""
        if self.in_artist_menu:
            # We're viewing the artist thumbnail grid - arrows do NOTHING
            return
        elif self.state.mode == 'artist' and self.state.artist_works:
            # We selected a work from artist menu and are browsing that artist's works
            prev_post_id = self.state.prev_in_artist_mode()
            if prev_post_id:
                self.load_work(prev_post_id)
            return
        else:
            # Random mode
            if not self.random_list:
                return
            
            self.current_random_index = (self.current_random_index - 1) % len(self.random_list)
            self.load_work(self.random_list[self.current_random_index])
    
    def load_work(self, post_id):
        """Load a specific work"""
        work_files = self.file_manager.get_post_files(post_id)
        if not work_files:
            return
        
        self.state.set_work(post_id, work_files)
        self.root.update_idletasks()
        self.update_display()
        
        if post_id in self.random_list:
            self.current_random_index = self.random_list.index(post_id)
    
    def update_display(self):
        """Update all UI elements for current work"""
        current_file = self.state.get_current_file()
        if not current_file:
            return
        
        # Load media
        success = self.media_viewer.load_media(current_file)
        
        if not success:
            # Try to load next work
            self.root.after(100, self.handle_right_arrow)
            return
        
        # Update sidebar for multi-page works
        if len(self.state.current_work) > 1:
            self.sidebar.create(self.state.current_work, self.state.current_page_idx)
            self.controls.show_delete_button(False)
        else:
            self.sidebar.destroy()
            self.controls.show_delete_button(True)
        
        # Update controls
        self.controls.update_info()
        self.root.update_idletasks()
    
    def on_page_select(self, page_idx):
        """Handle page selection from sidebar"""
        self.state.current_page_idx = page_idx
        if self.sidebar.exists():
            self.sidebar.highlight_thumbnail(page_idx)
        self.update_display()
    
    def next_page(self):
        """Go to next page in current work"""
        if len(self.state.current_work) > 1:
            self.state.current_page_idx = (self.state.current_page_idx + 1) % len(self.state.current_work)
            self.update_display()
            if self.sidebar.exists():
                self.sidebar.highlight_thumbnail(self.state.current_page_idx)
    
    def prev_page(self):
        """Go to previous page in current work"""
        if len(self.state.current_work) > 1:
            self.state.current_page_idx = (self.state.current_page_idx - 1) % len(self.state.current_work)
            self.update_display()
            if self.sidebar.exists():
                self.sidebar.highlight_thumbnail(self.state.current_page_idx)
    
    def on_page_delete(self, filename):
        """Delete a specific page file"""
        post_id = None
        for work in self.state.current_work:
            if work['filename'] == filename:
                post_id = work['post_id']
                break
        
        if post_id and self.file_manager.delete_file(filename):
            self.database.remove_file(filename)
            
            if post_id in self.random_list:
                self.random_list.remove(post_id)
                if self.current_random_index >= len(self.random_list):
                    self.current_random_index = max(0, len(self.random_list) - 1)
            
            if self.state.current_post_id in self.file_manager.all_posts:
                self.load_work(self.state.current_post_id)
            else:
                if self.random_list:
                    self.current_random_index = min(self.current_random_index, len(self.random_list) - 1)
                    self.load_work(self.random_list[self.current_random_index])
    
    def show_artist_menu(self):
        """Show artist menu for current artist"""
        current_file = self.state.get_current_file()
        if not current_file:
            return
        
        artist_id = current_file['artist_id']
        artist_name = current_file['artist']
        works = self.file_manager.get_artist_works(artist_id)
        
        if not works:
            print(f"No works found for artist: {artist_name}")
            return
        
        self.media_viewer.canvas.pack_forget()
        self.media_viewer.stop_video()
        
        if self.sidebar.exists():
            self.sidebar.destroy()
        
        self.controls.hide_all()
        
        # FIX #9: Set flags properly
        self.in_artist_menu = True
        self.state.mode = 'random'  # Keep in random mode while viewing grid
        
        self.artist_menu.show(artist_id, artist_name, works)
        
        self.add_back_button()
    
    def add_back_button(self):
        """Add back button to return to random mode"""
        if self.back_button and self.back_button.winfo_exists():
            self.back_button.destroy()
        
        self.back_button = tk.Button(self.root, text="← Back to Random",
                                   command=self.on_back_from_artist,
                                   font=('Segoe UI', 12),
                                   bg='#3d3d3d', fg='white',
                                   relief='flat', cursor='hand2')
        self.back_button.place(relx=0.0, rely=0.0, anchor='nw', x=10, y=10)
    
    def on_back_from_artist(self):
        """Handle back from artist menu"""
        self.artist_menu.hide()
        
        if self.back_button and self.back_button.winfo_exists():
            self.back_button.destroy()
        
        # FIX #9: Clear flags properly
        self.in_artist_menu = False
        self.state.exit_artist_mode()
        
        self.update_display()
        self.controls.show_all()
    
    def on_artist_work_select(self, post_id):
        """Handle work selection from artist menu"""
        # Get artist info BEFORE hiding menu (while current_work still valid)
        current_file = self.state.get_current_file()
        if not current_file:
            return
        
        artist_id = current_file['artist_id']
        works = self.file_manager.get_artist_works(artist_id)
        
        # Hide artist menu
        self.artist_menu.hide()
        
        if self.back_button and self.back_button.winfo_exists():
            self.back_button.destroy()
        
        # Set artist mode PROPERLY
        self.in_artist_menu = False
        self.state.set_artist_mode(artist_id, works)
        
        # Find the index of the selected work
        for idx, work in enumerate(works):
            if work['post_id'] == post_id:
                self.state.artist_work_index = idx
                break
        
        # Load the work (this will call set_work properly with work_files)
        self.load_work(post_id)
        self.controls.show_all()
    
    def add_points(self):
        """Add point to current post"""
        if self.state.current_post_id:
            new_points = self.database.add_point(self.state.current_post_id)
            self.controls.update_info()
    
    def add_nice(self):
        """Add nice to current post"""
        if self.state.current_post_id:
            new_nice = self.database.add_nice(self.state.current_post_id)
            self.controls.update_info()
    
    def delete_current(self):
        """Delete current file"""
        current_file = self.state.get_current_file()
        if not current_file:
            return
        
        filename = current_file['filename']
        post_id = self.state.current_post_id
        
        if self.file_manager.delete_file(filename):
            self.database.remove_file(filename)
            
            if post_id in self.random_list:
                self.random_list.remove(post_id)
                if self.current_random_index >= len(self.random_list):
                    self.current_random_index = max(0, len(self.random_list) - 1)
            
            if self.file_manager.all_posts:
                if self.random_list:
                    self.current_random_index = min(self.current_random_index, len(self.random_list) - 1)
                    self.load_work(self.random_list[self.current_random_index])
            else:
                print("No more files.")
    
    def move_current(self, target_folder):
        """Move current file to target folder"""
        current_file = self.state.get_current_file()
        if not current_file:
            return
        
        filename = current_file['filename']
        post_id = self.state.current_post_id
        
        if self.file_manager.move_file(filename, target_folder):
            self.database.remove_file(filename)
            
            if post_id in self.random_list:
                self.random_list.remove(post_id)
                if self.current_random_index >= len(self.random_list):
                    self.current_random_index = max(0, len(self.random_list) - 1)
            
            if self.file_manager.all_posts:
                if self.random_list:
                    self.current_random_index = min(self.current_random_index, len(self.random_list) - 1)
                    self.load_work(self.random_list[self.current_random_index])
    
    def toggle_video_playback(self):
        """Toggle video play/pause"""
        self.media_viewer.toggle_video_playback()
