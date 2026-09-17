# audio-track-mixer

Mixes all audio tracks of a video into a single track. Originally made for exporting multiple [SteelSeries Moments](https://steelseries.com/gg/moments) clips at once.

The video stream is copied untouched, so this is fast and lossless on the picture. Only the
audio is re-encoded.

## Requirements

- Python 3
- FFmpeg (both `ffmpeg` and `ffprobe` must be on `PATH`)

## Usage

A single file:

```
python script.py recording.mp4
```

Writes `recording_MIXED.mp4` next to the input.

A folder:

```
python script.py C:\Recordings
```

Walks the folder and all its subfolders, and writes the results into `outputs\`, mirroring
the input structure:

```
C:\Recordings\stream\day1.mkv  ->  outputs\stream\day1_MIXED.mkv
C:\Recordings\clips\day1.mkv   ->  outputs\clips\day1_MIXED.mkv
```

`outputs\` is created in the current working directory, not inside the input folder.

## What gets skipped

Non-video files are ignored, based on the MIME registry. Videos are skipped, with a message,
when they have no audio tracks or when FFmpeg can't read them. The run finishes either way.

Existing output files are overwritten without asking.

## Notes

Tracks are summed at full level (`amix` with `normalize=0`) rather than being scaled down by
the number of tracks, so a four-track recording doesn't come out quiet. If your source tracks
are already close to peak, the mix can clip.

Extension detection relies in
part on the system's MIME registry, so it can vary between machines.
