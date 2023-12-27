#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
import binascii
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from Crypto.Cipher import AES
import requests
import m3u8


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Network:

    def __init__(self, m3u8_file: str, m3u8_folder: str, download_folder: str):
        self.m3u8_file = m3u8_file
        self.m3u8_folder = m3u8_folder
        self.download_folder = download_folder
        self.failed_dw = []

    @staticmethod
    def console(message: str):
        now = datetime.now()
        date_now = datetime.today().strftime('%d-%m-%Y')
        time_now = now.strftime("%H:%M:%S")
        print(f"<{date_now} {time_now}>{bcolors.OKGREEN}{message}{bcolors.ENDC}")

    def download(self, segment_url):
        """Scarica un segmento specificato da un URL e restituisce il suo contenuto."""
        response = ''
        try:
            response = requests.get(segment_url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError:
            self.failed_dw.append(self.m3u8_file)
            print("FAILED CONTENT DOWNLOAD")
            return response.content

    def decrypt_cbc(self, key, iv, ciphertext):
        """Decrypta il testo (chipertext) con AES in modalità CBC."""
        cipher = AES.new(key, AES.MODE_CBC, iv)
        print(f"{bcolors.WARNING}#{bcolors.ENDC}", end='', flush=True)
        try:
            return cipher.decrypt(ciphertext)
        except ValueError:
            return

    def download_and_decrypt(self, segment_url, key):
        """Scarica un segmento e decrypta"""
        print(f"{bcolors.OKCYAN}D{bcolors.ENDC}", end='', flush=True)
        ciphertext = self.download(segment_url)
        """ Se non esiste una key ritorna il segmento considerato in 'chiaro' """
        if not key:
            return ciphertext
        iv = binascii.unhexlify('43A6D967D5C17290D98322F5C8F6660B')
        return self.decrypt_cbc(key, iv, ciphertext)

    def backstab(self, urls: list, crypt: bool) -> bool:

        # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        # Backastab skill
        # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        if crypt:
            xb = b'\xb2\x07\x82\xcb\xc3*xC\xe7i\x1dU\x95\x0c\x9aj'
        else:
            xb = None
        with ThreadPoolExecutor(max_workers=40) as executor:
            segments = executor.map(lambda url: self.download_and_decrypt(url, xb), urls)
        fail = False
        with open(f"{self.download_folder}{self.m3u8_file}", 'wb') as f:
            for segment in segments:
                if segment is None:
                    fail = True
                    break
                f.write(segment)
                print(f"{bcolors.OKGREEN}*{bcolors.ENDC}", end='', flush=True)
            print("\n")

        if fail:
            print("Errore durante il download di un segmento.Devi riscacaricare la playlist.")
            self.failed_dw = set(self.failed_dw)
            for t in self.failed_dw:
                print(t)
            os.remove(f"{self.download_folder}{self.m3u8_file}")
            return False


class ClientDownloader(Network):

    def __init__(self, m3u8_file: str, m3u8_folder: str, download_folder: str):
        super().__init__(m3u8_file, m3u8_folder, download_folder)

    def start(self):

        # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        # Carica la playlist dal file m3u8 e verifico se il ts file sono criptati
        # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

        ts_files, key = self.load_playlist()
        self.backstab(ts_files, key)

    def load_playlist(self) -> (list, bool):

        with open(f"{self.m3u8_folder}{self.m3u8_file}", "r") as file:
            playlist = m3u8.loads(file.read())

        self.m3u8_file = self.m3u8_file.replace('m3u8', 'mp4')
        self.console(f"[Video] {self.m3u8_file}")

        if playlist.keys[0]:
            if str(playlist.keys[0].uri):
                self.console(f"[Chiave] Presente")
            else:
                self.console(f"[Chiave] * NESSUNA *")
        else:
            self.console(f"[Chiave] * NESSUNA *")

        self.console(f"D = Downloading, # = Decifra, * = Scrive su file")
        return [segment.uri for segment in playlist.segments], False if not playlist.keys[0] else True
