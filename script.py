import subprocess
import sys
import os

file_name = sys.argv[1]
name, ext = os.path.splitext(file_name)

probe = subprocess.run("ffprobe -i " + file_name + " -show_entries stream=index -select_streams a -of csv=p=0 -v 0", capture_output=True, text=True)
num_of_channels = len(probe.stdout.split())

def buildFfmpegCommand():
    result = "ffmpeg -y -nostdin -i " + file_name + " -filter_complex \""

    for i in range(num_of_channels):
        result += "[0:a:" + str(i) + "]"

    result += "amix=inputs=" + str(num_of_channels) + ":duration=longest[a]\" -map 0:v -map \"[a]\" -c:v copy " + name + "_MIXED" + ext
    return result
        
result = subprocess.run(buildFfmpegCommand())
sys.exit(result.returncode)

