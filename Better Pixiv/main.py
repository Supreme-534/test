import tkinter as tk
from ui.main_window import MainWindow

def main():
    # Create main window
    root = tk.Tk()
    
    # Create and run application
    app = MainWindow(root)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()