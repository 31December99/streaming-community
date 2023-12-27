#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
import argparse
import asyncio
import os
import logging
from pathlib import Path

from scan import Scan
from decouple import config
from downloader import ClientDownloader

M3U8_FOLDER = config('m3u8_folder')
M3U8_SERIE = config('m3u8_serie')
M3U8_MOVIE = config('m3u8_movie')
DOWNLOAD_FOLDER = config('download_folder')
PLAYLIST_FOLDER = config('playlist_folder')

# LOG
logging.basicConfig(level=logging.INFO)


class Scbot:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        download_path = os.path.join(str(Path.home()), "Downloads", M3U8_FOLDER)

        path = os.path.join(download_path, M3U8_SERIE)
        if not os.path.exists(path):
            os.makedirs(path)

        path = os.path.join(download_path, M3U8_MOVIE)
        if not os.path.exists(path):
            os.makedirs(path)

        self.path_download = os.path.join(download_path, DOWNLOAD_FOLDER)
        if not os.path.exists(path):
            os.makedirs(path)

        self.path_playlist = os.path.join(download_path, PLAYLIST_FOLDER)
        if not os.path.exists(path):
            os.makedirs(path)



    async def start(self):

        try:
            parser = argparse.ArgumentParser(description='Comandi per il downloader', add_help=False)

            """ Obbligatorio """
            parser.add_argument('-video_id', '--video_id', type=int,
                                help='scarica solo un m3u8 ID')

            parser.add_argument('-range', '--range', nargs=2, type=int,
                                help='scansiona un range di m3u8 ID')

            parser.add_argument('-dw', '--dw', action='store_true',
                                help='Scarica i video con gli m3u8 nella cartella M3U8_FOLDER')

            args = parser.parse_args()

            """ Ottengo un più files by range ID """
            if args.range:
                min_range, max_range = args.range
                sc = Scan()
                await sc.connection()
                for v_id in range(min_range, max_range + 1):
                    await sc.start(video_id=v_id)
                await sc.database.close()

            """ Ottengo un solo file by ID """
            if args.video_id:
                sc = Scan()
                await sc.connection()
                await sc.start(video_id=args.video_id)
                await sc.database.close()

            """ scarico tutti i video da m3u8 presenti nella cartella play_list folder """
            if args.dw:
                folder = os.listdir(PLAYLIST_FOLDER)
                for video_file in folder:
                    if video_file.endswith(".m3u8"):
                        downloader = ClientDownloader(m3u8_file=video_file, m3u8_folder=self.path_playlist,
                                                      download_folder=self.path_download)
                        downloader.start()


        except KeyboardInterrupt:
            pass
        finally:
            pass


if __name__ == "__main__":

    if os.name == 'nt':
        os.system('color')

    scbot = Scbot()
    scbot.loop.run_until_complete(scbot.start())
