import subprocess
import os

print("=== FFmpeg Debug Test ===")

# Test 1: Check PATH environment
print(f"Python PATH: {os.environ.get('PATH', 'NOT FOUND')}")

# Test 2: Try running FFmpeg
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
    print(f"✅ FFmpeg found! Return code: {result.returncode}")
    print(f"First line of output: {result.stdout.split(chr(10))[0]}")
except FileNotFoundError:
    print("❌ FFmpeg not found via subprocess")
except Exception as e:
    print(f"❌ Error testing FFmpeg: {e}")

# Test 3: Try direct path
try:
    result = subprocess.run([r'C:\ffmpeg\bin\ffmpeg.exe', '-version'], capture_output=True, text=True, timeout=10)
    print(f"✅ Direct path works! Return code: {result.returncode}")
except Exception as e:
    print(f"❌ Direct path failed: {e}")

# Test 4: Check if file exists
ffmpeg_path = r'C:\ffmpeg\bin\ffmpeg.exe'
if os.path.exists(ffmpeg_path):
    print(f"✅ FFmpeg file exists at: {ffmpeg_path}")
else:
    print(f"❌ FFmpeg file NOT found at: {ffmpeg_path}")
