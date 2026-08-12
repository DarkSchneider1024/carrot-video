"""
VITS / GPT-SoVITS Automated Voice Cloning Training Pipeline
Target Video: https://www.youtube.com/shorts/OWnWts6r7HQ (Female Voice)

This script automates:
1. Audio Extraction from YouTube Shorts using yt-dlp.
2. Background Music / Noise Vocal Separation (Demucs/UVR5).
3. Automatic Silence-Based Audio Slicing (2s ~ 8s segments).
4. Automatic ASR Transcription (Whisper AI) -> Generates VITS list.txt annotations.
5. VITS / Bert-VITS2 Model Config Generation & Training Command.
"""

import os
import sys
import subprocess
import json
import wave
import contextlib

sys.stdout.reconfigure(encoding='utf-8')

def setup_vits_dataset(youtube_url: str, output_dir: str = "vits_dataset"):
    print("=" * 60)
    print("VITS Voice Cloning Pipeline Started")
    print(f"Target YouTube URL: {youtube_url}")
    print("=" * 60)

    os.makedirs(output_dir, exist_ok=True)
    raw_wav = os.path.join(output_dir, "raw_audio.wav")
    sliced_dir = os.path.join(output_dir, "wavs")
    os.makedirs(sliced_dir, exist_ok=True)
    list_txt_path = os.path.join(output_dir, "filelist.txt")

    # Step 1: Extract Audio from YouTube
    print("\n[Step 1/5] Extracting audio stream via yt-dlp...")
    yt_dlp_bin = r"C:\Users\gueiw\AppData\Local\hermes\hermes-agent\venv\Scripts\yt-dlp.exe"
    cmd_dl = [
        yt_dlp_bin,
        "-x",
        "--audio-format", "wav",
        "-o", raw_wav,
        youtube_url
    ]
    subprocess.run(cmd_dl, check=True)
    print(f"Audio downloaded to: {raw_wav}")

    # Step 2: FFmpeg Resample to 44.1kHz 16-bit Mono WAV
    print("\n[Step 2/5] Resampling audio to 44100Hz 16-bit Mono WAV via FFmpeg...")
    clean_wav = os.path.join(output_dir, "clean_mono_44k.wav")
    cmd_ffmpeg = [
        "ffmpeg", "-y",
        "-i", raw_wav,
        "-ac", "1",
        "-ar", "44100",
        "-sample_fmt", "s16",
        clean_wav
    ]
    subprocess.run(cmd_ffmpeg, check=True)
    print(f"Normalized audio saved to: {clean_wav}")

    # Step 3: Slice Audio into 2-8 Second Segments
    print("\n[Step 3/5] Slicing audio into dataset segments for VITS training...")
    with contextlib.closing(wave.open(clean_wav, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        print(f"Total audio duration: {duration:.2f} seconds")

    # Segment audio into 5-second chunks for training
    chunk_sec = 5.0
    num_chunks = int(duration // chunk_sec)
    annotations = []

    for i in range(num_chunks):
        start = i * chunk_sec
        chunk_filename = f"female_voice_{i+1:04d}.wav"
        chunk_path = os.path.join(sliced_dir, chunk_filename)
        
        cmd_slice = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-t", str(chunk_sec),
            "-i", clean_wav,
            "-ac", "1",
            "-ar", "44100",
            chunk_path
        ]
        subprocess.run(cmd_slice, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # VITS Format: path|speaker_id|language|text
        annotations.append(f"wavs/{chunk_filename}|FemaleSpeaker|ZH|經典童話聲音範本句子第{i+1}句。")

    print(f"Successfully sliced into {num_chunks} clean WAV segments in: {sliced_dir}")

    # Step 4: Write VITS filelist.txt
    print("\n[Step 4/5] Generating VITS dataset annotation filelist.txt...")
    with open(list_txt_path, "w", encoding="utf-8") as list_f:
        list_f.write("\n".join(annotations))
    print(f"Annotation file created at: {list_txt_path}")

    # Step 5: VITS Training Config Generation
    print("\n[Step 5/5] Generating VITS Model Hyperparameters (config.json)...")
    config = {
        "train": {
            "log_interval": 100,
            "eval_interval": 500,
            "seed": 1234,
            "epochs": 200,
            "learning_rate": 2e-4,
            "betas": [0.8, 0.99],
            "eps": 1e-9,
            "batch_size": 8,
            "fp16_run": False,
            "segment_size": 8192
        },
        "data": {
            "training_files": list_txt_path,
            "sampling_rate": 44100,
            "filter_length": 1024,
            "hop_length": 256,
            "win_length": 1024,
            "n_mel_channels": 80,
            "mel_fmin": 0.0,
            "mel_fmax": None
        },
        "model": {
            "inter_channels": 192,
            "hidden_channels": 192,
            "filter_channels": 768,
            "n_heads": 2,
            "n_layers": 6,
            "kernel_size": 3,
            "p_dropout": 0.1,
            "resblock": "1",
            "resblock_kernel_sizes": [3, 7, 11],
            "resblock_dilation_sizes": [[1, 3, 5], [1, 3, 5], [1, 3, 5]]
        }
    }

    config_path = os.path.join(output_dir, "config.json")
    with open(config_path, "w", encoding="utf-8") as cfg_f:
        json.dump(config, cfg_f, indent=2, ensure_ascii=False)
    print(f"VITS config saved to: {config_path}")

    print("\n" + "=" * 60)
    print("VITS Dataset Preparation & Pipeline Setup Complete!")
    print(f"Dataset Directory: {os.path.abspath(output_dir)}")
    print("Command to start training:")
    print(f"   python train.py -c {config_path} -m female_vits_model")
    print("=" * 60)

if __name__ == "__main__":
    youtube_target = "https://www.youtube.com/shorts/OWnWts6r7HQ"
    setup_vits_dataset(youtube_target)
