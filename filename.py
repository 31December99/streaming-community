# -*- coding: utf-8 -*-

import os
import re
import init


class Parser:

    def __init__(self, name: str):
        self.__title = None
        self.name = name
        self.type = None

        if self.__search_episodes():
            self.new_file = os.path.join(self.path, f"{self.__title} {self.__sx}{self.__ex}.m3u8")
        else:
            self.__path = init.path_movie
            self.new_file = os.path.join(self.__path, f"{name}.m3u8")

    def capital(self):
        """ divide le parole se la prima lettera è maiuscola"""
        tmp_str = [*self.__title]
        tmp_str += ' '  # fine caratter...
        new_str = ''
        for index, char in enumerate(tmp_str):
            if index < len(tmp_str):
                if (char.isupper() and not tmp_str[index + 1].isupper() and not tmp_str[index - 1].isupper() and
                    tmp_str[index - 1] != '-') and not tmp_str[index - 1].isspace():
                    new_str += ' ' + char
                else:
                    new_str += char
        self.__title = new_str.strip()

    def numbers(self):
        """ distanza un numero se preceduto da una parola"""
        tmp_str = [*self.__title]
        tmp_str += ' '  # fine caratter...
        new_str = ''
        for index, char in enumerate(tmp_str):
            if index < len(tmp_str):
                if char.isdigit() and tmp_str[index - 1].isalpha():
                    new_str += ' ' + char
                else:
                    new_str += char
        self.__title = new_str.strip()

    def remove_chars(self, substr: str) -> int:
        new_str = ''
        for s in substr:
            if s.isnumeric():
                new_str += s
        return int(new_str)

    def __search_episodes(self) -> bool:

        if 'movie' not in self.name.lower():

            """ Cerca SxEx """
            sxe = re.findall(r'[SsEe]\d+', self.name, re.IGNORECASE)
            if len(sxe) > 1:
                self.__sx = f"{str(sxe[0])}"
                self.__ex = f"{str(sxe[1])}"
                name_ = self.name.replace(self.__ex, '')
                name_ = name_.replace(self.__sx, '')
                self.__title = name_.strip()
                self.__path = os.path.join(init.path_serie, self.__title)
                self.type = 'Serie'
                return True

            """ Cerca S:xE:x """
            sxe = re.search(r'S:(\d+) E:(\d+)', self.name, re.IGNORECASE)
            if sxe:
                num = re.findall(r'\d+', sxe.group())
                self.__sx = f"S{str(num[0]).replace(':', '').zfill(2)}"
                self.__ex = f"E{str(num[1]).replace(':', '').zfill(2)}"
                name_ = self.name.replace(sxe.group(), '')
                self.__title = name_.strip()
                self.__path = os.path.join(init.path_serie, self.__title)
                self.type = 'Serie'
                return True

            """ Cerca _Ep_ee"""
            ep = re.search(r'\D(_Ep_\d+)', self.name, re.IGNORECASE)
            if ep:
                self.__sx = "S01"
                self.__ex = ep.group(1).split('Ep')
                self.__title = self.name.replace(ep.group(1), '')
                self.__title = self.__title.replace('_', ' ')
                self.__ex = f"E{str(self.__ex[1].replace('_', '').strip()).zfill(2)}"
                self.capital()
                self.__path = os.path.join(init.path_serie, self.__title)
                self.type = 'Serie'
                return True

            """ Cerca Ep ee"""
            ep = re.search(r'\sEp \d+', self.name, re.IGNORECASE)
            if ep:
                self.__sx = "S01"
                self.__ex = ep[0].split('Ep')
                self.__title = self.name.replace(ep[0], '')
                self.__ex = f"E{str(self.__ex[1].strip()).zfill(2)}"
                self.capital()
                self.__path = os.path.join(init.path_serie, self.__title)
                self.type = 'Serie'
                return True

            """ Cerca Sss_Ep_ee"""
            ep = re.findall(r'S\d+(_Ep_\d+)', self.name, re.IGNORECASE)
            if ep:
                se_tmp = re.findall(r'S(\d+)_', self.name, re.IGNORECASE)
                ep_tmp = ep[0].replace('_Ep_', '')
                self.__sx = f"S{str(se_tmp[0]).zfill(2)}"
                self.__ex = f"E{str(ep_tmp).zfill(2)}"
                self.__title = self.name.replace(f"S{se_tmp[0]}", '')
                self.__title = self.__title.replace(ep[0], '')
                self.__title = self.__title.replace('_', ' ')
                self.capital()
                self.__path = os.path.join(init.path_serie, self.__title)
                self.type = 'Serie'
                return True

            """ Cerca ss_Ep_ee"""
            ep = re.findall(r'\d+(_Ep_\d+)', self.name, re.IGNORECASE)
            if ep:
                str_tmp = ep[0].split('Ep')
                # Se maggiore non è una stagione
                self.__sx = 'S01' if int(
                    str_tmp[1].replace('_', '')) > 50 else f"S{str(str_tmp[1].replace('_', '')).zfill(2)}"
                self.__ex = f"E{str(str_tmp[1].replace('_', '')).zfill(2)}"
                self.__title = self.name.replace(ep[0], '')
                self.__title = self.__title.replace('_', ' ')
                self.capital()
                self.__path = os.path.join(init.path_serie, self.__title)
                self.type = 'Serie'
                return True

            """ Cerca _ee_ """
            # todo: deve essere preceduto da un zero altrimenti considera anche tutti i seguiti di film come serie..
            ep = re.findall(r'_\d+_', self.name, re.IGNORECASE)
            if ep:
                self.__sx = "S01"
                self.__ex = f"E{ep[0].replace('_', '').strip().zfill(2)}"
                self.__title = self.name.replace(ep[0], ' ')
                self.__title = self.__title.replace('_', ' ')
                self.capital()
                self.__path = os.path.join(init.path_serie, self.__title)
                self.type = 'Serie'
                return True

            # Multi episode
            ep = re.findall(r'\d+-\d+', self.name, re.IGNORECASE)
            if ep:
                start_ep = ep[0].split("-")[0]
                self.__sx = "S01"
                self.__ex = f"E{start_ep.replace('0', '').strip().zfill(2)}"
                self.__title = self.name.replace(ep[0], ' ')
                self.__title = self.__title.replace('_', ' ').strip()
                self.capital()
                self.__path = os.path.join(init.path_serie, self.__title)
                self.type = 'Serie'
                return True

            # Solo se il numero è alla fine e preceduto da '0' quando minore di 10 eltrimenti viene considerato come un
            # movie
            ep = re.search(r'\D(\d+)\s*$', self.name, re.IGNORECASE)
            if ep:
                if (int(ep.group(1)) < 10 and '0' in ep.group(1)) or int(ep.group(1)) > 9:
                    if int(ep.group(1)) < 1000:
                        self.__sx = "S01"
                        self.__ex = ep.group(1)
                        self.__ex = self.remove_chars(ep.group(1))
                        self.__title = self.name.replace(ep.group(1), '')
                        self.__title = self.__title.replace('_', ' ')
                        self.__ex = f"E{str(self.__ex).zfill(2)}"
                        self.capital()
                        self.__path = os.path.join(init.path_serie, self.__title)
                        self.type = 'Serie'
                        return True

        """ Cerca il titolo di un film"""
        self.__path = init.path_movie
        self.__title = self.name
        self.__title = self.__title.replace('_', ' ')

        # todo: cosa serve 'Ep' se c'è scritto Movie? ( verificare al prossimo scan)
        self.__title = self.__title.replace(' ep ', '')
        self.__sx = None
        self.__ex = None
        self.type = 'Movie'
        self.capital()
        self.numbers()
        return False

    @property
    def sx(self):
        return self.__sx

    @property
    def ex(self):
        return self.__ex

    @property
    def title(self):
        return self.__title

    @property
    def path(self):
        return self.__path
