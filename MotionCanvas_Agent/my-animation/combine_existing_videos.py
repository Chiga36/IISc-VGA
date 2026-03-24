#!/usr/bin/env python3
"""
Standalone video combiner - combines existing scene videos without regenerating them.
"""

import os
import glob
import subprocess
import datetime
from pathlib import Path

def check_ffmpeg():
    """Check if FFmpeg is available with fallback to direct path."""
    # Try standard PATH first
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return 'ffmpeg'
    except:
        pass
    
    # Try direct Windows path
    try:
        result = subprocess.run([r'C:\ffmpeg\bin\ffmpeg.exe', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return r'C:\ffmpeg\bin\ffmpeg.exe'
    except:
        pass
    
    return None

def find_scene_videos(output_dir):
    """Find all scene videos and sort them."""
    scene_videos = []
    
    for i in range(1, 20):  # Check scene1.mp4 to scene20.mp4
        video_path = os.path.join(output_dir, f"scene{i}.mp4")
        if os.path.exists(video_path):
            scene_videos.append((i, video_path))
    
    scene_videos.sort(key=lambda x: x[0])  # Sort by scene number
    return scene_videos

def create_video_list_file(video_files, list_file_path):
    """Create FFmpeg concat file."""
    with open(list_file_path, 'w') as f:
        for video_file in video_files:
            # FFmpeg needs forward slashes
            video_path = video_file.replace('\\', '/')
            f.write(f"file '{video_path}'\n")

def combine_videos(ffmpeg_cmd, video_files, output_path):
    """Combine videos using FFmpeg."""
    # Create temporary concat file
    list_file_path = "temp_video_list.txt"
    create_video_list_file(video_files, list_file_path)
    
    try:
        # Simple concatenation command
        cmd = [
            ffmpeg_cmd, '-y',  # -y to overwrite output file
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file_path,
            '-c', 'copy',  # Copy without re-encoding (faster)
            output_path
        ]
        
        print(f"🔄 Running FFmpeg command...")
        print(f"Command: {' '.join(cmd[:6])}... {output_path}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running FFmpeg: {e}")
        return False
    finally:
        # Clean up temp file
        if os.path.exists(list_file_path):
            os.remove(list_file_path)

def main():
    """Main combining function."""
    print("🎬 Standalone Video Combiner")
    print("=" * 50)
    
    # Setup paths
    output_dir = r"c:\Users\Dell\Desktop\IISc_VGA_RVCE-main\MotionCanvas_Agent\my-animation\output"
    
    if not os.path.exists(output_dir):
        print(f"❌ Output directory not found: {output_dir}")
        return
    
    # Check FFmpeg
    ffmpeg_cmd = check_ffmpeg()
    if not ffmpeg_cmd:
        print("❌ FFmpeg not found. Please restart your terminal and try again.")
        print("Or install FFmpeg: https://www.gyan.dev/ffmpeg/builds/")
        return
    
    print(f"✅ FFmpeg found: {ffmpeg_cmd}")
    
    # Find scene videos
    scene_videos = find_scene_videos(output_dir)
    
    if not scene_videos:
        print(f"❌ No scene videos found in: {output_dir}")
        return
    
    print(f"\n🎬 Found {len(scene_videos)} scene videos:")
    for scene_num, path in scene_videos:
        filename = os.path.basename(path)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"   Scene {scene_num}: {filename} ({size_mb:.1f} MB)")
    
    # Get topic name
    topic_name = input(f"\nEnter video title (or press Enter for 'Educational_Video'): ").strip()
    if not topic_name:
        topic_name = "Educational_Video"
    
    # Create safe filename
    safe_topic_name = "".join(c for c in topic_name if c.isalnum() or c in (' ', '-', '_')).strip()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{safe_topic_name}_{timestamp}.mp4"
    output_path = os.path.join(output_dir, output_filename)
    
    # Get video file paths
    video_files = [video_path for _, video_path in scene_videos]
    
    # Combine videos
    print(f"\n🔄 Combining {len(video_files)} videos...")
    success = combine_videos(ffmpeg_cmd, video_files, output_path)
    
    if success:
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n🎉 SUCCESS! Combined video created:")
        print(f"📁 Location: {output_path}")
        print(f"📊 Size: {file_size_mb:.1f} MB")
        print(f"🎬 Contains: {len(scene_videos)} scenes")
        
        # Ask to open folder
        open_folder = input("\nOpen output folder? (y/N): ").strip().lower()
        if open_folder == 'y':
            try:
                os.startfile(output_dir)  # Windows only
            except:
                print(f"Please navigate to: {output_dir}")
    else:
        print("❌ Failed to combine videos")

if __name__ == "__main__":
    main()
