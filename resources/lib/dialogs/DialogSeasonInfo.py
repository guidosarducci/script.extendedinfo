# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from ..Utils import *
from ..TheMovieDB import *
from ..ImageTools import *
from DialogBaseInfo import DialogBaseInfo
from ..WindowManager import wm
from ..OnClickHandler import OnClickHandler
from .. import VideoPlayer

ch = OnClickHandler()
PLAYER = VideoPlayer.VideoPlayer()


def get_season_window(window_type):

    class DialogSeasonInfo(DialogBaseInfo, window_type):

        def __init__(self, *args, **kwargs):
            super(DialogSeasonInfo, self).__init__(*args, **kwargs)
            self.type = "Season"
            self.tvshow_id = kwargs.get('id')
            data = extended_season_info(tvshow_id=self.tvshow_id,
                                        dbid=kwargs.get("dbid"),
                                        tvshow_dbid=kwargs.get("tvshow_dbid"),
                                        season_number=kwargs.get('season'))
            if not data:
                return None
            self.info, self.data = data
            if "dbid" not in self.info:  # need to add comparing for seasons
                self.info['poster'] = get_file(url=self.info.get("poster", ""))
            self.info['ImageFilter'], self.info['ImageColor'] = filter_image(input_img=self.info.get("poster", ""),
                                                                             radius=25)
            self.listitems = [(1000, self.data["actors"]),
                              (750, self.data["crew"]),
                              (2000, self.data["episodes"]),
                              (1150, self.data["videos"]),
                              (1250, self.data["images"]),
                              (1350, self.data["backdrops"])]

        def onInit(self):
            self.get_youtube_vids("%s %s tv" % (self.info["TVShowTitle"], self.info['title']))
            super(DialogSeasonInfo, self).onInit()
            pass_dict_to_skin(data=self.info,
                              prefix="",
                              window_id=self.window_id)
            self.fill_lists()

        def onClick(self, control_id):
            super(DialogSeasonInfo, self).onClick(control_id)
            ch.serve(control_id, self)

        @ch.click(120)
        def browse_season(self):
            self.close()
            xbmc.executebuiltin("ActivateWindow(videos,videodb://tvshows/titles/%s/%s?tvshowid=%s)" % (self.info["tvshow_dbid"], self.info["season"], self.info["tvshow_dbid"]))

        @ch.click(750)
        @ch.click(1000)
        def open_actor_info(self):
            wm.open_actor_info(prev_window=self,
                               actor_id=self.listitem.getProperty("id"))

        @ch.click(2000)
        def open_episode_info(self):
            wm.open_episode_info(prev_window=self,
                                 tvshow=self.info["TVShowTitle"],
                                 tvshow_id=self.tvshow_id,
                                 season=self.listitem.getProperty("season"),
                                 episode=self.listitem.getProperty("episode"))

        @ch.click(132)
        def open_text(self):
            xbmcgui.Dialog().textviewer(heading=LANG(32037),
                                        text=self.info["Plot"])

    return DialogSeasonInfo
