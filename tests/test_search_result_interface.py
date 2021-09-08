# coding:utf-8
import sys
import os
import json

from PyQt5.QtWidgets import QApplication

from common.meta_data_getter import SongInfoGetter, AlbumInfoGetter
from View.search_result_interface import SearchResultInterface


def getPlaylists():
    """ 获取播放列表 """
    playlists = {}
    folder = "Playlists"
    for file in os.listdir(folder):
        path = f'{folder}/{file}'
        if file.endswith('.json'):
            with open(path, encoding='utf-8') as f:
                playlists[file[:-5]] = json.load(f)
    return playlists


if __name__ == '__main__':
    songInfoGetter = SongInfoGetter(['resource/test_audio'])
    albumInfoGetter = AlbumInfoGetter(songInfoGetter.songInfo_list)
    songInfo_list = songInfoGetter.songInfo_list
    albumInfo_list = albumInfoGetter.albumInfo_list
    playlists = getPlaylists()

    app = QApplication(sys.argv)
    w = SearchResultInterface()
    w.search('aiko', songInfo_list, albumInfo_list, playlists)
    w.show()
    sys.exit(app.exec_())