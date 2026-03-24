#!/usr/bin/env python3
"""
Video combiner for Motion Canvas generated scenes.
Combines multiple scene videos into a single educational video.
"""

import os
import glob
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
import datetime

class VideoCombiner:
    """Combines multiple Motion Canvas scene videos into a final educational video."""
    
    def __init__(self, project_root: str = None):
        """Initialize the video combiner."""
        if project_root is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.project_root = os.path.dirname(current_dir)
        else:
            self.project_root = project_root
            
        self.output_dir = os.path.join(self.project_root, "output")
        self.combined_dir = os.path.join(self.project_root, "combined_videos")
        
        # Create combined videos directory
        os.makedirs(self.combined_dir, exist_ok=True)
        
        print(f"📁 Project root: {self.project_root}")
        print(f"📁 Scene videos: {self.output_dir}")
        print(f"📁 Combined videos: {self.combined_dir}")
    
    def find_scene_videos(self) -> List[tuple]:
        """
        Find all scene videos in the output directory.
        Returns list of (scene_number, filename, full_path) tuples.
        """
        if not os.path.exists(self.output_dir):
            print(f"❌ Output directory not found: {self.output_dir}")
            return []
        
        video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.webm']
        videos = []
        
        for ext in video_extensions:
            pattern = os.path.join(self.output_dir, ext)
            for video_path in glob.glob(pattern):
                filename = os.path.basename(video_path)
                
                # Extract scene number from filename (e.g., "scene1.mp4" -> 1)
                scene_number = self._extract_scene_number(filename)
                if scene_number is not None:
                    videos.append((scene_number, filename, video_path))
        
        # Sort by scene number
        videos.sort(key=lambda x: x[0])
        return videos
    
    def _extract_scene_number(self, filename: str) -> Optional[int]:
        """Extract scene number from filename."""
        import re
        
        # Try patterns like "scene1.mp4", "scene_1.mp4", "1.mp4"
        patterns = [
            r'scene(\d+)',
            r'scene_(\d+)',
            r'^(\d+)\.',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def create_video_list_file(self, video_files: List[str], list_file_path: str):
        """Create a text file listing videos for FFmpeg concat."""
        with open(list_file_path, 'w') as f:
            for video_file in video_files:
                # FFmpeg concat requires forward slashes even on Windows
                video_path = video_file.replace('\\', '/')
                f.write(f"file '{video_path}'\n")
    
    def combine_videos_ffmpeg(self, video_files: List[str], output_path: str,
                             add_transitions: bool = True) -> bool:
        """
        Combine videos using FFmpeg.
        
        Args:
            video_files: List of video file paths
            output_path: Output combined video path
            add_transitions: Whether to add fade transitions between scenes
            
        Returns:
            True if successful, False otherwise
        """
        if not self.check_ffmpeg():
            print("❌ FFmpeg not found. Please install FFmpeg first.")
            print("   Download from: https://ffmpeg.org/download.html")
            return False
        
        # Create temporary file list for concat
        list_file_path = os.path.join(self.combined_dir, "video_list.txt")
        self.create_video_list_file(video_files, list_file_path)
        
        try:
            if add_transitions:
                # Complex filter with fade transitions
                return self._combine_with_transitions(video_files, output_path)
            else:
                # Simple concatenation
                cmd = [
                    'ffmpeg', '-y',  # -y to overwrite output file
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', list_file_path,
                    '-c', 'copy',  # Copy without re-encoding (faster)
                    output_path
                ]
                
                print(f"🔄 Combining {len(video_files)} videos...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Videos combined successfully: {output_path}")
                    return True
                else:
                    print(f"❌ FFmpeg error: {result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error combining videos: {e}")
            return False
        finally:
            # Clean up temporary file
            if os.path.exists(list_file_path):
                os.remove(list_file_path)
    
    def _combine_with_transitions(self, video_files: List[str], output_path: str) -> bool:
        """Combine videos with fade transitions between scenes."""
        if len(video_files) < 2:
            return self.combine_videos_ffmpeg(video_files, output_path, add_transitions=False)
        
        # Build complex FFmpeg filter for fade transitions
        inputs = []
        for i, video_file in enumerate(video_files):
            inputs.extend(['-i', video_file])
        
        # Create fade transition filter
        filter_complex = self._build_fade_filter(len(video_files))
        
        cmd = [
            'ffmpeg', '-y'
        ] + inputs + [
            '-filter_complex', filter_complex,
            '-map', f'[v{len(video_files)-1}]',
            '-map', f'[a{len(video_files)-1}]',
            output_path
        ]
        
        print(f"🔄 Combining {len(video_files)} videos with transitions...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Videos combined with transitions: {output_path}")
            return True
        else:
            print(f"❌ FFmpeg transition error: {result.stderr}")
            # Fallback to simple concatenation
            print("🔄 Falling back to simple concatenation...")
            return self.combine_videos_ffmpeg(video_files, output_path, add_transitions=False)
    
    def _build_fade_filter(self, num_videos: int, fade_duration: float = 0.5) -> str:
        """Build FFmpeg filter for fade transitions."""
        filters = []
        
        for i in range(num_videos):
            if i == 0:
                # First video: fade out at the end
                filters.append(f"[{i}:v]fade=t=out:st=0:d={fade_duration}[v{i}]")
                filters.append(f"[{i}:a]afade=t=out:st=0:d={fade_duration}[a{i}]")
            elif i == num_videos - 1:
                # Last video: fade in at the beginning
                filters.append(f"[{i}:v]fade=t=in:st=0:d={fade_duration}[v{i}]")
                filters.append(f"[{i}:a]afade=t=in:st=0:d={fade_duration}[a{i}]")
            else:
                # Middle videos: fade in and out
                filters.append(f"[{i}:v]fade=t=in:st=0:d={fade_duration},fade=t=out:st=0:d={fade_duration}[v{i}]")
                filters.append(f"[{i}:a]afade=t=in:st=0:d={fade_duration},afade=t=out:st=0:d={fade_duration}[a{i}]")
        
        # Concatenate all processed videos
        video_inputs = "".join([f"[v{i}]" for i in range(num_videos)])
        audio_inputs = "".join([f"[a{i}]" for i in range(num_videos)])
        
        filters.append(f"{video_inputs}concat=n={num_videos}:v=1:a=0[vout]")
        filters.append(f"{audio_inputs}concat=n={num_videos}:v=0:a=1[aout]")
        
        return ";".join(filters)
    
    def create_title_card(self, title: str, duration: int = 3) -> str:
        """Create a title card video for the beginning."""
        title_path = os.path.join(self.combined_dir, "title_card.mp4")
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c=white:size=1920x1080:duration={duration}',
            '-vf', f'drawtext=fontfile=arial.ttf:text=\'{title}\':fontcolor=black:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2',
            '-pix_fmt', 'yuv420p',
            title_path
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Title card created: {title_path}")
            return title_path
        except subprocess.CalledProcessError:
            print("❌ Failed to create title card")
            return None
    
    def combine_all_scenes(self, topic_name: str = "Educational Video",
                          add_title_card: bool = True,
                          add_transitions: bool = True) -> Optional[str]:
        """
        Combine all scene videos into a final educational video.
        
        Args:
            topic_name: Name of the educational topic
            add_title_card: Whether to add a title card at the beginning
            add_transitions: Whether to add fade transitions between scenes
            
        Returns:
            Path to combined video if successful, None otherwise
        """
        # Find all scene videos
        scene_videos = self.find_scene_videos()
        
        if not scene_videos:
            print("❌ No scene videos found in the output directory")
            return None
        
        print(f"\n🎬 Found {len(scene_videos)} scene videos:")
        for scene_num, filename, _ in scene_videos:
            print(f"   Scene {scene_num}: {filename}")
        
        # Prepare video files list
        video_files = [video_path for _, _, video_path in scene_videos]
        
        # Add title card if requested
        if add_title_card and self.check_ffmpeg():
            title_card_path = self.create_title_card(topic_name)
            if title_card_path:
                video_files.insert(0, title_card_path)
        
        # Create output filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic_name = "".join(c for c in topic_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        output_filename = f"{safe_topic_name}_{timestamp}.mp4"
        output_path = os.path.join(self.combined_dir, output_filename)
        
        # Combine videos
        success = self.combine_videos_ffmpeg(video_files, output_path, add_transitions)
        
        if success:
            # Get final video info
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"\n🎉 Final video created successfully!")
            print(f"📁 Location: {output_path}")
            print(f"📊 Size: {file_size_mb:.1f} MB")
            print(f"🎬 Total scenes: {len(scene_videos)}")
            
            # Clean up title card
            if add_title_card:
                title_card_path = os.path.join(self.combined_dir, "title_card.mp4")
                if os.path.exists(title_card_path):
                    os.remove(title_card_path)
            
            return output_path
        
        return None
    
    def show_available_scenes(self):
        """Display all available scene videos."""
        scene_videos = self.find_scene_videos()
        
        if not scene_videos:
            print("❌ No scene videos found in the output directory")
            return
        
        print(f"\n🎬 Available Scene Videos:")
        print("-" * 60)
        print(f"{'Scene':<8} {'Filename':<25} {'Size (MB)':<10}")
        print("-" * 60)
        
        for scene_num, filename, video_path in scene_videos:
            size_mb = os.path.getsize(video_path) / (1024 * 1024)
            print(f"{scene_num:<8} {filename:<25} {size_mb:<10.1f}")
        
        print("-" * 60)
        print(f"Total: {len(scene_videos)} scenes")

