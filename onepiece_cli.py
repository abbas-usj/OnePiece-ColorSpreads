#!/usr/bin/env python3
'''
Downloading/Updating Color spreads of One Piece from the fandom site.

Usage:
python onepiece_cli.py 
    --> will download all the images in the current directory

python onepiece_cli.py -p "PATH/TO/DIRECTORY"
    --> will download/update in the provided directory the latest color spreads
'''

import os
import argparse
from onepiece_downloader import OnePieceDownloader

# ANSI escape codes for terminal formatting
LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Download One Piece Color Spreads')
    parser.add_argument("-p", "--path", type=str, required=False,
                       help="Path to download/update images (default: current directory)")
    args = parser.parse_args()
    
    # Create downloader instance
    downloader = OnePieceDownloader()
    
    # Determine path
    if args.path:
        img_path = args.path.rstrip('/')  # Remove trailing slash if present
        update_mode = True
        local_images = downloader.get_local_images(img_path)
        print(f"Updating {img_path} --> Number of local images: {len(local_images)}")
    else:
        img_path = os.getcwd()
        update_mode = False
        print(f"Downloading all images in current folder: {img_path}")
    
    try:
        # Check remote images
        print("Fetching remote images...")
        remote_images = downloader.get_remote_images()
        remote_names = [img['name'] for img in remote_images]
        print(f"Total number of remote images: {len(remote_images)}")
        
        if update_mode:
            # Update mode - download only missing images
            if sorted(remote_names) == sorted(local_images):
                print(f"{img_path} is up-to-date. No new images to download")
                return
            
            # Download missing images
            counter = 0
            for img in remote_images:
                if img['name'] not in local_images:
                    print(f"Downloading: {img['name']} in {img_path}")
                    print(LINE_UP, end=LINE_CLEAR)  # Clear the previous line
                    
                    if downloader.download_image(img_path, img['name'], img['url']):
                        counter += 1
                    else:
                        print(f"Failed to download: {img['name']}")
            
            print(f"Downloaded {counter} images in {img_path}")
        
        else:
            # Full download mode - download all images
            counter = 0
            for img in remote_images:
                print(f"Downloading: {img['name']}")
                print(LINE_UP, end=LINE_CLEAR)  # Clear the previous line
                
                if downloader.download_image(img_path, img['name'], img['url']):
                    counter += 1
                else:
                    print(f"Failed to download: {img['name']}")
            
            print(f"Downloaded {counter} images in {img_path}")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())