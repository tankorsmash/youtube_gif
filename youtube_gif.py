import copy
import string
import urlparse
import youtube_dl

from dateutil.parser import parse as dateparse
from moviepy.editor import VideoFileClip

vid_url = r"https://www.youtube.com/watch?v=CulczSynxjk&feature=youtu.be&t=1s"

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
        info = downloader.extract_info(url, download=False)

        vid_title = info.get('title', 'Untitled').replace(' ', '_').encode('utf8', 'ignore').translate(string.maketrans("", ""), string.punctuation)
        vid_id = info.get('id', 'ID-less')
        final_time_tuple = parse_url_for_timestamp(url)

        final_vid_title = (vid_title+"__"+vid_id).encode('ascii', 'ignore').decode('utf8')
        new_params['outtmpl'] = final_vid_title
        downloader.params = new_params
        downloader.download([url])

    except Exception as e:
        print
        print 'ERROR!!'
        print e
        print

    finally:
        downloader.params = orig_params

    return final_vid_title, final_time_tuple

def get_clip(video_title, start=(0,0), seconds=5):
    video = VideoFileClip(video_title)

    end = (start[0], start[1]+seconds)
    clip = video.subclip(start, end)

    return clip

def make_gif(clip, gif_title=None):
    if not gif_title:
        gif_title = "UntitledGif.gif"
    if not gif_title.endswith('.gif'):
        gif_title+=".gif"

    # clip.write_gif(gif_title)
    clip.write_gif(gif_title, program='ffmpeg')
    return gif_title


def main():
    downloader = youtube_dl.YoutubeDL({
        "outtmpl": "%(id)s",
        "noplaylist" : True,
        })
    video_title, start_tuple = download_url(downloader, vid_url)
    clip = get_clip(video_title, start=start_tuple, seconds=6)
    gif_title = make_gif(clip, video_title)

    print '\nsuccess! the new gif is called:', gif_title


if __name__ == "__main__":
    main()
