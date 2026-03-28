import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import sys
import threading
import time
from onepiece_downloader import OnePieceDownloader

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class OnePieceDownloaderGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("One Piece Color Spreads Downloader")
        self.root.geometry("800x700")
        self.root.minsize(650, 600)
        
        # Set icon if exists - FIXED
        try:
            icon_path = resource_path("./src/Shanks.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        self.downloader = OnePieceDownloader()
        self.remote_images = []
        self.is_checking = False
        self.is_downloading = False
        self.stop_download = threading.Event()
        
        # Initialize value references
        self.remote_value = None
        self.local_value = None
        self.new_value = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container
        main = ctk.CTkFrame(self.root, fg_color="transparent")
        main.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main.grid_columnconfigure(0, weight=1)
        
        # Header
        self.create_header(main)
        
        # Stats cards
        self.create_stats_cards(main)
        
        # Folder selection
        self.create_folder_section(main)
        
        # Action buttons
        self.create_action_buttons(main)
        
        # Status section
        self.create_status_section(main)
        
        # Recent downloads section
        self.create_recent_section(main)
    
    def create_header(self, parent):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Try to load logo - FIXED
        try:
            icon_path = resource_path("./src/Shanks.ico")
            if os.path.exists(icon_path):
                logo_image = Image.open(icon_path)
                logo_image = logo_image.resize((50, 50), Image.Resampling.LANCZOS)
                logo_ctk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(50, 50))
                logo_label = ctk.CTkLabel(header_frame, image=logo_ctk, text="")
                logo_label.pack(side="left", padx=(0, 15))
        except:
            pass
        
        # Title
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True)
        
        title_text = "One Piece Color Spreads Downloader"
        title = ctk.CTkLabel(
            title_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FF6B6B"
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Download all color spreads from the One Piece Wiki",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        subtitle.pack(anchor="w")
    
    def create_stats_cards(self, parent):
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Card 1: Remote 
        self.create_stat_card(stats_frame, "📡", "Remote", "0", "Available online", 0)

        # Card 2: Local
        self.create_stat_card(stats_frame, "💾", "Local", "0", "Already downloaded", 1)
        
        # Card 3: New
        self.create_stat_card(stats_frame, "✨", "New", "0", "Ready to download", 2)
    
    def create_stat_card(self, parent, emoji, title, value, subtitle, column):
        """Create a stat card with larger emoji"""
        card = ctk.CTkFrame(parent, corner_radius=12, border_width=1, border_color="gray30")
        
        # Create a frame for the emoji and title (horizontal layout)
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(pady=(12, 5))
        
        # Emoji with larger font
        emoji_label = ctk.CTkLabel(
            header_frame, 
            text=emoji, 
            font=ctk.CTkFont(size=28),  # Larger font for emoji
            text_color="gray70"
        )
        emoji_label.pack(side="left", padx=(0, 8))
        
        # Title text
        title_label = ctk.CTkLabel(
            header_frame, 
            text=title, 
            font=ctk.CTkFont(size=16, weight="bold"),  # Larger title font
            text_color="gray70"
        )
        title_label.pack(side="left")
        
        # Value (large number)
        value_label = ctk.CTkLabel(
            card, 
            text=value, 
            font=ctk.CTkFont(size=32, weight="bold"),  # Even larger for numbers
            text_color="#FF6B6B" if column == 2 else "white"
        )
        value_label.pack(pady=(5, 0))
        
        # Subtitle text
        subtitle_label = ctk.CTkLabel(
            card, 
            text=subtitle, 
            font=ctk.CTkFont(size=11), 
            text_color="gray50"
        )
        subtitle_label.pack(pady=(5, 12))
        
        # Store references for updating values
        if column == 0:
            self.remote_value = value_label
        elif column == 1:
            self.local_value = value_label
        else:
            self.new_value = value_label
        
        # Position the card in the grid
        card.grid(row=0, column=column, padx=(0, 10) if column < 2 else 0, sticky="ew")
    
    def create_folder_section(self, parent):
        folder_frame = ctk.CTkFrame(parent, corner_radius=12)
        folder_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        folder_frame.grid_columnconfigure(0, weight=1)
        
        # Header with larger emoji
        header = ctk.CTkLabel(
            folder_frame, 
            text="📁  Download Location",  # Space after emoji
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=15, pady=(12, 8))
        
        # Folder selection
        folder_controls = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_controls.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 12))
        folder_controls.grid_columnconfigure(0, weight=1)
        
        self.folder_path = ctk.StringVar()
        folder_entry = ctk.CTkEntry(
            folder_controls, 
            textvariable=self.folder_path,
            placeholder_text="Select a folder to save images...", 
            height=40,
            font=ctk.CTkFont(size=13)
        )
        folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            folder_controls, 
            text="📂  Browse",  # Add emoji to browse button
            command=self.browse_folder,
            height=40, 
            width=200, 
            fg_color="#2C3E50",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        browse_btn.grid(row=0, column=1)
    
    def create_action_buttons(self, parent):
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        
        # Configure columns with equal weight
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        # Create buttons without width initially
        self.check_btn = ctk.CTkButton(
            button_frame, 
            text="🔍  Check for New Images",
            command=self.check_images, 
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3498DB",
            hover_color="#2980B9"
        )
        self.check_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.download_btn = ctk.CTkButton(
            button_frame, 
            text="🡻  Download New Images",
            command=self.start_download, 
            state="disabled",
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#019F3B",
            hover_color="#257C49"
        )
        self.download_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.stop_btn = ctk.CTkButton(
            button_frame, 
            text="⛔  Stop Download",
            command=self.stop_downloading, 
            state="disabled",
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#E74C3C", 
            hover_color="#C0392B"
        )
        self.stop_btn.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        
        # Store button frame reference for resize handling
        self.button_frame = button_frame
        
        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Initial resize
        self.root.after(100, self.update_button_widths)

    def update_button_widths(self):
        """Update button widths based on current window size"""
        if hasattr(self, 'button_frame'):
            # Get available width for buttons (frame width minus padding)
            frame_width = self.button_frame.winfo_width()
            if frame_width > 100:  # Only update if frame has reasonable width
                button_width = int((frame_width - 20) / 3)  # Divide by 3 minus padding
                button_width = max(150, min(300, button_width))  # Clamp between 150-300
                
                self.check_btn.configure(width=button_width)
                self.download_btn.configure(width=button_width)
                self.stop_btn.configure(width=button_width)

    def on_window_resize(self, event):
        """Handle window resize events"""
        # Only update when main window is resized
        if event.widget == self.root:
            self.root.after(100, self.update_button_widths)
    
    def create_status_section(self, parent):
        status_frame = ctk.CTkFrame(parent, corner_radius=12)
        status_frame.grid(row=4, column=0, sticky="ew", pady=(0, 15))
        
        # Status header with emoji
        status_header = ctk.CTkLabel(
            status_frame, 
            text="📊  Status", 
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        status_header.pack(padx=15, pady=(12, 5), fill="x")
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="Status: Ready",
            font=ctk.CTkFont(size=12), 
            anchor="w"
        )
        self.status_label.pack(padx=15, pady=(0, 8), fill="x")
        
        # Progress bar with percentage
        progress_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        progress_frame.pack(padx=15, pady=(0, 5), fill="x")
        
        self.progress = ctk.CTkProgressBar(
            progress_frame, 
            height=18, 
            corner_radius=8,
            progress_color="#FF6B6B"
        )
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.progress_percent = ctk.CTkLabel(
            progress_frame, 
            text="0%", 
            width=45,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.progress_percent.pack(side="right")
        
        self.progress.set(0)
        
        # Current file label with emoji
        self.current_file = ctk.CTkLabel(
            status_frame, 
            text="", 
            font=ctk.CTkFont(size=11),
            text_color="gray70", 
            anchor="w"
        )
        self.current_file.pack(padx=15, pady=(0, 12), fill="x")
    
    def create_recent_section(self, parent):
        self.recent_frame = ctk.CTkFrame(parent, corner_radius=12)
        self.recent_frame.grid(row=5, column=0, sticky="ew")
        
        # Toggle button for recent downloads with emoji
        self.recent_toggle = ctk.CTkButton(
            self.recent_frame,
            text="▼  Recent Downloads",  # Space after emoji
            command=self.toggle_recent,
            fg_color="transparent",
            text_color="gray70",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35,
            anchor="w"
        )
        self.recent_toggle.pack(padx=15, pady=(8, 5), fill="x")
        
        # Container for recent items
        self.recent_content = ctk.CTkFrame(self.recent_frame, fg_color="transparent")
        self.recent_list = []
    
    def toggle_recent(self):
        if self.recent_content.winfo_ismapped():
            self.recent_content.pack_forget()
            self.recent_toggle.configure(text="▶  Recent Downloads")
        else:
            self.recent_content.pack(padx=15, pady=(0, 10), fill="both")
            self.recent_toggle.configure(text="▼  Recent Downloads")
    
    def add_recent_download(self, filename):
        """Add a filename to the recent downloads list"""
        # Truncate long filenames
        display_name = filename if len(filename) < 50 else filename[:47] + "..."
        
        label = ctk.CTkLabel(
            self.recent_content,
            text=f"✓  {display_name}",  # Add space after checkmark
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        label.pack(fill="x", pady=2)
        self.recent_list.append(label)
        
        # Keep only last 10 downloads
        if len(self.recent_list) > 10:
            self.recent_list[0].destroy()
            self.recent_list.pop(0)
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.folder_path.set(folder)
            # Update local count
            local_images = self.downloader.get_local_images(folder)
            if self.local_value:
                self.local_value.configure(text=str(len(local_images)))
            self.status_label.configure(text="✅  Folder selected. Click 'Check' to see available images.")
    
    def update_stats(self, remote_count=None, local_count=None, new_count=None):
        if remote_count is not None and self.remote_value:
            self.remote_value.configure(text=str(remote_count))
        if local_count is not None and self.local_value:
            self.local_value.configure(text=str(local_count))
        if new_count is not None and self.new_value:
            self.new_value.configure(text=str(new_count))
    
    def check_images(self):
        if not self.folder_path.get():
            messagebox.showwarning("No Folder", "Please select a download folder first!")
            return
        
        if self.is_checking:
            return
        
        def progress_callback(message, page_num):
            self.status_label.configure(text=f"🔍  {message}")
            self.root.update_idletasks()
        
        def check_thread():
            self.is_checking = True
            
            # Change text without changing width (use same length text)
            self.check_btn.configure(
                state="disabled", 
                text="⌛  Checking...",
                fg_color="#2C3E50"
            )
            self.status_label.configure(text="🔍  Fetching remote images from all pages...")
            
            try:
                path = self.folder_path.get()
                local_images = self.downloader.get_local_images(path)
                if self.local_value:
                    self.local_value.configure(text=str(len(local_images)))
                
                remote_images = self.downloader.get_remote_images(progress_callback)
                self.remote_images = remote_images
                if self.remote_value:
                    self.remote_value.configure(text=str(len(remote_images)))
                
                remote_names = [img['name'] for img in remote_images]
                new_count = sum(1 for name in remote_names if name not in local_images)
                if self.new_value:
                    self.new_value.configure(text=str(new_count))
                
                if new_count > 0:
                    self.download_btn.configure(state="normal")
                    self.status_label.configure(text=f"✅  Found {new_count} new images available across {len(remote_images)} total!")
                else:
                    self.download_btn.configure(state="disabled")
                    self.status_label.configure(text="✅  All images are up-to-date!")
                    
            except Exception as e:
                self.status_label.configure(text=f"❌  Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to check images:\n{str(e)}")
            finally:
                self.check_btn.configure(
                    state="normal", 
                    text="🔍  Check for New Images",
                    fg_color="#3498DB"
                )
                self.is_checking = False
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def start_download(self):
        """Start the download process"""
        if not self.folder_path.get():
            return
        
        if self.is_downloading:
            return
        
        # Reset stop event
        self.stop_download.clear()
        
        path = self.folder_path.get()
        local_images = self.downloader.get_local_images(path)
        remote_names = [img['name'] for img in self.remote_images]
        new_images = [img for img in self.remote_images if img['name'] not in local_images]
        
        if not new_images:
            messagebox.showinfo("No Images", "No new images to download!")
            return
        
        # Ask for confirmation
        result = messagebox.askyesno(
            "Confirm Download",
            f"📥  You're about to download {len(new_images)} new images.\n\n"
            f"📡  Total images available: {len(self.remote_images)}\n"
            f"💾  Already downloaded: {len(local_images)}\n\n"
            "Do you want to continue?"
        )
        if not result:
            return
        
        # Start download in thread
        download_thread = threading.Thread(
            target=self.download_images,
            args=(new_images, remote_names),
            daemon=True
        )
        download_thread.start()
    
    def stop_downloading(self):
        """Stop the ongoing download"""
        if self.is_downloading:
            self.stop_download.set()
            self.status_label.configure(text="⛔  Stopping download... Please wait...")
            self.stop_btn.configure(state="disabled", text="⛔  Stopping...")
    
    def download_images(self, new_images, remote_names):
        """Download images with stop capability"""
        self.is_downloading = True
        self.download_btn.configure(state="disabled")
        self.check_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal", text="⛔  Stop Download")
        self.progress.set(0)
        self.progress_percent.configure(text="0%")
        
        total = len(new_images)
        successful = 0
        stopped_early = False
        
        for i, img in enumerate(new_images, 1):
            # Check if stop was requested
            if self.stop_download.is_set():
                stopped_early = True
                self.status_label.configure(
                    text=f"⛔  Stopped after downloading {successful}/{total} images"
                )
                break
            
            # Update current file
            self.current_file.configure(text=f"📥  Downloading: {img['name']}")
            
            # Download image
            if self.downloader.download_image(self.folder_path.get(), img['name'], img['url']):
                successful += 1
                self.add_recent_download(img['name'])
            
            # Update progress
            progress_value = i / total
            self.progress.set(progress_value)
            self.progress_percent.configure(text=f"{int(progress_value * 100)}%")
            self.status_label.configure(text=f"📥  Downloading {i}/{total}")
            self.root.update_idletasks()
            
            # Small delay to be respectful
            time.sleep(0.1)
        
        # Clear current file display
        self.current_file.configure(text="")
        
        # Update final stats
        final_local = self.downloader.get_local_images(self.folder_path.get())
        if self.local_value:
            self.local_value.configure(text=str(len(final_local)))
        final_new = sum(1 for name in remote_names if name not in final_local)
        if self.new_value:
            self.new_value.configure(text=str(final_new))
        
        # Update status message based on how download ended
        if stopped_early:
            self.status_label.configure(
                text=f"⛔  Download stopped. Downloaded {successful}/{total} images."
            )
            messagebox.showwarning(
                "Download Stopped",
                f"⛔  Download was stopped by user.\n\n"
                f"✅  Downloaded {successful} out of {total} images.\n\n"
                f"🔍  Click 'Check' to see remaining images."
            )
        elif successful == total:
            self.status_label.configure(text=f"✅  Complete! Downloaded all {successful} images!")
            messagebox.showinfo("Complete", f"✅  Successfully downloaded all {successful} images!")
        elif successful > 0:
            self.status_label.configure(text=f"⚠️  Partial - Downloaded {successful}/{total} images")
            messagebox.showwarning(
                "Partial Download",
                f"⚠️  Downloaded {successful} out of {total} images.\n\n"
                f"Some images may have failed to download."
            )
        else:
            self.status_label.configure(text="❌  No images were downloaded")
        
        # Reset buttons
        self.download_btn.configure(state="disabled" if final_new == 0 else "normal")
        self.check_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled", text="⛔  Stop Download")
        self.progress.set(0)
        self.progress_percent.configure(text="0%")
        self.is_downloading = False
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_downloading:
            result = messagebox.askyesno(
                "Download in Progress",
                "⚠️  A download is currently in progress.\n\n"
                "Are you sure you want to exit?\n"
                "The download will be stopped."
            )
            if result:
                self.stop_download.set()
                time.sleep(0.5)
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    app = OnePieceDownloaderGUI()
    app.run()