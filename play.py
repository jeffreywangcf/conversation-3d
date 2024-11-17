import platform
import subprocess

audio_file = "/tmp/play.wav"
os_type = platform.system()
if os_type == "Linux":
    command = 'aplay'
elif os_type == "Darwin":
    command = 'afplay'
else:
    raise Exception("OS type not supported")

subprocess.run([command, audio_file], check=True)