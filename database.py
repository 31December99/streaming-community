# -*- coding: utf-8 -*-

import aiosqlite
from unidecode import unidecode


class Database:

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.db = None

    async def connect(self):
        self.db = await aiosqlite.connect(self.file_name)
        return self.db

    async def insert(self, table: str, title: str, edit: str, season: str, episode: str, download_url: str,
                     status: str, art: str, tmdbid: str, videoid: str):
        normalized = unidecode(title) if title else None
        try:
            await self.db.execute(f"INSERT INTO {table} (title,edit,season,episode,videoid,download_url,status,art,"
                                  f"tmdbid,normalized) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                  (
                                      title, edit, season, episode, videoid, download_url, status, art, tmdbid,
                                      normalized))
        except Exception as w:
            print(f"l'url del titolo {title} è gia stato registrato nel database {w}")

    async def create_table_page(self, table: str):

        page_table = f"""CREATE TABLE IF NOT EXISTS {table} (
                        id             INTEGER PRIMARY KEY AUTOINCREMENT
                                               UNIQUE
                                               NOT NULL,
                        title       TEXT,
                        normalized  TEXT,
                        edit        TEXT, 
                        season      TEXT,
                        episode     TEXT, 
                        videoid     TEXT UNIQUE,
                        download_url TEXT UNIQUE,
                        status      TEXT,
                        art         TEXT,   
                        tmdbid      TEXT,
                        overview    TEXT,     
                        poster_path TEXT              
                    );"""

        await self.db.execute(page_table)

    async def load_titles(self, table: str):
        # carico tutti i download urls della tabella
        cursor = await self.db.execute(f"SELECT download_url FROM {table}")
        url = []
        for item in await cursor.fetchall():
            url.append(item[0])
        return url

    async def load_m3u8_offline(self, table: str):
        # Carico tutti i download urls dopo il check degli m3u8 in attesa di essere riscaricati
        cursor = await self.db.execute(f"SELECT download_url,id FROM {table} WHERE status ='OFFLINE'")
        download_urls = []
        for item in await cursor.fetchall():
            download_urls.append(item)
        return download_urls

    async def not_found(self):
        cursor = await self.db.execute(f"SELECT videoid FROM Errors")
        return [int(item[0]) for item in await cursor.fetchall()]

    async def delete(self, table: str, videoid: str):
        await self.db.execute(f"DELETE FROM {table} WHERE videoid=?", (videoid,))
        await self.db.commit()

    async def load_video(self, table: str):
        # carico tutti i download urls della tabella
        cursor = await self.db.execute(f"SELECT title,season,episode,download_url FROM {table}")
        url = []
        for item in await cursor.fetchall():
            url.append(item)
        return url

    async def load_titles_byname(self, table: str, name: str):
        # carico solo i link associati ad una serie o film
        cursor = await self.db.execute(f"SELECT download_url FROM {table} WHERE title=?", (name,))
        url = []
        for item in await cursor.fetchall():
            url.append(item[0])
        return url

    async def update_status(self, table: str, url: str, status: str):
        # aggiorna il campo status con il valore convertito da epoch a datetime
        await self.db.execute(f"UPDATE {table} SET status=? WHERE download_url=?", (status, url))

    async def update_download_url(self, table: str, url: str, _id: str):
        # aggiorna il campo status con il valore convertito da epoch a datetime
        await self.db.execute(f"UPDATE {table} SET download_url=?, status='updated' WHERE id=?", (url, _id))

    async def update_tokendb(self, table: str, url: str, title: str, season: str, episode: str):
        # aggiorna il campo download_url con il valore del nuovo token
        await self.db.execute(f"UPDATE {table} SET download_url=? WHERE title=? AND season=? AND episode=?",
                              (url, title.strip(), season.strip(), episode.strip()))
        await self.db.commit()

    async def close(self):
        await self.db.close()
