"""
User Interface components
"""
from .styles import ModernStyle
from .media_viewer import MediaViewer
from .sidebar import Sidebar
from .artist_menu import ArtistMenu
from .controls import ControlPanel
from .main_window import MainWindow

__all__ = [
    'ModernStyle', 
    'MediaViewer', 
    'Sidebar', 
    'ArtistMenu', 
    'ControlPanel',
    'MainWindow'
]