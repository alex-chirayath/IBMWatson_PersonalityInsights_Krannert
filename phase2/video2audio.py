import imageio

# uncomment below if ffmpeg needs to be installed
# imageio.plugins.ffmpeg.download()

from moviepy.editor import *

"""
	Reads a video file, extracts audio and saves it to a new file

	Arguments: 	video_filename - Name of input video file
				audio_filename - Name of audio file to be created
				fps - Frames per second
				nbytes - Sample width (2 for 16-bit, 4 for 32-bit)
	Return: void
"""
def convert_vid2aud(video_filename, audio_filename, fps = 44100, nbytes = 2):
	videoclip = VideoFileClip(video_filename)
	audioclip = videoclip.audio

	audioclip.write_audiofile(audio_filename, fps, nbytes)