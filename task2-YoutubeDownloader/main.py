import os
import yt_dlp
import subprocess

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")

def download_video_audio(link, folder_path, quality):
    ydl_opts_video = {
        'format': f'bestvideo[height<={quality}]',
        'outtmpl': os.path.join(folder_path, '%(title)s_video.%(ext)s'),
    }
    ydl_opts_audio = {
        'format': 'bestaudio',
        'outtmpl': os.path.join(folder_path, '%(title)s_audio.%(ext)s'),
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            ydl.download([link])
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            ydl.download([link])
        print("Download is complete")
        return True
    except Exception as e:
        print(f"There was a problem downloading the video: {e}")
        return False

def merge_video_audio(video_path, audio_path, output_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-y',
        output_path
    ]
    print(f"Merging video: {video_path} and audio: {audio_path} into {output_path}")
    subprocess.run(command)
    print(f"Merged file saved as: {output_path}")

    if os.path.exists(video_path):
        os.remove(video_path)
    if os.path.exists(audio_path):
        os.remove(audio_path)

desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
folder_path = os.path.join(desktop_path, 'Youtube Downloads')
create_folder(folder_path)

urls = []
qualities = []

while True:
    link = str(input("Enter the URL (or 'x' to stop): ")).strip()
    if link.lower() == 'x':
        break
    urls.append(link)
    while True:
        quality = input(f"Enter the desired quality for video {len(urls)} (144, 240, 360, 480, 720, 1080, 1440, 2160, 4320): ").strip()
        if quality.isdigit() and int(quality) in [144, 240, 360, 480, 720, 1080, 1440, 2160, 4320]:
            qualities.append(quality)
            break
        else:
            print("Invalid input. Please enter a valid resolution.")

for index, link in enumerate(urls):
    quality = qualities[index]
    while not download_video_audio(link, folder_path, quality):
        quality = input(f"Enter a different video quality for video {index + 1} (144, 240, 360, 480, 720, 1080, 1440, 2160, 4320): ").strip()
        qualities[index] = quality

video_files = [f for f in os.listdir(folder_path) if f.endswith('_video.webm')]
audio_files = [f for f in os.listdir(folder_path) if f.endswith('_audio.webm')]

print("Video files found:", video_files)
print("Audio files found:", audio_files)

for video_file in video_files:
    video_path = os.path.join(folder_path, video_file)
    audio_file = video_file.replace('_video.webm', '_audio.webm')
    audio_path = os.path.join(folder_path, audio_file)
    output_file = video_file.replace('_video.webm', '.mp4')
    output_path = os.path.join(folder_path, output_file)
    print(f"Output path: {output_path}")
    merge_video_audio(video_path, audio_path, output_path)
