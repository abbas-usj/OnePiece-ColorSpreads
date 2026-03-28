# OnePiece Color Spreads Downloader

Download all color spreads of One Piece from the official wiki.

## Features

- Download all One Piece color spreads
- Update existing folders with new color spreads
- Modern GUI with progress tracking and real-time stats
- CLI version for automation and scripting
- Cancel downloads mid-process
- Real-time statistics (remote/local/new images)

## About

Written in Python 3.14, using:
- **CustomTkinter** for modern GUI
- **Cloudscraper** for bypassing Cloudflare protection
- **BeautifulSoup4** for HTML parsing

All color spreads come from: 
`https://onepiece.fandom.com/wiki/Category:Color_Spreads`

## Installation

### Option 1: Standalone Executable (No Python Required)

Download the latest `OP-ColorSpreads-Downloader.exe` from the releases section and run it directly.

### Option 2: Run from Source

1. Clone this repository:
```bash
git clone https://github.com/abbas-usj/OnePiece-ColorSpreads.git
cd OnePiece-ColorSpreads
```
2.Install dependencies:
```bash
pip install -r requirements.txt
```
3.Run the application:
```bash
# GUI Version
python onepiece_gui.py

# CLI Version
python onepiece_cli.py
```

## Usage

### GUI Version
1.Click Browse to select your download folder
2.Click Check for New Images to see what's available
3.Click Download New Images to start downloading
4.Use Stop Download to cancel mid-download
![Alt text](src/OP-ColorSpreads-GUI_Usage.gif)

### CLI Version
```bash
# Download all images to current directory
python onepiece_cli.py

# Download/update to specific directory
python onepiece_cli.py -p "C:/Users/[YourName]/Downloads/OnePiece"
```
