#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
import os
from pathlib import Path
from decouple import config

M3U8_FOLDER = config('m3u8_folder')
M3U8_SERIE = config('m3u8_serie')
M3U8_MOVIE = config('m3u8_movie')
DOWNLOAD_FOLDER = config('download_folder')
PLAYLIST_FOLDER = config('playlist_folder')
TOKEN_360P = config('token360p')
TOKEN_480P = config('token480p')
TOKEN_720P = config('token720p')
UPDATED_NETLOC = config('updated_netloc')
UPDATED_PATH = config('updated_path')

download_path = os.path.join(str(Path.home()), "Downloads", M3U8_FOLDER)
path_serie = os.path.join(download_path, M3U8_SERIE)
path_movie = os.path.join(download_path, M3U8_MOVIE)
path_download = os.path.join(download_path, DOWNLOAD_FOLDER)
path_playlist = os.path.join(download_path, PLAYLIST_FOLDER)

