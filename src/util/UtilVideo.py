import struct
import logging
import subprocess
import json
from pymediainfo import MediaInfo


def mp4_duration_with_ffprobe(filename):
    try:
        result = subprocess.check_output(f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filename}"', shell=True).decode()
        fields = json.loads(result)['streams'][0]
        duration = 0

        if 'tags' in fields and 'DURATION' in fields['tags']:
            duration = round(float(fields['tags']['DURATION']), 2)
        elif 'duration' in fields:
            duration = round(float(fields['duration']), 2)

        return duration
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.warn("ffprobe not found or an error occurred. Using pymediainfo instead.")

        try:
            media_info = MediaInfo.parse(filename)
            for track in media_info.tracks:
                if track.track_type == "Video":
                    duration = round(track.duration / 1000, 2) if track.duration else None

                    return duration
        except OSError:
            logging.warn("Fail to get video metadata from pymediainfo.")
    except json.JSONDecodeError:
        logging.warn("Fail to get video metadata from ffprobe.")

    return 0
