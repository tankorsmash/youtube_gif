import copy
import youtube_dl
from moviepy.editor import VideoFileClip

vid_url = r"https://www.youtube.com/watch?v=E2JpTN0qBZs&list=UU3tNpTOHsTnkmbwztCs30sA"
vid_url = r"https://www.youtube.com/watch?v=wISNp3V3LfA&feature=youtu.be&t=5m"

def download_url(downloader, url):
    orig_params = downloader.params

    final_vid_title = "Error?"

    try:
        new_params = copy.copy(orig_params)
        info = downloader.extract_info(url, download=False)
        vid_title = info.get('title', 'Untitled').replace(' ', '_')
        vid_id = info.get('id', 'ID-less')

        final_vid_title = (vid_title+"__"+vid_id).encode('ascii', 'ignore').decode('utf8')
        new_params['outtmpl'] = final_vid_title
        downloader.params = new_params
        downloader.download([url])
    except Exception as e:
        print
        print 'ERROR!!'
        print e
    finally:
        downloader.params = orig_params

    return final_vid_title

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

    clip.write_gif(gif_title, program='ffmpeg')
    return gif_title


def main():
    downloader = youtube_dl.YoutubeDL({
        "outtmpl": "%(id)s",
        "noplaylist" : True,
        })
    video_title = download_url(downloader, vid_url)
    clip = get_clip(video_title, start=(5,0))
    gif_title = make_gif(clip, video_title)

    print '\nsuccess! the new gif is called:', gif_title


if __name__ == "__main__":
    main()