# CLI Interface
def main():
    """Interactive command-line interface for video combining."""
    combiner = VideoCombiner()
    
    while True:
        print("\n🎬 Motion Canvas Video Combiner")
        print("=" * 40)
        print("1. Show available scenes")
        print("2. Combine all scenes (with transitions)")
        print("3. Combine all scenes (simple)")
        print("4. Combine with custom title")
        print("5. Check FFmpeg installation")
        print("0. Exit")
        print("=" * 40)
        
        try:
            choice = input("Enter your choice (0-5): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                combiner.show_available_scenes()
            elif choice == '2':
                topic_name = input("Enter video title (or press Enter for 'Educational Video'): ").strip()
                if not topic_name:
                    topic_name = "Educational Video"
                result = combiner.combine_all_scenes(topic_name, add_title_card=True, add_transitions=True)
                if result:
                    print(f"🎉 Combined video saved: {result}")
            elif choice == '3':
                topic_name = input("Enter video title (or press Enter for 'Educational Video'): ").strip()
                if not topic_name:
                    topic_name = "Educational Video"
                result = combiner.combine_all_scenes(topic_name, add_title_card=False, add_transitions=False)
                if result:
                    print(f"🎉 Combined video saved: {result}")
            elif choice == '4':
                topic_name = input("Enter custom video title: ").strip()
                if topic_name:
                    result = combiner.combine_all_scenes(topic_name, add_title_card=True, add_transitions=True)
                    if result:
                        print(f"🎉 Combined video saved: {result}")
            elif choice == '5':
                if combiner.check_ffmpeg():
                    print("✅ FFmpeg is installed and ready")
                else:
                    print("❌ FFmpeg not found. Please install FFmpeg first.")
                    print("   Download from: https://ffmpeg.org/download.html")
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
