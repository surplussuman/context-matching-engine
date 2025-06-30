# Audio Extraction and transcription

import os
import ffmpeg
from faster_whisper import WhisperModel
import datetime

def extract_audio(video_path, output_audio_path="output_audio.wav"):
    """
    Extract audio from a video file and save it as a 16kHz mono WAV file.
    """
    try:
        ffmpeg.input(video_path).output(
            output_audio_path,
            format="wav",
            acodec="pcm_s16le",
            ar=16000,
            ac=1
        ).run(overwrite_output=True)
        print(f"[INFO] Audio extracted to: {output_audio_path}")
        return output_audio_path
    except Exception as e:
        print(f"[ERROR] Audio extraction failed: {e}")
        return None


def transcribe_audio(audio_path, model_size="small", device="cpu"):
    """
    Transcribe audio using Faster Whisper.
    """
    try:
        compute_type = "float16" if device == "cuda" else "int8"
        print(f"[INFO] Loading Whisper model ({model_size}) on {device} ({compute_type})...")
        print(f"[DEBUG]  Before transcraption: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        segments, _ = model.transcribe(audio_path)

        full_transcription = ""
        for segment in segments:
            full_transcription += f"[{segment.start:.2f}s - {segment.end:.2f}s]: {segment.text.strip()}\n"

        print("[INFO] Transcription completed.")
        print(f"[DEBUG] After transcription: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return full_transcription.strip()
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        return None
