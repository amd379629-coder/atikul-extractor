#!/usr/bin/env python3
"""
SEX ATIKUL - Premium Website, API & Video Downloader v3.0
Advanced Web Scraping, Asset, API Feed & Video Downloader Tool
"""

import os
import sys
import time
import urllib.parse
import urllib.request

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("\n[!] Please install BeautifulSoup first:  pip install beautifulsoup4\n")

X, B = "\033[0m", "\033[1m"

def c256(n):
    return f"\033[38;5;{n}m"

# 256-colour gradient banner theme
COLORS = [196, 208, 226, 46, 51, 33, 201]

LOGO = [
    "  ███████╗███████╗██╗  ██╗    █████╗ ████████╗██╗██╗  ██╗██╗   ██╗██╗     ",
    "  ██╔════╝██╔════╝╚██╗██╔╝   ██╔══██╗╚══██╔══╝██║██║ ██╔╝██║   ██║██║     ",
    "  ███████╗█████╗   ╚███╔╝    ███████║   ██║   ██║█████╔╝ ██║   ██║██║     ",
    "  ╚════██║██╔══╝   ██╔██╗    ██╔══██║   ██║   ██║██╔═██╗ ██║   ██║██║     ",
    "  ███████║███████╗██╔╝ ██╗   ██║  ██║   ██║   ██║██║  ██╗╚██████╔╝███████╗",
    "  ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝",
]

def banner():
    print()
    print(f"{c256(196)}┌──[ SYSTEM CORE ]─────────────────────────────────────────┐{X}")
    for msg in ("Initializing SEX ATIKUL engine v3.0", "Loading API & Video modules", "Ready for advanced extraction"):
        sys.stdout.write(f"{c256(196)}│ [{B}+{X}{c256(196)}] {msg} ")
        sys.stdout.flush()
        for _ in range(2):
            time.sleep(0.1)
            sys.stdout.write(".")
            sys.stdout.flush()
        print(f" OK{X}")
    print(f"{c256(196)}└──────────────────────────────────────────────────────────┘{X}")
    for line, col in zip(LOGO, COLORS):
        print(f"{c256(col)}{B}{line}{X}")
    print(f"{c256(51)}  ░▒▓█ {B}☠  S E X   A T I K U L  ☠{X}{c256(51)} █▓▒░{X}")
    print(f"{c256(244)}  ╚═► Premium Web, API & Video Downloader Tool  |  Python Edition\n{X}")

