# coding:utf-8
from typing import List

from common.crawler import QueryServerType
from common.database.entity import SongInfo
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from components.song_list_widget import NoScrollSongListWidget, SongCardType
from components.song_list_widget.song_card import PlaylistInterfaceSongCard
from components.widgets.menu import AddToMenu, DownloadMenu, RoundMenu
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QAction


class SongCardListContextMenu(RoundMenu):
    """ Context menu of song list widget """

    def __init__(self, showDownload=False, parent=None):
        super().__init__("", parent)
        self.playAct = QAction(self.tr("Play"), self)
        self.nextSongAct = QAction(self.tr("Play next"), self)
        self.deleteAct = QAction(self.tr("Delete from playlist"), self)
        self.showAlbumAct = QAction(self.tr("Show album"), self)
        self.viewOnlineAct = QAction(self.tr('View online'), self)
        self.editInfoAct = QAction(self.tr("Edit info"), self)
        self.showPropertyAct = QAction(self.tr("Properties"), self)
        self.selectAct = QAction(self.tr("Select"), self)
        self.addToMenu = AddToMenu(self.tr("Add to"), self)
        self.downloadMenu = DownloadMenu(self.tr("Download"), self)

        self.addActions([self.playAct, self.nextSongAct])
        self.addMenu(self.addToMenu)
        self.addActions([self.deleteAct, self.showAlbumAct, self.viewOnlineAct, self.editInfoAct])
        if showDownload:
            self.addMenu(self.downloadMenu)

        self.addAction(self.showPropertyAct)
        self.addSeparator()
        self.addAction(self.selectAct)


class SongListWidget(NoScrollSongListWidget):
    """ Playlist interface song list widget """

    playSignal = pyqtSignal(int)   # 将当前歌曲切换为指定的歌曲卡

    def __init__(self, songInfos: List[SongInfo], parent=None):
        """
        Parameters
        ----------
        songInfos:list
            song information list

        parent:
            父级窗口
        """
        super().__init__(songInfos, SongCardType.PLAYLIST_INTERFACE_SONG_CARD, parent)
        self.resize(1150, 758)
        self.createSongCards()
        setStyleSheet(self, 'song_list_widget')

    def contextMenuEvent(self, e: QContextMenuEvent):
        hitIndex = self.indexAt(e.pos()).column()
        if hitIndex < 0:
            return

        showDownload = self.currentSongInfo.file.startswith("http")
        contextMenu = SongCardListContextMenu(showDownload, self)
        self.__connectMenuSignalToSlot(contextMenu)
        contextMenu.exec(self.cursor().pos())

    def __onPlayButtonClicked(self, index):
        """ play button clicked slot """
        self.playSignal.emit(index)
        # the following line can't be deleted, because there may be duplicate songs
        self.setPlay(index)

    def __onSongCardDoubleClicked(self, index):
        """ song card double clicked slot """
        if self.isInSelectionMode:
            return

        self.playSignal.emit(index)

    def __onRemoveButtonClicked(self, index, songCard=None):
        """ remove button clicked slot """
        songInfo = songCard.songInfo if songCard else self.sender().songInfo
        self.removeSongCard(index)
        self.removeSongSignal.emit(songInfo)

    def _connectSongCardSignalToSlot(self, songCard: PlaylistInterfaceSongCard):
        """ connect song card signal to slot """
        songCard.doubleClicked.connect(self.__onSongCardDoubleClicked)
        songCard.removeSongSignal.connect(self.__onRemoveButtonClicked)
        songCard.playButtonClicked.connect(self.__onPlayButtonClicked)
        songCard.clicked.connect(self.setCurrentIndex)
        songCard.checkedStateChanged.connect(
            self.onSongCardCheckedStateChanged)

    def __connectMenuSignalToSlot(self, menu: SongCardListContextMenu):
        """ connect context menu signal to slot """
        menu.editInfoAct.triggered.connect(self.showSongInfoEditDialog)
        menu.showPropertyAct.triggered.connect(self.showSongPropertyDialog)
        menu.viewOnlineAct.triggered.connect(
            lambda: signalBus.getSongDetailsUrlSig.emit(self.currentSongInfo, QueryServerType.WANYI))
        menu.playAct.triggered.connect(
            lambda: signalBus.playOneSongCardSig.emit(self.currentSongInfo))
        menu.nextSongAct.triggered.connect(
            lambda: signalBus.nextToPlaySig.emit([self.currentSongInfo]))
        menu.deleteAct.triggered.connect(
            lambda: self.__onRemoveButtonClicked(self.currentRow(), self.currentSongCard))
        menu.selectAct.triggered.connect(
            lambda: self.currentSongCard.setChecked(True))
        menu.showAlbumAct.triggered.connect(
            lambda: signalBus.switchToAlbumInterfaceSig.emit(
                self.currentSongCard.album,
                self.currentSongCard.singer
            )
        )

        menu.addToMenu.playingAct.triggered.connect(
            lambda: signalBus.addSongsToPlayingPlaylistSig.emit([self.currentSongInfo]))
        menu.addToMenu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, self.songInfos))
        menu.addToMenu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit([self.currentSongInfo]))

        menu.downloadMenu.downloadSig.connect(
            lambda quality: signalBus.downloadSongSig.emit(self.currentSongInfo, quality))
