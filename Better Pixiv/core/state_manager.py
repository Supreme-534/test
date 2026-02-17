class AppState:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.mode = 'random'  # 'random', 'artist'
        self.current_post_id = None
        self.current_artist_id = None
        self.current_page_idx = 0
        self.current_work = []
        self.history = []
        
        # Artist mode navigation
        self.artist_works = []
        self.artist_work_index = 0
        
        # UI state
        self.artist_menu_active = False
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
    
    def set_work(self, post_id, work_files):
        """Set current work and reset page index"""
        self.current_post_id = post_id
        self.current_work = work_files
        self.current_page_idx = 0
        
        # Add to history if not already there
        if post_id not in self.history:
            self.history.append(post_id)
    
    def set_artist_mode(self, artist_id, works):
        """Enter artist mode"""
        self.mode = 'artist'
        self.current_artist_id = artist_id
        self.artist_works = works
        self.artist_work_index = 0
        
        # FIX #9: DON'T call set_work here - let main_window handle loading the work
        # The old code: self.set_work(works[0]['post_id'], []) was causing current_work to be empty
    
    def exit_artist_mode(self):
        """Exit artist mode back to random"""
        self.mode = 'random'
        self.current_artist_id = None
        self.artist_works = []
        self.artist_work_index = 0
    
    def next_in_artist_mode(self):
        """Move to next work in artist mode"""
        if self.mode == 'artist' and self.artist_works:
            self.artist_work_index = (self.artist_work_index + 1) % len(self.artist_works)
            return self.artist_works[self.artist_work_index]['post_id']
        return None
    
    def prev_in_artist_mode(self):
        """Move to previous work in artist mode"""
        if self.mode == 'artist' and self.artist_works:
            self.artist_work_index = (self.artist_work_index - 1) % len(self.artist_works)
            return self.artist_works[self.artist_work_index]['post_id']
        return None
    
    def get_current_file(self):
        """Get current file info"""
        if self.current_work and 0 <= self.current_page_idx < len(self.current_work):
            return self.current_work[self.current_page_idx]
        return None
    
    def get_pixiv_url(self):
        """Get Pixiv URL for current work"""
        if self.current_post_id:
            return f"https://www.pixiv.net/en/artworks/{self.current_post_id}"
        return ""
