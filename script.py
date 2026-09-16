import subprocess
import sys
import os
from pathlib import Path

file_name = sys.argv[1]
path = Path(file_name)
    
def process_file(name, ext, file_mode):
    probe = subprocess.run("ffprobe -i " + name + ext + " -show_entries stream=index -select_streams a -of csv=p=0 -v 0", capture_output=True, text=True)
    num_of_channels = len(probe.stdout.split())

    result = subprocess.run(build_ffmpeg_command(name, ext, num_of_channels, file_mode))
    return result.returncode

def build_ffmpeg_command(name, ext, num_of_channels, file_mode):
    result = "ffmpeg -y -nostdin -i " + name + ext + " -filter_complex \""

    for i in range(num_of_channels):
        result += "[0:a:" + str(i) + "]"

    result += "amix=inputs=" + str(num_of_channels) + ":duration=longest[a]\" -map 0:v -map \"[a]\" -c:v copy "

    if file_mode:
        result += name + "_MIXED" + ext
    else:
        result += "outputs\\" + os.path.basename(name) + "_MIXED" + ext

    return result

if path.is_file():
    name, ext = os.path.splitext(file_name)
    process_file(name, ext, True)
else:
    for file in path.iterdir():
        output_path = Path("outputs")
        output_path.mkdir(exist_ok=True)

        name, ext = os.path.splitext(file)
        process_file(name, ext, False)