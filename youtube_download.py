import subprocess
import sys

video_link, thread = sys.argv[1], sys.argv[2]
subprocess.call([
	"youtube-dl",
	video_link,
	"--external-downloader",
	"aria2c",
	"--external-downloader-args",
	"-x"+thread
])