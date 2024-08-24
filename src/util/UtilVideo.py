import struct


def get_video_metadata(filename):
    import subprocess, json

    result = subprocess.check_output(
            f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filename}"',
            shell=True).decode()

    fields = json.loads(result)['streams'][0]
    duration = 0

    if 'tags' in fields and 'DURATION' in fields['tags']:
        duration = round(float(fields['tags']['DURATION']), 2)
    elif 'duration' in fields:
        duration = round(float(fields['duration']), 2)

    width = fields.get('width', 0)
    height = fields.get('height', 0)
    return duration, width, height
