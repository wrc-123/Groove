# coding:utf-8
from unittest import TestCase
from app.common.lyric_parser import KuWoLyricParser


class TestLyricParser(TestCase):
    """ 测试歌词解析器 """

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)

    def test_kuwo_lyric_parser(self):
        """ 测试酷我音乐歌词解析器 """
        lyric1 = [
            {
                "lineLyric": "See You Again - Wiz Khalifa&Charlie Puth",
                "time": "0.15"
            },
            {
                "lineLyric": "It's been a long day without you my friend",
                "time": "10.74"
            },
            {
                "lineLyric": "没有老友你的陪伴 日子真是漫长",
                "time": "17.7"
            },
            {
                "lineLyric": "And I'll tell you all about it when I see you again",
                "time": "17.7"
            },
            {
                "lineLyric": "与你重逢之时 我会敞开心扉倾诉所有",
                "time": "23.5"
            }
        ]

        lyric1_res = {
            '0.15': ['See You Again - Wiz Khalifa&Charlie Puth'],
            '10.74': ["It's been a long day without you my friend", '没有老友你的陪伴 日子真是漫长'],
            '17.7': ["And I'll tell you all about it when I see you again",
                     '与你重逢之时 我会敞开心扉倾诉所有']
        }

        lyric2 = [
            {
                "lineLyric": "恋をしたのは - Aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "词：aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "曲：aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "ああ恋をしたのは",
                "time": "0.93"
            },
            {
                "lineLyric": "啊 堕入爱河",
                "time": "31.38"
            },
            {
                "lineLyric": "今降るこの雨",
                "time": "31.38"
            },
            {
                "lineLyric": "眼前仍飘落着霏霏细雨",
                "time": "34.4"
            }
        ]

        lyric2_res = {
            '0.0': ['恋をしたのは - Aiko', '词：aiko', '曲：aiko'],
            '0.93': ['ああ恋をしたのは', '啊 堕入爱河'],
            '31.38': ['今降るこの雨', '眼前仍飘落着霏霏细雨']
        }

        lyric3 = [
            {
                "lineLyric": "恋をしたのは - Aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "词：aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "曲：aiko",
                "time": "0.0"
            },
            {
                "lineLyric": "ああ恋をしたのは",
                "time": "0.93"
            },
        ]

        lyric3_res = {
            '0.0': ['恋をしたのは - Aiko', '词：aiko', '曲：aiko'],
            '0.93': ['ああ恋をしたのは'],
        }

        self.assertEqual(KuWoLyricParser.parse(lyric1), lyric1_res)
        self.assertEqual(KuWoLyricParser.parse(lyric2), lyric2_res)
        self.assertEqual(KuWoLyricParser.parse(lyric3), lyric3_res)
        self.assertEqual(KuWoLyricParser.parse(None), {'0.0': ['暂无歌词']})
        self.assertEqual(KuWoLyricParser.parse([]), {'0.0': ['暂无歌词']})