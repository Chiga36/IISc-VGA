#!/usr/bin/env python3

"""
Frame to Video Converter for Motion Canvas

This script takes the generated frame images from Motion Canvas rendering
and combines them into MP4 video files using FFmpeg.
"""

import os
import glob
import subprocess
import sys
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

class FrameToVideoConverter:
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.ensure_output_dir()
        self.ffmpeg_path = self.find_ffmpeg()

    def clean_output_frames(self):
        deleted = 0;
        for frame_file in self.output_dir.rglob('*.png'):
            try:
                frame_file.unlink()
                deleted += 1
            except Exception as e:
                print(f"❌ Failed to delete {frame_file}: {e}")
        print(f"🗑️ Deleted {deleted} frame files")


    def find_ffmpeg(self):
        """Find FFmpeg binary"""
        # Try local FFmpeg first
        local_ffmpeg = PROJECT_ROOT / "node_modules" / "@ffmpeg-installer" / "linux-x64" / "ffmpeg"
        if local_ffmpeg.exists():
            return str(local_ffmpeg)

        # Try system FFmpeg
        try:
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        return "ffmpeg"  # Hope it's in PATH

    def ensure_output_dir(self):
        """Ensure output directory exists"""
        self.output_dir.mkdir(exist_ok=True)

    def find_frame_sequences(self):
        """Find all frame sequences in the output directory"""
        sequences = {}

        # Look for frame patterns in output directory and subdirectories
        frame_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            frame_files.extend(list(self.output_dir.rglob(ext)))  # Recursive search

        print(f"🔍 Found {len(frame_files)} image files")

        for frame_file in frame_files:
            filename = frame_file.name
            parent_dir = frame_file.parent.name

            # Try to extract sequence info from filename
            # Patterns like: 000001.png, frame-001.png, etc.
            patterns = [
                r'(\d{6})\.(png|jpg|jpeg)$',  # 000001.png (Motion Canvas default)
                r'(.+)-(\d{6})\.(png|jpg|jpeg)$',  # project-000001.png
                r'(.+)-frame-(\d+)\.(png|jpg|jpeg)$',  # scene1-frame-001.png
                r'(.+)_(\d+)\.(png|jpg|jpeg)$',  # scene1_001.png
                r'(.+)-(\d+)\.(png|jpg|jpeg)$',  # scene1-001.png
            ]

            sequence_name = parent_dir  # Use parent directory as default sequence name
            frame_num = None

            for pattern in patterns:
                match = re.match(pattern, filename)
                if match:
                    if len(match.groups()) == 2:  # Just frame number and extension
                        frame_num = int(match.group(1))
                    else:  # Has base name too
                        base_name = match.group(1)
                        frame_num = int(match.group(2))
                        if base_name != "frame":  # Don't use generic "frame" as name
                            sequence_name = f"{parent_dir}_{base_name}"
                    break

            if frame_num is not None:
                if sequence_name not in sequences:
                    sequences[sequence_name] = []
                sequences[sequence_name].append((frame_num, frame_file))

        # Sort frames by number
        for sequence_name in sequences:
            sequences[sequence_name].sort(key=lambda x: x[0])

        return sequences

    def create_video_from_frames(self, scene_name, frame_list, fps=30):
        """Create MP4 video from frame sequence using FFmpeg"""
        if not frame_list:
            print(f"❌ No frames found for {scene_name}")
            return None

        print(f"🎬 Creating video for {scene_name} from {len(frame_list)} frames")

        # Create scene directory
        scene_dir = self.output_dir / scene_name
        scene_dir.mkdir(exist_ok=True)

        video_path = scene_dir / f"{scene_name}.mp4"

        # Sort frames and create a temporary file list for FFmpeg
        sorted_frames = sorted(frame_list, key=lambda x: x[0])

        # Create a pattern for FFmpeg input
        if sorted_frames:
            first_frame = sorted_frames[0][1]
            frame_pattern = str(first_frame).replace(str(sorted_frames[0][0]).zfill(6), "%06d")

            # If the pattern doesn't work, use concat method
            temp_list_file = self.output_dir / f"temp_frames_{scene_name}.txt"

            with open(temp_list_file, 'w') as f:
                for frame_num, frame_path in sorted_frames:
                    f.write(f"file '{frame_path}'\n")
                    f.write(f"duration {1/fps}\n")
                # Add last frame again for proper ending
                if sorted_frames:
                    f.write(f"file '{sorted_frames[-1][1]}'\n")

            # FFmpeg command using concat demuxer
            ffmpeg_cmd = [
                self.ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", str(temp_list_file),
                "-vf", f"fps={fps}",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18",
                "-y",  # Overwrite output
                str(video_path)
            ]

            print(f"🔧 Running FFmpeg: {' '.join(ffmpeg_cmd[:8])}...")

            try:
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)

                # Clean up temp file
                temp_list_file.unlink(missing_ok=True)

                if result.returncode == 0:
                    if video_path.exists() and video_path.stat().st_size > 1000:
                        file_size = video_path.stat().st_size / (1024 * 1024)  # MB
                        print(f"✅ Video created: {video_path} ({file_size:.1f}MB)")

                        # Also create a copy in the main output directory
                        main_video_path = self.output_dir / f"{scene_name}.mp4"
                        subprocess.run(['cp', str(video_path), str(main_video_path)], check=False)
                        print(f"📁 Copy saved to: {main_video_path}")

                        return video_path
                    else:
                        print(f"❌ Video file created but seems empty: {video_path}")
                        return None
                else:
                    print(f"❌ FFmpeg failed: {result.stderr}")
                    return None

            except subprocess.TimeoutExpired:
                print(f"❌ FFmpeg timeout for {scene_name}")
                temp_list_file.unlink(missing_ok=True)
                return None
            except Exception as e:
                print(f"❌ FFmpeg error: {e}")
                temp_list_file.unlink(missing_ok=True)
                return None

        return None

    def convert_all_sequences(self, fps=30):
        """Convert all found frame sequences to videos"""
        sequences = self.find_frame_sequences()

        if not sequences:
            print("❌ No frame sequences found!")
            print("💡 Make sure Motion Canvas has generated frame images in the output directory")
            return []

        print(f"🎯 Found {len(sequences)} frame sequences:")
        for name, frames in sequences.items():
            print(f"   📸 {name}: {len(frames)} frames")

        created_videos = []

        for scene_name, frame_list in sequences.items():
            video_path = self.create_video_from_frames(scene_name, frame_list, fps)
            if video_path:
                created_videos.append(video_path)

        return created_videos

    def convert_specific_scene(self, scene_name, fps=30):
        """Convert frames for a specific scene"""
        sequences = self.find_frame_sequences()

        # Look for matching scene
        matching_sequences = {k: v for k, v in sequences.items()
                            if scene_name.lower() in k.lower() or k.lower() in scene_name.lower()}

        if not matching_sequences:
            print(f"❌ No frame sequence found for scene: {scene_name}")
            print(f"Available sequences: {list(sequences.keys())}")
            return None

        if len(matching_sequences) > 1:
            print(f"⚠️ Multiple sequences found for {scene_name}: {list(matching_sequences.keys())}")
            print("Converting the first match...")

        scene_key = list(matching_sequences.keys())[0]
        frame_list = matching_sequences[scene_key]

        return self.create_video_from_frames(scene_name, frame_list, fps)

def main():
    converter = FrameToVideoConverter()

def main():
    converter = FrameToVideoConverter()

    # Check for --no-cleanup flag to prevent frame deletion
    clean_frames = True
    args = sys.argv[1:]
    if '--no-cleanup' in args:
        clean_frames = False
        args.remove('--no-cleanup')

    if len(args) > 0:
        # Convert specific scene
        scene_name = args[0]
        fps = int(args[1]) if len(args) > 1 else 30

        print(f"🎬 Converting frames to video for scene: {scene_name}")
        video_path = converter.convert_specific_scene(scene_name, fps)

        if video_path:
            print(f"\n🎉 Video created successfully: {video_path}")
            # Only delete frames if cleanup is enabled
            if clean_frames:
                converter.clean_output_frames()
        else:
            print(f"\n❌ Failed to create video for {scene_name}")
            sys.exit(1)
    # ...existing code...
    else:
        # Convert all sequences
        print("🎬 Converting all frame sequences to videos...")
        videos = converter.convert_all_sequences()

        if videos:
            print(f"\n🎉 Successfully created {len(videos)} videos:")
            for video in videos:
                print(f"   📹 {video}")
        else:
            print("\n❌ No videos were created")
            sys.exit(1)

if __name__ == "__main__":
    main()
