# -*- coding: utf-8 -*-
import argparse
import asyncio
import os
import logging
import init
from scan import Scan
from downloader import ClientDownloader


# LOG
logging.basicConfig(level=logging.INFO)


class Scbot:

    def __init__(self):
        self.loop = asyncio.get_event_loop()

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
                folder = os.listdir(init.path_playlist)
                for video_file in folder:
                    if video_file.endswith(".m3u8"):
                        downloader = ClientDownloader(m3u8_file=video_file)
                        downloader.start()


        except KeyboardInterrupt:
            pass
        finally:
            pass


if __name__ == "__main__":

    if os.name == 'nt':
        os.system('color')

    if not os.path.exists(init.path_serie):
        os.makedirs(init.path_serie)

    if not os.path.exists(init.path_movie):
        os.makedirs(init.path_movie)

    if not os.path.exists(init.path_download):
        os.makedirs(init.path_download)

    if not os.path.exists(init.path_playlist):
        os.makedirs(init.path_playlist)

    scbot = Scbot()
    scbot.loop.run_until_complete(scbot.start())
