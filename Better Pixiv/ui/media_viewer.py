def play_video_popup(self):
    # adding debug output
    print(f"Attempting to play video from: {self.current_video_path}")
    if self.current_video_path:
        # existing code to play the video
        pass
    else:
        print("No video path set.")
        
    # Original logic follows here...
    
# Add additional code for storing the video path
    def load_video(self, video_path):
        self.current_video_path = video_path
        print(f"Loaded video path: {self.current_video_path}")