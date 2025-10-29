import os
import sys
import argparse
import subprocess
from pathlib import Path
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


def ms_to_srt_time(ms):
    seconds, ms = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(ms):03}"

def filter_emojis(text:str):
    emo_set = {"😊", "😔", "😡", "😰", "🤢", "😮", "👏", "😀", "😭", "🤧", "😷",
               "❓", "🎼"}
    for ej in emo_set:
        text = text.replace(ej, "")
    return text

def filter_words(text:str):
    text = filter_emojis(text)
    text = text.strip()
    if text == "。" or text == "." or text == "," or text == "？" or text == "?":
        return ""
    else:
        return text

def sentence_info_to_srt(sentence_info):
    srt_lines = []
    count = 1
    for idx, item in enumerate(sentence_info, start=1):
        start_time = ms_to_srt_time(item["start"])
        end_time = ms_to_srt_time(item["end"])
        text = rich_transcription_postprocess(item["sentence"])
        text = filter_words(text)
        if text != "":
            srt_lines.append(f"{count}")
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(text)
            srt_lines.append("")  # Empty line between entries
            count = count + 1
    return "\n".join(srt_lines)


def convert_to_wav(input_path, output_path):
    """Convert mp3/mp4 to wav using ffmpeg, or copy wav directly"""
    if input_path.suffix.lower() == ".wav":
        # Copy wav file directly
        subprocess.run(["cp", str(input_path), str(output_path)], check=True)
    else:
        # Convert to wav
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(output_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def process_audio(model, wav_path, language):
    """Run ASR and save SRT"""
    res = model.generate(
        input=str(wav_path),
        cache={},
        language=language,
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,
        merge_length_s=15,
    )

    print(res)

    sentence_info = res[0]["sentence_info"]
    srt_text = sentence_info_to_srt(sentence_info)

    srt_path = wav_path.with_suffix(".srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_text)
    print(f"✅ Generated SRT: {srt_path}")


def main(input_dir, output_dir, language):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load model once
    print("🚀 Loading model...")
    model = AutoModel(
        model="iic/SenseVoiceSmall",
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30000},
        device="cuda:0",
    )
    print("✅ Model loaded.")

    # Process each audio/video file (with subfolders)
    supported_ext = {".mp4", ".mp3", ".wav", ".wmv"}
    for file in input_dir.rglob("*"):
        if file.is_file() and file.suffix.lower() in supported_ext:
            relative_path = file.relative_to(input_dir)
            wav_output = (output_dir / relative_path).with_suffix(".wav")
            wav_output.parent.mkdir(parents=True, exist_ok=True)

            print(f"🎧 Processing: {file}")
            try:
                convert_to_wav(file, wav_output)
                process_audio(model, wav_output, language)
                os.remove(wav_output)
            except subprocess.CalledProcessError:
                print(f"⚠️ Error converting {file}, skipping.")
            except Exception as e:
                print(f"❌ Error processing {file}: {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch ASR with FunASR")
    parser.add_argument("input_dir", help="Input folder containing mp4/mp3/wav files")
    parser.add_argument("output_dir", help="Output folder for wav and srt files")
    parser.add_argument("--language", default="auto", help="Language (zh, en, yue, ja, ko, nospeech)")
    args = parser.parse_args()

    main(args.input_dir, args.output_dir, args.language)
