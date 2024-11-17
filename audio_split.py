import librosa
import soundfile as sf
import numpy as np
import os
from pyannote.audio import Pipeline


def write_audio(file_name, audio_data, sample_rate, output_dir):
    output_path = os.path.join(output_dir, file_name)
    sf.write(output_path, audio_data, sample_rate)
    print(f"{file_name} saved to: {output_path}")


def separate_speakers(pipeline, input_file):
    output_dir = 'output/'
    y, sr = librosa.load(input_file, sr=None)
    diarization = pipeline(input_file, num_speakers=2)
    output_data = {}
    speakers = {}
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        if speaker not in speakers:
            speakers[speaker] = f"part{len(speakers) + 1}.wav"
            output_data[speakers[speaker]] = np.zeros_like(y)
        start_sample = int(turn.start * sr)
        end_sample = int(turn.end * sr)
        output_data[speakers[speaker]][start_sample:end_sample] = y[start_sample:end_sample]
    os.makedirs(output_dir, exist_ok=True)
    for file_name, audio_data in output_data.items():
        write_audio(file_name, audio_data, sr, output_dir)


if __name__ == "__main__":
    api_token = os.getenv("API_TOKEN")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=api_token)
    separate_speakers(pipeline, "debate.wav")
