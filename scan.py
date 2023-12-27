# -*- coding: utf-8 -*-

import logging
import sys
import requests
import warnings
import playlists
import init
from database import Database
from urllib.parse import urlparse, urlunparse

# LOG
logging.basicConfig(level=logging.INFO)


class Myhttp:
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    @staticmethod
    async def head(headThisUrl: str) -> requests:
        try:
            return requests.head(headThisUrl, verify=False)
        except (requests.exceptions.RequestException, ConnectionResetError) as e:
            print(f"[_head] Ho intercettato {e}")
            return e.value

    @staticmethod
    async def get(getThisUrl: str) -> requests:
        try:
            return requests.get(getThisUrl, verify=False)
        except (requests.exceptions.RequestException, ConnectionResetError) as e:
            print(f"[_get] Ho intercettato {e}")
            sys.exit()  # Potrebbe andare in errore per un problema temporaneo al server


class Scan(Myhttp):
    def __init__(self):
        self.database = None
        self.scws = None
        self.url = None
        self.video_id = None

    async def connection(self):
        self.database = Database("scommunity.db")
        await self.database.connect()
        print("-----------------------------------CONNESSIONE AL DATABASE -----------------------------")

        await self.database.create_table_page(table='Serie')
        await self.database.create_table_page(table='Movie')
        await self.database.create_table_page(table='Anime')
        await self.database.create_table_page(table='Errors')

    async def start(self, video_id=38450) -> bool:

        self.video_id = video_id
        if self.video_id < 38450:  # sembra essere il primo..
            self.video_id = 38450

        video = playlists.Urls(self.video_id)
        if video.parser:
            print(f"[{video.parser.type.upper()}] [{video.parser.title}] {video.url.replace('scws.work', '*****')}")
            await self.database.insert(table=video.parser.type, title=video.parser.title, edit='',
                                       season=video.parser.sx, episode=video.parser.ex,
                                       download_url=video.url, status=None, art=None, tmdbid=None,
                                       videoid=self.video_id)
            await self.database.db.commit()
            return True
        else:
            # print(f"[{video.result.status_code}] {self.video_id}")
            await self.database.insert(table='Errors', title=None, edit=None, season=None, episode=None,
                                       download_url=None, status=video.result.status_code, art=None,
                                       tmdbid=None, videoid=self.video_id)
            await self.database.db.commit()
            return False

    async def update_token_db(self, table: str):
        """
        :param table: Serie o Movie
        :return:
        """
        download_urls = await self.database.load_video(table)
        for title, season, episode, download_url in download_urls:
            __tmp = download_url.split("&token=")
            base_url = __tmp[0]
            if '720p' in download_url:
                new_token = f"{base_url}&token={init.TOKEN_720P}"
                logging.info(new_token)
                await self.database.update_tokendb(table=table, url=new_token, title=title, season=season,
                                                   episode=episode)
            if '480p' in download_url:
                new_token = f"{base_url}&token={init.TOKEN_480P}"
                logging.info(new_token)
                await self.database.update_tokendb(table=table, url=new_token, title=title, season=season,
                                                   episode=episode)
            if '360p' in download_url:
                new_token = f"{base_url}&token={init.TOKEN_360P}"
                logging.info(new_token)
                await self.database.update_tokendb(table=table, url=new_token, title=title, season=season,
                                                   episode=episode)

            self.database.db.commit()

        logging.info("Fine aggiornamento status")

    async def update_download_url(self, table: str):
        download_urls = sorted(await self.database.load_m3u8_offline(table))
        for download_url, _id in download_urls:
            # *** I nuovi token deve essere aggiornati nel file .env **
            # todo: updated_netloc e updated_path per il momento sono dichiarati in .env
            d_url_tmp = download_url.split('?')
            d_url_tmp = d_url_tmp[0].split("/")
            video_id = d_url_tmp[-1]
            parsed_url = urlparse(download_url)
            # Creo un nuovo url con il nuovo netloc e path
            updated_url = urlunparse(
                (parsed_url.scheme, init.UPDATED_NETLOC, init.UPDATED_PATH + video_id, parsed_url.params,
                 parsed_url.query, parsed_url.fragment))
            print(f"[UPDATED] {updated_url}")
            await self.database.update_download_url(table, updated_url, _id)
        await self.database.db.commit()

    async def not_found(self):
        video_list = await self.database.not_found()
        # Se risponde ancora con 404 non inserisce nuovamente il record in 'Errors' in quanto UNIQUE
        for list_id in video_list:
            result = await self.start(video_id=list_id)
            if result:
                await self.database.delete(table='Errors', videoid=list_id)
