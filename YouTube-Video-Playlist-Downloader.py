# Ultimate Playlist + Template YouTube Downloader (complete)
# - Playlist download (auto folder per playlist)
# - Filename templates: {index}, {channel}, {title}, {resolution}, {playlist}
# - Skip existing files (resume by skipping finished items)
# - Thumbnail download + embed (even for skipped files)
# - AAC audio conversion for compatibility
# - Progress bar, speed, ETA, colored output
# - Thumbnail metadata fix for skipped files
# - Summary + auto-open folder
# - SORT EXISTING VIDEOS before download by playlist order

from pytubefix import YouTube, Playlist
import os
import time
import sys
import subprocess
import re
import requests
import winsound
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# ---------------------------
# Progress callback
# ---------------------------
def on_progress(stream, chunk, bytes_remaining):
    try:
        total_size = stream.filesize
    except Exception:
        total_size = 1
    bytes_downloaded = total_size - bytes_remaining
    percent = (bytes_downloaded / total_size * 100) if total_size > 0 else 0

    current_time = time.time()
    elapsed_time = current_time - on_progress.start_time
    if elapsed_time > 0:
        speed = bytes_downloaded / elapsed_time
        speed_mb = speed / 1024 / 1024
        eta = bytes_remaining / speed if (speed > 0 and bytes_remaining > 0) else 0
    else:
        speed_mb = 0
        eta = 0

    bar_length = 30
    filled_length = int(bar_length * percent // 100)
    bar = Fore.GREEN + '█' * filled_length + Fore.WHITE + '-' * (bar_length - filled_length)

    sys.stdout.write(
        f"\r📥 |{bar}| {Fore.GREEN}{percent:6.2f}% "
        f"{Fore.YELLOW}Speed: {speed_mb:4.2f} MB/s "
        f"{Fore.CYAN}ETA: {eta:5.1f}s"
    )
    sys.stdout.flush()

on_progress.start_time = time.time()

# ---------------------------
# Utilities
# ---------------------------
def clean_filename(s):
    if not s:
        return "unknown"
    return re.sub(r'[\\/*?:"<>|]', "", s).strip()

def download_thumbnail(yt, out_folder, basename):
    """Download a thumbnail image for yt object into out_folder, return path or None."""
    thumb_url = getattr(yt, "thumbnail_url", None)
    if not thumb_url:
        return None
    try:
        r = requests.get(thumb_url, timeout=15)
        if r.status_code == 200:
            thumb_path = os.path.join(out_folder, f"{basename}_thumb.jpg")
            with open(thumb_path, "wb") as f:
                f.write(r.content)
            return thumb_path
    except Exception:
        pass
    return None

def merge_with_thumbnail(video_file, audio_file, final_file, thumb_path, metadata):
    """Merge video+audio, convert audio to AAC, embed metadata and (optionally) thumbnail."""
    cmd = ["ffmpeg", "-y", "-i", video_file, "-i", audio_file]
    if thumb_path:
        cmd += ["-i", thumb_path]
        cmd += [
            "-map", "0:v",
            "-map", "1:a",
            "-map", "2",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-metadata", f"title={metadata.get('title','')}",
            "-metadata", f"artist={metadata.get('artist','')}",
            "-metadata:s:v", "title=Album cover",
            "-metadata:s:v", "comment=Cover (front)",
            final_file
        ]
    else:
        cmd += [
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-metadata", f"title={metadata.get('title','')}",
            "-metadata", f"artist={metadata.get('artist','')}",
            final_file
        ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    try:
        if os.path.exists(video_file):
            os.remove(video_file)
    except:
        pass
    try:
        if os.path.exists(audio_file):
            os.remove(audio_file)
    except:
        pass
    if thumb_path:
        try:
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        except:
            pass

def probe_has_thumbnail(file_path):
    """Return True if mp4 has an embedded cover/thumbnail stream."""
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream_tags=title,comment", "-of", "default=nw=1", file_path],
            capture_output=True, text=True
        )
        out = proc.stdout.lower() if proc and proc.stdout else ""
        if "album cover" in out or "cover" in out or "comment=cover" in out:
            return True
    except:
        pass
    return False

def ensure_thumbnail_embedded(video_path, yt):
    try:
        if not os.path.exists(video_path):
            return
        if probe_has_thumbnail(video_path):
            return
        print(f"\n🖼️ Embedding missing thumbnail into: {video_path}")
        thumb_path = download_thumbnail(yt, os.path.dirname(video_path), clean_filename(getattr(yt, "video_id", yt.title)))
        if not thumb_path:
            print("⚠️ Thumbnail not available.")
            return
        tmp_out = video_path + ".tmp.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", thumb_path,
            "-map", "0",
            "-map", "1",
            "-c", "copy",
            "-metadata:s:v", "title=Album cover",
            "-metadata:s:v", "comment=Cover (front)",
            tmp_out
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.replace(tmp_out, video_path)
        try:
            os.remove(thumb_path)
        except:
            pass
        print("✅ Thumbnail embedded successfully.")
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️ Thumbnail embed failed: {e}{Style.RESET_ALL}")

# ---------------------------
# Download single item
# ---------------------------
def download_video_item(link, out_folder, template, index, audio_only=False, chosen_index=None, skip_if_exists=True):
    try:
        link = link.replace("shorts/", "watch?v=").split("&")[0]
        yt = YouTube(link, on_progress_callback=on_progress)
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to initialize YouTube object: {e}{Style.RESET_ALL}")
        return False

    safe_title = clean_filename(yt.title)
    safe_channel = clean_filename(yt.author or "Unknown")
    playlist_index = index
    audio_stream = yt.streams.filter(adaptive=True, type="audio").order_by('abr').desc().first()
    metadata_map = {
        "index": f"{playlist_index:02d}",
        "channel": safe_channel,
        "title": safe_title,
        "resolution": "audio"
    }

    # audio-only
    if audio_only:
        filename = template.format(**metadata_map)
        if not filename.lower().endswith(".mp3"):
            filename = filename + ".mp3"
        final_audio_path = os.path.join(out_folder, filename)
        if skip_if_exists and os.path.exists(final_audio_path):
            print(f"⏩ Skipped (exists): {final_audio_path}")
            return True

        print(f"\n🎬 {Fore.CYAN}Title:{Style.RESET_ALL} {yt.title}")
        print(f"📺 {Fore.CYAN}Channel:{Style.RESET_ALL} {yt.author}")
        print(f"\n{Fore.GREEN}🎧 Downloading audio ({audio_stream.abr}) ...{Style.RESET_ALL}")
        on_progress.start_time = time.time()
        tmp_audio = os.path.join(out_folder, "audio_temp.mp4")
        audio_stream.download(output_path=out_folder, filename="audio_temp.mp4")
        cmd = ["ffmpeg", "-y", "-i", tmp_audio, "-vn", "-c:a", "libmp3lame", "-b:a", "192k", final_audio_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        try:
            os.remove(tmp_audio)
        except:
            pass
        print(f"{Fore.GREEN}\n✅ Audio download complete!{Style.RESET_ALL}\n📂 {final_audio_path}")
        return True

    # video mode
    video_streams = yt.streams.filter(adaptive=True, type="video", file_extension='mp4').order_by('resolution').desc()
    if not video_streams:
        print(Fore.RED + "❌ No adaptive MP4 video streams available." + Style.RESET_ALL)
        return False
    video_stream = video_streams[chosen_index - 1] if chosen_index and len(video_streams) >= chosen_index else video_streams.first()
    resolution = video_stream.resolution or "Unknown"
    metadata_map["resolution"] = resolution
    filename = template.format(**metadata_map)
    if not filename.lower().endswith(".mp4"):
        filename += ".mp4"
    final_path = os.path.join(out_folder, filename)

    if skip_if_exists and os.path.exists(final_path):
        print(f"⏩ Skipped (already exists): {final_path}")
        ensure_thumbnail_embedded(final_path, yt)
        return True

    print(f"\n🎬 Title: {yt.title}")
    print(f"📺 Channel: {yt.author}")
    print(f"⏱️ Length: {yt.length} seconds")
    print(f"\n{Fore.GREEN}🎞️ Downloading video ({resolution})...{Style.RESET_ALL}")
    on_progress.start_time = time.time()
    video_tmp = os.path.join(out_folder, "video_temp.mp4")
    video_stream.download(output_path=out_folder, filename="video_temp.mp4")

    print(f"\n{Fore.GREEN}🎧 Downloading audio...{Style.RESET_ALL}")
    on_progress.start_time = time.time()
    audio_tmp = os.path.join(out_folder, "audio_temp.mp4")
    audio_stream.download(output_path=out_folder, filename="audio_temp.mp4")

    thumb = download_thumbnail(yt, out_folder, clean_filename(getattr(yt, "video_id", safe_title)))
    metadata = {"title": yt.title, "artist": yt.author}
    merge_with_thumbnail(video_tmp, audio_tmp, final_path, thumb, metadata)
    ensure_thumbnail_embedded(final_path, yt)
    print(f"{Fore.GREEN}\n✅ Download complete!{Style.RESET_ALL}\n📂 {final_path}")
    return True

# ---------------------------
# Main
# ---------------------------
def main():
    try:
        link = input("Enter YouTube video or playlist URL: ").strip()
        base_out = r"D:\YouTube download"
        os.makedirs(base_out, exist_ok=True)

        print("\nFilename template examples (use variables: {index}, {channel}, {title}, {resolution}, {playlist})")
        print("[1] {channel} - {title} ({resolution}).mp4")
        print("[2] {index} - {title}.mp4")
        print("[3] {playlist} - {index} - {title} ({resolution}).mp4")
        custom = input("\nChoose template number or type custom (Enter for #1): ").strip()
        if custom in ("", "1"):
            template = "{channel} - {title} ({resolution}).mp4"
        elif custom == "2":
            template = "{index} - {title}.mp4"
        elif custom == "3":
            template = "{playlist} - {index} - {title} ({resolution}).mp4"
        else:
            template = custom

        is_playlist = "playlist" in link.lower() or "list=" in link.lower()
        summary = {"success": 0, "failed": 0}

        if is_playlist:
            pl = Playlist(link)
            pl_title = clean_filename(pl.title or "Playlist")
            playlist_folder = os.path.join(base_out, pl_title)
            os.makedirs(playlist_folder, exist_ok=True)
            print(f"\n📜 Playlist detected: {pl.title}")
            print(f"📺 Channel: {pl.owner or 'Unknown'}")
            print(f"🎥 Total videos: {len(pl.video_urls)}")

            mode = input("\n🎧 Download audio only? (y/n): ").strip().lower()
            audio_only = (mode == 'y')

            chosen_index = None
            if not audio_only:
                temp_yt = YouTube(pl.video_urls[0])
                vstreams = temp_yt.streams.filter(adaptive=True, type="video", file_extension='mp4').order_by('resolution').desc()
                print(f"\nSelect quality for all videos:")
                for i, s in enumerate(vstreams, 1):
                    fps = f"{s.fps} fps" if s.fps else ""
                    print(f"[{i}] {s.resolution} ({fps})")
                choice = input("\nSelect resolution number (Enter for highest): ").strip()
                chosen_index = int(choice) if choice.isdigit() else 1

            # --- SORT EXISTING FILES BEFORE DOWNLOAD ---
            existing_files = [f for f in os.listdir(playlist_folder) if f.lower().endswith(".mp4")]
            if existing_files:
                print(f"\n📂 Found {len(existing_files)} existing files. Sorting and renaming by playlist order...")
                title_map = {}
                for idx, url in enumerate(pl.video_urls, start=1):
                    try:
                        yt = YouTube(url)
                        clean_title = clean_filename(yt.title).lower()
                        title_map[clean_title] = idx
                    except Exception:
                        continue
                for f in existing_files:
                    original_path = os.path.join(playlist_folder, f)
                    lower_f = f.lower()
                    for title_key, idx in title_map.items():
                        if title_key in lower_f:
                            ext = os.path.splitext(f)[1]
                            new_name = f"{idx:02d} - {f}"
                            new_path = os.path.join(playlist_folder, new_name)
                            if not os.path.exists(new_path):
                                os.rename(original_path, new_path)
                            break
                print("✅ Sorting complete! Continuing with missing downloads...")

            # --- Download missing videos ---
            for idx, video_url in enumerate(pl.video_urls, start=1):
                print(f"\n\n▶️ Downloading video {idx}/{len(pl.video_urls)}...")
                try:
                    per_template = template.replace("{playlist}", pl_title)
                    ok = download_video_item(video_url, playlist_folder, per_template, idx, audio_only, chosen_index, True)
                    summary["success" if ok else "failed"] += 1
                except Exception as e:
                    print(f"{Fore.RED}❌ Skipped:{Style.RESET_ALL} {e}")
                    summary["failed"] += 1

            try:
                os.startfile(playlist_folder)
            except:
                pass

        else:
            mode = input("\n🎧 Download audio only? (y/n): ").strip().lower()
            audio_only = (mode == 'y')
            single_template = template.replace("{playlist}", "")
            ok = download_video_item(link, base_out, single_template, 1, audio_only, None, True)
            summary["success" if ok else "failed"] += 1
            try:
                os.startfile(base_out)
            except:
                pass

        print("\n\n" + Fore.CYAN + "Download summary:" + Style.RESET_ALL)
        print(Fore.GREEN + f"  Success: {summary['success']}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"  Failed: {summary['failed']}" + Style.RESET_ALL)

        winsound.Beep(900, 200)
        winsound.Beep(1200, 200)
        winsound.Beep(1500, 200)

    except Exception as e:
        print(f"\n{Fore.RED}❌ Error:{Style.RESET_ALL} {e}")

if __name__ == "__main__":
    main()
