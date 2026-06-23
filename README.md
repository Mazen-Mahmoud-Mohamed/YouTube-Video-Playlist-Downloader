# 🚀 Ultimate Playlist + Template YouTube Downloader

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue" />
  <img src="https://img.shields.io/badge/Platform-Windows-success" />
  <img src="https://img.shields.io/badge/FFmpeg-Required-orange" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
</p>

A powerful YouTube downloader built with **pytubefix** that supports **single videos**, **entire playlists**, **custom naming templates**, **thumbnail embedding**, **audio conversion**, **resume support**, and **automatic playlist organization**.

---

# ✨ Features

## 🎬 Video Downloads
- Download single YouTube videos
- Download entire playlists
- Automatic video + audio merging
- MP4 output
- Quality selection
- Embedded metadata

## 🎧 Audio Downloads
- Audio-only mode
- MP3 conversion
- 192 kbps output
- Playlist audio downloads

## 📜 Playlist Features
- Automatic playlist detection
- Creates a dedicated folder for each playlist
- Downloads missing videos only
- Skips already downloaded files
- Sorts existing files according to playlist order
- Resume-friendly

## 🖼 Thumbnail Support
- Downloads video thumbnails
- Embeds cover art into videos
- Repairs missing thumbnails in old downloads

## 📊 Advanced Download Information
- Progress bar
- Download percentage
- Download speed
- Estimated remaining time (ETA)
- Colored terminal output

---

# 📁 Output Structure

```text
D:\YouTube download
│
├── Playlist A
│   ├── 01 - Video.mp4
│   ├── 02 - Video.mp4
│   └── ...
│
└── Playlist B
```

---

# 🏷 Filename Templates

Supported placeholders:

| Placeholder | Description |
|------------|-------------|
| `{index}` | Playlist position |
| `{channel}` | Channel name |
| `{title}` | Video title |
| `{resolution}` | Video resolution |
| `{playlist}` | Playlist name |

### Examples

```text
{channel} - {title} ({resolution}).mp4
```

```text
{index} - {title}.mp4
```

```text
{playlist} - {index} - {title} ({resolution}).mp4
```

---

# 📦 Installation

## 1. Clone Repository

```bash
git clone https://github.com/your-username/youtube-downloader.git
cd youtube-downloader
```

## 2. Install Dependencies

```bash
pip install pytubefix
pip install requests
pip install colorama
```

Or:

```bash
pip install pytubefix requests colorama
```

---

# ⚙ Requirements

## Python

- Python 3.9+

## FFmpeg

FFmpeg must be installed and added to PATH.

Verify installation:

```bash
ffmpeg -version
```

```bash
ffprobe -version
```

---

# 🚀 Usage

Run:

```bash
python downloader.py
```

The program will ask for:

1. YouTube URL
2. Filename template
3. Audio-only or Video mode
4. Video quality (for playlists)

Example:

```text
Enter YouTube video or playlist URL:
https://youtube.com/playlist?list=XXXXX
```

---

# 🔧 Core Functions

## on_progress()

Displays:

- Download progress
- Download speed
- ETA
- Progress bar

---

## download_thumbnail()

Downloads the video's thumbnail and stores it temporarily.

---

## merge_with_thumbnail()

Uses FFmpeg to:

- Merge streams
- Convert audio to AAC
- Embed metadata
- Embed thumbnail

---

## ensure_thumbnail_embedded()

Checks downloaded videos and injects thumbnails when missing.

---

## download_video_item()

Main download engine responsible for:

- Stream selection
- Downloading
- Merging
- Metadata
- Thumbnail processing

---

# 🎯 Resume Support

If a file already exists:

```text
⏩ Skipped (already exists)
```

The downloader:

- Does not re-download it
- Verifies thumbnail metadata
- Continues with remaining videos

Perfect for interrupted playlist downloads.

---

# 📸 Screenshots

Add screenshots here:

```md
![Main Menu](screenshots/menu.png)

![Downloading](screenshots/download.png)

![Playlist](screenshots/playlist.png)
```

---

# 🛠 Technologies Used

- Python
- pytubefix
- FFmpeg
- FFprobe
- Requests
- Colorama

---

# 🔮 Future Improvements

- GUI Version
- Multi-threaded downloads
- Automatic updates
- Subtitle downloads
- SponsorBlock integration
- Cookie authentication support

---

# ⚠ Disclaimer

This project is intended for educational and personal use only.

Users are responsible for ensuring compliance with:

- YouTube Terms of Service
- Copyright laws
- Local regulations

---

# ⭐ Support

If you found this project useful:

- Star the repository
- Fork the project
- Submit improvements
- Report bugs

---

Made with ❤️ using Python.
