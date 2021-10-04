
from abc import ABCMeta, abstractproperty
from disco.voice.playable import FFmpegInput, YoutubeDLInput
from disco.types.user import User

try:
    import youtube_dl
    ytdl = youtube_dl.YoutubeDL({'format': 'webm[abr>0]/bestaudio/best', 'default_search': 'ytsearch', 'verbose': 'true'})
except ImportError:
    ytdl = None

class TrackInfo():
    # Define a class with the following properties:
    # - title
    # - uploader
    # - id
    # - length
    # - url
    # - img
    # - extractor

    def __init__(self, title, uploader, id, length, url, img, extractor):
        self.title = title
        self.uploader = uploader
        self.id = id
        self.length = length
        self.url = url
        self.img = img
        self.extractor = extractor

    def __str__(self):
        return self.title + ' - ' + self.uploader

class PlayableTrack(YoutubeDLInput):

    def __init__(self, url: str, requester: User, *args, **kwargs):
        super().__init__(url, *args, **kwargs)
        self.url = url
        self.requester = requester
        self.track_info = {}
        self.results = None

    def get_info(self):
        if '_type' in self.results and self.results['_type'] == 'playlist':
            self.track_info['title'] = self.results['entries'][0]['title']
            self.track_info['uploader'] = self.results['entries'][0]['uploader']
            self.track_info['id'] = self.results['entries'][0]['id']
            self.track_info['length'] = self.results['entries'][0]['duration']
            self.track_info['img'] = self.results['entries'][0]['thumbnail']
        else:
            self.track_info['title'] = self.results['title']
            self.track_info['uploader'] = self.results['uploader']
            self.track_info['id'] = self.results['id']
            self.track_info['length'] = self.results['duration']
            self.track_info['img'] = self.results['thumbnail']
            
        self.track_info['extractor'] = self.results['extractor']
        self.track_info['url'] = self.results['webpage_url']
        self.track_info['original_request'] = self._url
        self.track_info['original_requester'] = None

    def __str__(self):
        return f'{self.info["title"]} by {self.info["uploader"]}'