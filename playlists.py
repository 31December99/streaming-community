# -*- coding: utf-8 -*-

import os
import re
import sys
import warnings
import m3u8
import requests
import init
from filename import Parser

class Myhttp:
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    @staticmethod
    def head(headThisUrl: str) -> requests:
        try:
            return requests.head(headThisUrl, verify=False)
        except (requests.exceptions.RequestException, ConnectionResetError) as e:
            print(f"[_head] Ho intercettato {e}")
            return e.value

    @staticmethod
    def get(getThisUrl: str) -> requests:
        try:
            return requests.get(getThisUrl, verify=False)
        except (requests.exceptions.RequestException, ConnectionResetError) as e:
            print(f"[_get] Ho intercettato {e}")
            sys.exit()  # Potrebbe andare in errore per un problema temporaneo al server


class Urls(Myhttp):
    SCWS_URL = "https://scws.work/video/"
    BASE_URL = "scws.work/playlist/"

    Q = {'720': f'token={init.TOKEN_720P}&canCast=1&n=1',
         '480': f'token={init.TOKEN_480P}&canCast=1&n=1',
         '360': f'token={init.TOKEN_360P}&canCast=1&n=1'}

    def __init__(self, videoid=38450):
        self.__url = None
        self.parser = None
        self.video_id = videoid
        self.scws = f'{self.SCWS_URL}{self.video_id}'
        self.result = self.head(headThisUrl=self.scws)
        if self.result.status_code == 200:
            scws_data = self.get(getThisUrl=self.scws)
            scws_data = scws_data.json()
            self.__name = scws_data['data']['name']
            self.__name = self.__name.replace('/', ' ')  # carattere invalido per nome file
            self.__name = self.__name.replace('.mp4', '')
            self.__name = self.__name.replace('.mkv', '')
            self.__name = self.__name.replace('.avi', '')
            self.__name = self.__name.replace('%27', "'")
            self.__name = self.__name.replace('%20', ' ')
            self.__name = self.__name.replace('%5b', ' ')
            self.__name = self.__name.replace('%5d', ' ')
            self.__name = self.__name.replace('%C3%B9', 'ù')
            self.__name = self.__name.replace('.', ' ')
            # Universal media player
            self.__name = self.__name.replace('-UMS-', ' ')
            # todo: posto alla fine non permette di rinoscere episodi con numero alla fine vedi sopra r'\D(\d+)\s*$'
            self.__name = self.__name.replace('DVDrip', ' ')

            self.__quality = scws_data['data']['quality']
            if self.__quality == 1080:
                self.__quality = 720
            """ Solitamente quality e durata non presenti e play error nel browser """
            if str(self.__quality) not in self.Q:
                self.result.status_code = "404 Quality"
                return
            self.url = (f"https://{self.BASE_URL}{self.video_id}?type=video&rendition="
                        f"{self.__quality}p&{self.Q[str(self.__quality)]}")
            self.parser = Parser(self.__name)

            if not os.path.exists(self.parser.path):
                os.makedirs(self.parser.path)
            self.m3u8()

    def m3u8(self):
        playlistText = self.get(getThisUrl=self.url)
        playlist = m3u8.loads(playlistText.text)
        if None not in playlist.keys:
            if len(playlist.keys) != 0:
                new_m3u8 = str(playlist.keys[0])
                new_uri = 'https://scws.work/storage/enc.key'
                new_m3u8_str = re.sub(r'(URI=")[^"]+(")', r'\g<1>' + new_uri + r'\g<2>', new_m3u8)
                for segment in playlist.segments.by_key(playlist.keys[-1]):
                    segment.key = new_m3u8_str
                playlist.keys[-1] = new_m3u8_str
        with open(self.parser.new_file, "w") as file:
            file.write(playlist.dumps())
        return self.parser