def download_website(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    print(f"{c256(226)}[*] Connecting to target: {url}{X}")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"{c256(196)}[!] Connection Failed: {e}{X}")
        return

    # ফোল্ডার তৈরি
    out_dir = "/sdcard/Download/Sex_Atikul_Downloads" if os.path.isdir("/sdcard/Download") else "./Downloaded_Site"
    os.makedirs(out_dir, exist_ok=True)
    
    # মেইন HTML ফাইল সেভ করা
    html_path = os.path.join(out_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"{c256(46)}[+] Main HTML saved successfully!{X}")

    # BeautifulSoup parsing
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # প্রয়োজনীয় ফোল্ডারসমূহ তৈরি (assets, videos, feeds)
    assets_dir = os.path.join(out_dir, "assets")
    videos_dir = os.path.join(out_dir, "videos")
    feeds_dir = os.path.join(out_dir, "feeds", "posts", "default")
    
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    os.makedirs(feeds_dir, exist_ok=True)

    # ১. সাধারণ অ্যাসেটস (ছবি, CSS, JS) ডাউনলোড
    print(f"{c256(51)}[*] Extracting and downloading assets (Images, CSS, JS)...{X}")
    tags = [('link', 'href'), ('script', 'src'), ('img', 'src')]
    asset_count = 0

    for tag_name, attr in tags:
        for tag in soup.find_all(tag_name):
            file_url = tag.get(attr)
            if file_url:
                full_url = urllib.parse.urljoin(url, file_url)
                try:
                    file_name = os.path.basename(urllib.parse.urlparse(full_url).path)
                    if not file_name or '.' not in file_name:
                        continue
                    file_save_path = os.path.join(assets_dir, file_name)
                    
                    img_req = urllib.request.Request(full_url, headers=headers)
                    with urllib.request.urlopen(img_req) as res, open(file_save_path, 'wb') as sf:
                        sf.write(res.read())
                    asset_count += 1
                except Exception:
                    continue

    print(f"{c256(46)}[+] Successfully downloaded {asset_count} assets!{X}")

    # ২. ভিডিও ফাইল ডাউনলোড করার প্রসেস (<video>, <source>, <a> ট্যাগ)
    print(f"{c256(51)}[*] Searching and downloading video files (MP4, WebM, etc.)...{X}")
    video_count = 0
    video_tags = soup.find_all(['video', 'source', 'a'])
    
    for tag in video_tags:
        v_url = tag.get('src') or tag.get('href')
        if v_url and any(v_ext in v_url.lower() for v_ext in ['.mp4', '.webm', '.ogg', '.m3u8', '.mov', '.avi']):
            full_v_url = urllib.parse.urljoin(url, v_url)
            try:
                v_name = os.path.basename(urllib.parse.urlparse(full_v_url).path)
                if not v_name:
                    v_name = f"video_{video_count}.mp4"
                v_save_path = os.path.join(videos_dir, v_name)

                print(f"{c256(226)}    Downloading video: {v_name}{X}")
                v_req = urllib.request.Request(full_v_url, headers=headers)
                with urllib.request.urlopen(v_req) as v_res, open(v_save_path, 'wb') as vf:
                    vf.write(v_res.read())
                video_count += 1
            except Exception:
                continue

    print(f"{c256(46)}[+] Successfully downloaded {video_count} videos!{X}")

    # ৩. ওয়েবসাইট ফিড ও এপিআই ফাইলগুলো (/feeds/posts/default/...) স্বয়ংক্রিয়ভাবে ডাউনলোড ও ডুপ্লিকেট করা
    print(f"{c256(51)}[*] Downloading API feeds and post structures...{X}")
    feed_count = 0
    # সোর্স কোডে থাকা যেকোনো ফিড বা জেসন লিংক খোঁজা
    for tag in soup.find_all(['script', 'link', 'a']):
        f_url = tag.get('href') or tag.get('src')
        if f_url and 'feeds/posts/default' in f_url:
            full_f_url = urllib.parse.urljoin(url, f_url)
            try:
                # লোকাল ফোল্ডারে সঠিক পাথ অনুযায়ী ফাইল সেভ করার ব্যবস্থা
                parsed_path = urllib.parse.urlparse(full_f_url).path
                filename = os.path.basename(parsed_path)
                if not filename:
                    filename = "default"
                
                feed_save_path = os.path.join(feeds_dir, filename)
                
                f_req = urllib.request.Request(full_f_url, headers=headers)
                with urllib.request.urlopen(f_req) as f_res, open(feed_save_path, 'wb') as ff:
                    ff.write(f_res.read())
                feed_count += 1
            except Exception:
                continue
    
    # এছাড়াও কমন ফিডগুলো যাতে মিস না হয়, সেগুলোর জন্য একটি ডিফল্ট ডামি/মেইন ফিড ফাইল তৈরি করা যাতে 404 এরর না আসে
    try:
        default_feed_path = os.path.join(feeds_dir, "default")
        with open(default_feed_path, "w", encoding="utf-8") as df:
            df.write('<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>Sex Atikul Feed Mirror</title></feed>')
        feed_count += 1
    except Exception:
        pass

    print(f"{c256(46)}[+] Successfully downloaded {feed_count} feed/API components!{X}")
    print(f"{c256(226)}[★] All files, videos & feeds saved to: {out_dir}{X}\n")

def main():
    banner()
    while True:
        try:
            target = input(f"{c256(196)}{B}SEX-ATIKUL{X}{c256(244)}@tool{X}{c256(196)}:~# {X}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{c256(196)}Exiting... Goodbye!{X}")
            break
        
        if target.lower() in ("q", "quit", "exit"):
            print(f"{c256(196)}Exiting... Goodbye!{X}")
            break
        if not target:
            continue
        
        download_website(target)

if __name__ == "__main__":
    main()