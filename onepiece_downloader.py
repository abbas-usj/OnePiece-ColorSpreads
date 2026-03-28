#!/usr/bin/env python3
"""
Core library for downloading One Piece Color Spreads
"""

import os
import cloudscraper
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
from urllib.parse import urljoin

class OnePieceDownloader:
    """Core downloader class for One Piece Color Spreads"""
    
    BASE_URL = "https://onepiece.fandom.com/wiki/Category:Color_Spreads"
    
    def __init__(self):
        # Create a cloudscraper session to bypass Cloudflare
        self.scraper = cloudscraper.create_scraper()
    
    def get_local_images(self, path: str) -> List[str]:
        """Get list of images in local directory"""
        local_images = []
        if os.path.exists(path):
            for item in os.listdir(path):
                if os.path.isfile(os.path.join(path, item)):
                    if item.lower().endswith(('.png', '.jpg', '.jpeg')):
                        local_images.append(item)
        return local_images
    
    def get_remote_images(self, progress_callback=None) -> List[Dict[str, str]]:
        """
        Fetch all remote images from the wiki by following pagination
        Returns list of dicts with 'name' and 'url' keys
        """
        all_images = []
        current_url = self.BASE_URL
        page_num = 1
        
        while current_url:
            if progress_callback:
                progress_callback(f"Fetching page {page_num}...", page_num)
            
            # Fetch the page
            r = self.scraper.get(current_url, timeout=15)
            if r.status_code != 200:
                raise Exception(f"HTTP {r.status_code} - Failed to access {current_url}")
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Extract images from current page
            page_images = self.extract_images_from_page(soup)
            all_images.extend(page_images)
            
            if progress_callback:
                progress_callback(f"Found {len(page_images)} images on page {page_num}", page_num)
            
            # Look for next page link
            next_url = self.find_next_page_url(soup, current_url)
            current_url = next_url
            page_num += 1
            
            # Small delay to be respectful
            if current_url:
                time.sleep(1)
        
        # Remove duplicates (in case any image appears on multiple pages)
        return self.deduplicate_images(all_images)
    
    def extract_images_from_page(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all image URLs from a single page"""
        images = []
        
        # Method 1: Look for category page members (most common)
        category_ul = soup.find('ul', {"class": "category-page__members-for-char"})
        if category_ul:
            lis = category_ul.find_all('li')
            for li in lis:
                img = self.extract_image_from_element(li)
                if img:
                    images.append(img)
            if images:
                return images
        
        # Method 2: Look for gallery boxes
        gallery_items = soup.find_all('div', class_='gallerybox')
        for item in gallery_items:
            img = self.extract_image_from_element(item)
            if img:
                images.append(img)
        
        if images:
            return images
        
        # Method 3: Look for wikia gallery items
        gallery_items = soup.find_all('div', class_='wikia-gallery-item')
        for item in gallery_items:
            img = self.extract_image_from_element(item)
            if img:
                images.append(img)
        
        if images:
            return images
        
        # Method 4: Look for all image links
        image_links = soup.find_all('a', class_='image')
        for link in image_links:
            img = link.find('img')
            if img:
                img_src = img.get('src', '') or img.get('data-src', '')
                if img_src:
                    img_url = img_src.split("/revision/")[0]
                    img_name = img_url.split("/")[-1]
                    if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        images.append({"name": img_name, "url": img_url})
        
        return images
    
    def extract_image_from_element(self, element) -> Optional[Dict[str, str]]:
        """Extract image from a BeautifulSoup element"""
        # Try to find img tag directly
        img = element.find('img')
        if img:
            img_src = img.get('src', '') or img.get('data-src', '')
            if img_src:
                img_url = img_src.split("/revision/")[0]
                img_name = img_url.split("/")[-1]
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return {"name": img_name, "url": img_url}
        
        # Try to find image in links
        link = element.find('a', class_='image')
        if link:
            img = link.find('img')
            if img:
                img_src = img.get('src', '') or img.get('data-src', '')
                if img_src:
                    img_url = img_src.split("/revision/")[0]
                    img_name = img_url.split("/")[-1]
                    if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        return {"name": img_name, "url": img_url}
        
        return None
    
    def find_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """Find the URL for the next page in the pagination"""
        # Look for "Next" link in pagination
        pagination = soup.find('div', class_='category-page__pagination')
        if pagination:
            next_link = pagination.find('a', class_='category-page__pagination-next')
            if next_link and next_link.get('href'):
                return urljoin(current_url, next_link['href'])
        
        # Alternative: Look for "Next" link anywhere
        next_link = soup.find('a', text='Next')
        if next_link and next_link.get('href'):
            return urljoin(current_url, next_link['href'])
        
        # Alternative: Look for link with "next" in class or text
        next_link = soup.find('a', class_='next')
        if next_link and next_link.get('href'):
            return urljoin(current_url, next_link['href'])
        
        return None
    
    def deduplicate_images(self, images: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove duplicate images based on name"""
        seen = set()
        unique = []
        for img in images:
            if img['name'] not in seen:
                seen.add(img['name'])
                unique.append(img)
        return unique
    
    def download_image(self, path: str, img_name: str, img_url: str) -> bool:
        """
        Download a single image
        Returns True if successful, False otherwise
        """
        try:
            r = self.scraper.get(img_url, timeout=15)
            if r.status_code == 200:
                # Check if it's actually an image
                content_type = r.headers.get('content-type', '')
                if 'image' in content_type:
                    filepath = os.path.join(path, img_name)
                    with open(filepath, 'wb') as f:
                        f.write(r.content)
                    return True
            return False
        except Exception:
            return False
    
    def check_for_updates(self, path: str, progress_callback=None) -> Dict:
        """
        Check for new images available
        Returns dict with remote_count, local_count, new_count, new_images
        """
        local_images = self.get_local_images(path)
        remote_images = self.get_remote_images(progress_callback)
        
        remote_names = [img['name'] for img in remote_images]
        new_images = [img for img in remote_images if img['name'] not in local_images]
        
        return {
            'remote_count': len(remote_images),
            'local_count': len(local_images),
            'new_count': len(new_images),
            'new_images': new_images,
            'remote_images': remote_images
        }