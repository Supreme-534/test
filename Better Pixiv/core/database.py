import json
import os
from config import POINTS_FILE, NICE_FILE

class Database:
    def __init__(self):
        self.points_db = self._load(POINTS_FILE)
        self.nice_db = self._load(NICE_FILE)
        
        # Migrate from image-based to post-based
        self.migrate_to_post_based()
    
    def _load(self, filename):
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def migrate_to_post_based(self):
        """Migrate from image-based to post-based storage"""
        print("Checking for database migration...")
        
        # Check if we have old image-based data
        old_points = {}
        old_nice = {}
        
        for filename, value in self.points_db.items():
            if '_p' in filename:
                post_id = filename.split('_p')[0]
                if post_id not in old_points:
                    old_points[post_id] = 0
                old_points[post_id] += value
        
        for filename, value in self.nice_db.items():
            if '_p' in filename:
                post_id = filename.split('_p')[0]
                if post_id not in old_nice:
                    old_nice[post_id] = 0
                # Take maximum nice value for post
                if value > old_nice.get(post_id, 0):
                    old_nice[post_id] = value
        
        # If we found old data, migrate it
        if old_points or old_nice:
            print(f"Migrating {len(old_points)} posts from image-based to post-based storage")
            
            # Update points: sum all image points for each post
            for post_id, total_points in old_points.items():
                self.points_db[post_id] = total_points
            
            # Update nice: take maximum nice for each post
            for post_id, max_nice in old_nice.items():
                self.nice_db[post_id] = max_nice
            
            # Save the migrated databases
            self._save(self.points_db, POINTS_FILE)
            self._save(self.nice_db, NICE_FILE)
            print("Migration complete!")
    
    def get_points(self, post_id):
        """Get points for a post"""
        return self.points_db.get(post_id, 0)
    
    def get_nice(self, post_id):
        """Get nice for a post"""
        return self.nice_db.get(post_id, 0)
    
    def add_point(self, post_id):
        """Add point to a post"""
        self.points_db[post_id] = self.points_db.get(post_id, 0) + 1
        self._save(self.points_db, POINTS_FILE)
        return self.points_db[post_id]
    
    def add_nice(self, post_id):
        """Add nice to a post"""
        self.nice_db[post_id] = self.nice_db.get(post_id, 0) + 1
        self._save(self.nice_db, NICE_FILE)
        return self.nice_db[post_id]
    
    def remove_file(self, filename):
        """Remove file from both databases (for compatibility)"""
        # In post-based system, we don't track individual files
        # But we still need this for backward compatibility
        pass
    
    def remove_post(self, post_id):
        """Remove post from databases"""
        if post_id in self.points_db:
            del self.points_db[post_id]
            self._save(self.points_db, POINTS_FILE)
        
        if post_id in self.nice_db:
            del self.nice_db[post_id]
            self._save(self.nice_db, NICE_FILE)