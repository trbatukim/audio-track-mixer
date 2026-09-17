import subprocess
import sys
import shutil
import mimetypes
from pathlib import Path

if len(sys.argv) != 2:
    raise Exception("Too many/few arguments given")

for tool in ["ffmpeg", "ffprobe"]:
    if shutil.which(tool) is None:
        raise Exception(tool + " was not found on PATH. Install FFmpeg and make sure it is on PATH.")

file_name = sys.argv[1]
path = Path(file_name)
count = 0
total = 0

if not path.exists():
    raise Exception("Path not found: " + file_name)

def is_video(file_path):
    if not file_path.is_file():
        return False

    mime_type, _ = mimetypes.guess_type(file_path)

    return mime_type is not None and mime_type.startswith("video/")

def output_for(file_path):
    rel = file_path.relative_to(path)
    out = Path("outputs") / rel.parent / (rel.stem + "_MIXED" + rel.suffix)
    out.parent.mkdir(parents=True, exist_ok=True)
    return out
    
def process_file(in_path, out_path):
    global count, total
    probe = subprocess.run(["ffprobe", "-i", str(in_path), "-show_entries", "stream=index",
                            "-select_streams", "a", "-of", "csv=p=0", "-v", "error"],
                           capture_output=True, text=True)

    if probe.returncode != 0:
        print("Skipping (could not read file): " + str(in_path))
        print("  " + probe.stderr.strip())
        return None

    num_of_channels = len(probe.stdout.split())

    if num_of_channels == 0:
        print("Skipping (no audio): " + str(in_path))
        return None

    result = subprocess.run(build_ffmpeg_command(in_path, out_path, num_of_channels))
    total += 1

    if result.returncode == 0:
        count += 1

    return result.returncode

def build_ffmpeg_command(in_path, out_path, num_of_channels):
    filter_complex = ""

    for i in range(num_of_channels):
        filter_complex += "[0:a:" + str(i) + "]"
    filter_complex += "amix=inputs=" + str(num_of_channels) + ":duration=longest:normalize=0[a]"

    return ["ffmpeg", "-y", "-nostdin", "-i", str(in_path),
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", str(out_path)]

def handle_file(file_path):
    if file_path.is_file():
        if not is_video(file_path):
            raise Exception("Input file is not a video file.")
        
        process_file(file_path, file_path.with_name(file_path.stem + "_MIXED" + file_path.suffix))
    else:
        for child in file_path.iterdir():
            if child.name == "outputs":
                continue
            if child.is_file():
                if not is_video(child):
                    continue
                process_file(child, output_for(child))
            else:
                handle_file(child)

handle_file(path)

print("Successfully squashed " + str(count) + "/" + str(total) + " files.")