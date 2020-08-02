import sys
import os
import re

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

from ..my_functions.is_not_leave import isNotLeave
from ..my_functions.get_album_cover_path import getAlbumCoverPath
from .window_mask import WindowMask


class SongInfoCard(QWidget):
    """ 播放栏左侧歌曲信息卡 """
    clicked = pyqtSignal()

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        # 保存信息
        self.setSongInfo(songInfo)
        # 实例化小部件
        self.albumPic = QLabel(self)
        self.windowMask = WindowMask(self, (0, 0, 0, 50))
        self.scrollTextWindow = ScrollTextWindow(songInfo, self)
        # 初始化界面
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(115 + 15 + self.scrollTextWindow.width() + 25,115)
        self.setAttribute(Qt.WA_StyledBackground | Qt.WA_TranslucentBackground)
        self.scrollTextWindow.move(130, 0)
        self.albumPic.resize(115, 115)
        # 获取封面路径
        self.setAlbumCover()
        # 如果传入的歌曲信息为空，就隐藏
        if not self.songInfo:
            self.hide()

    def setSongInfo(self, songInfo: dict):
        """ 设置歌曲信息 """
        self.songInfo = songInfo
        self.songName = self.songInfo.get('songName','')
        self.songerName = self.songInfo.get('songer','')

    def updateSongInfoCard(self, songInfo: dict):
        """ 更新歌曲信息卡 """
        if songInfo:
            self.show()
            self.setSongInfo(songInfo)
            self.scrollTextWindow.initUI(songInfo)
            self.resize(115 + 15 + self.scrollTextWindow.width() + 25,115)
            self.setAlbumCover()
        else:
            self.hide()

    def enterEvent(self, e):
        """ 鼠标进入时显示遮罩 """
        if self.scrollTextWindow.isSongNameTooLong and not self.scrollTextWindow.songNameTimer.isActive(
        ):
            self.scrollTextWindow.songNameTimer.start()
        if self.scrollTextWindow.isSongerNameTooLong and not self.scrollTextWindow.songerNameTimer.isActive(
        ):
            self.scrollTextWindow.songerNameTimer.start()
        self.windowMask.show()

    def leaveEvent(self, e):
        self.windowMask.hide()

    def setAlbumCover(self):
        """ 设置封面 """
        # 如果专辑信息为空就直接隐藏
        if not self.songInfo.get('album'):
            self.hide()
            return
        self.coverPath = getAlbumCoverPath(self.songInfo.get('album',' ')[-1])
        self.albumPic.setPixmap(
            QPixmap(self.coverPath).scaled(
                115, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mouseReleaseEvent(self, e):
        """ 鼠标松开发送信号 """
        self.clicked.emit()


class ScrollTextWindow(QWidget):
    """ 滚动字幕 """
    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent)
        self.hasInitWidget = False
        # 实例化定时器
        self.songPauseTimer = QTimer(self)
        self.songNameTimer = QTimer(self)
        self.songerNameTimer = QTimer(self)
        self.songerPauseTimer = QTimer(self)
        # 初始化界面
        self.initUI(songInfo)

    def setSongInfo(self, songInfo: dict):
        """ 更新歌曲信息 """
        self.songInfo = songInfo
        self.songName = self.songInfo.get('songName','')
        self.songerName = self.songInfo.get('songer','')

    def initUI(self, songInfo: dict):
        """ 重置所有属性 """
        # 设置刷新时间和移动距离
        self.timeStep = 19
        self.moveStep = 1
        self.songCurrentIndex = 0
        self.songerCurrentIndex = 0
        # 设置字符串溢出标志位
        self.isSongNameAllOut = False
        self.isSongerNameAllOut = False
        # 设置两段字符串之间留白的宽度
        self.spacing = 25
        # 初始化界面
        self.setSongInfo(songInfo)
        self.initWidget()
        self.update()

    def initWidget(self):
        """ 初始化界面 """
        self.adjustWindowWidth()
        if not self.hasInitWidget:
            #self.setFixedHeight(115)
            self.setAttribute(Qt.WA_StyledBackground)
            # 初始化定时器
            self.songPauseTimer.setInterval(400)
            self.songerPauseTimer.setInterval(400)
            self.songNameTimer.setInterval(self.timeStep)
            self.songerNameTimer.setInterval(self.timeStep)
            self.songNameTimer.timeout.connect(self.updateSongIndex)
            self.songerNameTimer.timeout.connect(self.updateSongerIndex)
            self.songPauseTimer.timeout.connect(self.restartTextTimer)
            self.songerPauseTimer.timeout.connect(self.restartTextTimer)
        # 根据字符串宽度是否大于窗口宽度开启滚动：
        if self.songNameTimer.isActive():
            self.songNameTimer.stop()
        if self.songerNameTimer.isActive():
            self.songerNameTimer.stop()
        if self.isSongNameTooLong:
            self.songNameTimer.start()
        if self.isSongerNameTooLong:
            self.songerNameTimer.start()
        self.hasInitWidget = True

    def getTextWidth(self):
        """ 计算文本的总宽度 """
        # 计算大写字母个数
        self.__countCapitalLetters()
        songFontMetrics = QFontMetrics(QFont('Microsoft YaHei', 14, 400))
        self.songNameWidth = sum(
            [songFontMetrics.width(i) for i in self.songName]) + 7 * self.songCapLetterNum
        # 检测歌手名是否全是英文
        self.isMatch = re.match(r'^[a-zA-Z]+$', self.songerName)
        if not self.isMatch:
            songerFontMetrics = QFontMetrics(QFont('Microsoft YaHei', 12, 500))
        else:
            songerFontMetrics = QFontMetrics(QFont('Microsoft YaHei', 11, 500))
        # 总是会少一个字符的长度
        self.songerNameWidth = sum(
            [songerFontMetrics.width(i) for i in self.songerName]) + 8 + 4 * self.songerCapLetterNum

    def adjustWindowWidth(self):
        """ 根据字符串长度调整窗口宽度 """
        self.getTextWidth()
        maxWidth = max(self.songNameWidth, self.songerNameWidth)
        # 判断是否有字符串宽度超过窗口的最大宽度
        self.isSongNameTooLong = self.songNameWidth > 250
        self.isSongerNameTooLong = self.songerNameWidth > 250
        # 设置窗口的宽度
        self.resize(min(maxWidth, 250), 115)

    def updateSongIndex(self):
        """ 更新歌名下标 """
        self.update()
        self.songCurrentIndex += 1
        # 设置下标重置条件
        resetSongIndexCond = self.songCurrentIndex * \
            self.moveStep >= self.songNameWidth + self.spacing * self.isSongNameAllOut
        # 只要条件满足就要重置下标并将字符串溢出置位，保证在字符串溢出后不会因为留出的空白而发生跳变
        if resetSongIndexCond:
            self.songCurrentIndex = 0
            self.isSongNameAllOut = True

    def updateSongerIndex(self):
        """ 更新歌手名下标 """
        self.update()
        self.songerCurrentIndex += 1
        resetSongerIndexCond = self.songerCurrentIndex * \
            self.moveStep >= self.songerNameWidth + self.spacing * self.isSongerNameAllOut
        if resetSongerIndexCond:
            self.songerCurrentIndex = 0
            self.isSongerNameAllOut = True

    def paintEvent(self, e):
        """ 绘制文本 """
        painter = QPainter(self)
        painter.setPen(Qt.white)
        # 绘制歌名
        painter.setFont(QFont('Microsoft YaHei', 14))
        if self.isSongNameTooLong:
            # 实际上绘制了两段完整的字符串
            # 从负的横坐标开始绘制第一段字符串
            x1 = self.spacing * self.isSongNameAllOut - \
                self.moveStep * self.songCurrentIndex
            painter.drawText(x1, 54, self.songName)
            # 绘制第二段字符串
            x2 = self.songNameWidth - self.moveStep * self.songCurrentIndex + \
                self.spacing * (1 + self.isSongNameAllOut)
            painter.drawText(x2, 54, self.songName)
            # 循环一次后就将滚动停止
            if self.isSongNameAllOut and not (x1 and x2):
                # 判断鼠标是否离开,离开的话就停止滚动
                notLeave = isNotLeave(self)
                if not notLeave:
                    self.songNameTimer.stop()
                else:
                    self.songNameTimer.stop()
                    self.songPauseTimer.start()
        else:
            painter.drawText(0, 54, self.songName)

        # 绘制歌手名
        if not self.isMatch:
            painter.setFont(QFont('Microsoft YaHei', 12, 75))
        else:
            painter.setFont(QFont('Microsoft YaHei', 11, 75))
        if self.isSongerNameTooLong:
            x3 = self.spacing * self.isSongerNameAllOut - self.moveStep * \
                self.songerCurrentIndex
            x4 = self.songerNameWidth - self.moveStep * self.songerCurrentIndex + \
                self.spacing * (1 + self.isSongerNameAllOut)
            painter.drawText(x3, 82, self.songerName)
            painter.drawText(x4, 82, self.songerName)
            if self.isSongerNameAllOut and not (x3 and x4):
                notLeave = isNotLeave(self)
                if not notLeave:
                    self.songerNameTimer.stop()
                else:
                    self.songerNameTimer.stop()
                    self.songerPauseTimer.start()
        else:
            painter.drawText(0, 82, self.songerName)

    def enterEvent(self, e):
        """ 鼠标进入时打开滚动效果 """
        if self.isSongNameTooLong and not self.songNameTimer.isActive():
            self.songNameTimer.start()
        if self.isSongerNameTooLong and not self.songerNameTimer.isActive():
            self.songerNameTimer.start()

    def restartTextTimer(self):
        """ 重新打开指定的定时器 """
        self.sender().stop()
        if self.sender() == self.songPauseTimer:
            self.songNameTimer.start()
        else:
            self.songerNameTimer.start()

    def __countCapitalLetters(self):
        """ 计算大写字母个数 """
        # 特殊字符按大写字母算
        specialCharacters="（）()！!"
        self.songerCapLetterNum = sum(
            [1 for i in self.songerName if i.isupper() or i in specialCharacters])
        self.songCapLetterNum = sum(
            [1 for i in self.songName if i.isupper() or i in specialCharacters])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    songInfo = {
        'songName': 'ハッピーでバッドな眠りは浅い',
        'songer': '鎖那',
        'album': [r'resource\Album Cover\ハッピーでバッドな眠りは浅い\ハッピーでバッドな眠りは浅い.png']
    }
    demo = SongInfoCard(songInfo)
    demo.setStyleSheet('background:rgb(129,133,137)')
    demo.show()
    sys.exit(app.exec_())