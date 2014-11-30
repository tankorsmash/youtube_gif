import requests
import copy
import string
import urlparse
import youtube_dl
import urllib

from dateutil.parser import parse as dateparse
from moviepy.editor import VideoFileClip

vid_url = r"https://www.youtube.com/watch?v=WtkILPy2ew0&feature=youtu.be&t=34s"

def parse_url_for_timestamp(url):

	parsed_url = urlparse.urlparse(url)
	qs = urlparse.parse_qs(parsed_url.query)

	raw_time = None
	if 't' in qs:
		raw_time = qs['t'][0]
	elif 't=' in parsed_url.fragment:
		raw_time = parsed_url.fragment.split('=')[1] #assume only one frag

	result = (0, 0)
	if raw_time:
		try:
			raw = dateparse(raw_time)
			result = raw.minute, raw.second
		except Exception as e:
			print 'date error:',e
			result = (0, 0)
		else:
			print 'resulting time', result

	return result

def download_url(downloader, url):
	orig_params = downloader.params

	final_vid_title = "Error?"
	final_time_tuple = (0, 0)

	try:
		new_params = copy.copy(orig_params)
		print 'trying url', url
		if 'you' not in url:
			url = "http://youtube.com/watch/?"+url
		info = downloader.extract_info(url, download=False)

		vid_title = info.get('title', 'Untitled').replace(' ', '_').encode('utf8', 'ignore').translate(string.maketrans("", ""), string.punctuation)
		vid_title = ''.join([i if ord(i) < 128 else ' ' for i in vid_title])
		vid_id = info.get('id', 'ID-less')
		final_time_tuple = parse_url_for_timestamp(url)


		final_vid_title = (vid_title+"__"+vid_id).decode('utf', 'ignore').encode('utf8')
		new_params['outtmpl'] = "/home/tankorsmash/scripts/"+final_vid_title.decode('utf')
		downloader.params = new_params
		downloader.download([url])

	except Exception as e:
		print
		print 'ERROR!!'
		print e
		import ipdb; ipdb.set_trace() #todo

		print

	finally:
		downloader.params = orig_params

	return final_vid_title, final_time_tuple

def get_clip(video_title, start=(0,0), seconds=5):
	print 'getting clip of video_title', video_title
	video = VideoFileClip("/home/tankorsmash/scripts/"+video_title)

	end = (start[0], start[1]+seconds)
	clip = video.subclip(start, end)

	return clip

def make_gif(clip, gif_title=None):
	if not gif_title:
		gif_title = "UntitledGif.gif"
	if not gif_title.endswith('.gif'):
		gif_title+=".gif"

	#clip.write_gif(gif_title)
	clip.write_gif("/home/tankorsmash/scripts/"+gif_title, program='ffmpeg')
	return gif_title

def upload_to_gfycat(gif_title):
	try:
		response = requests.post(r"http://upload.gfycat.com/transcode?fetchUrl=tankorsmash.webfactional.com/raw/%s"%(gif_title,))
				#params=dict(fetchUrl="tankorsmash.webfactional.com/raw/%s"% gif_title))
		if response.json().get('error', "").startswith("Connection timeout"):
			print 'Please try again in a sec, this is a long upload'
		elif response.json().get('error'):
			print response.json()['error']
		else:
			print '\nCongrats! Your Gfycat is', response.json()['gifUrl']
			print '<a href="%s" target="_blank"><img src="%s"></a>' % (response.json()['gifUrl'], response.json()['gifUrl'])
	except Exception as e:
		print e
		print response.content


def get_gif(url):
	url = urllib.unquote(url)
	downloader = youtube_dl.YoutubeDL({
		"outtmpl": "%(id)s",
		"noplaylist" : True,
		"quiet" : True
		})
	video_title, start_tuple = download_url(downloader, url)
	clip = get_clip(video_title, start=start_tuple, seconds=6)
	gif_title = make_gif(clip, video_title)
	upload_to_gfycat(gif_title)

	print '\nsuccess! the new gif is called:', gif_title


if __name__ == "__main__":
	import sys
	if len(sys.argv) == 1:
		get_gif(vid_url)
	else: 
		get_gif(sys.argv[1])
