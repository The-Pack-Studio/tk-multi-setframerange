# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import hou

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class FrameOperation(HookBaseClass):
    """
    Hook called to perform a frame operation with the
    current scene
    """

    def get_frame_range(self, **kwargs):
        """
        get_frame_range will return a tuple of (in_frame, out_frame)

        :returns: Returns the frame range in the form (in_frame, out_frame, head_frame, tail_frame)
        :rtype: tuple[int, int, int, int]
        """
        # current_in, current_out = hou.playbar.playbackRange()
        # return (current_in, current_out)

        current_in, current_out = hou.playbar.playbackRange()
        current_in = int(current_in)
        current_out = int(current_out)
        current_head = int(hou.text.expandString("$FSTART"))
        current_tail = int (hou.text.expandString("$FEND"))

        return (current_in, current_out, current_head, current_tail)



    def set_frame_range(self, in_frame=None, out_frame=None, head_frame=None, tail_frame=None, **kwargs):
        """
        set_frame_range will set the frame range using `in_frame` and `out_frame` and the head and tail

        :param int in_frame: in_frame for the current context
            (e.g. the current shot, current asset etc)

        :param int out_frame: out_frame for the current context
            (e.g. the current shot, current asset etc)

        :param int head_frame: head_frame for the current context
            (e.g. the current shot, current asset etc)

        :param int tail_frame: tail_frame for the current context
            (e.g. the current shot, current asset etc)
        """

        # We have to use hscript until SideFX gets around to implementing hou.setGlobalFrameRange()

        hou.hscript('set -g NOZSTART = {}'.format(head_frame))
        hou.hscript('set -g NOZEND = {}'.format(tail_frame))
        hou.hscript('set -g NOZCUTSTART = {}'.format(in_frame))
        hou.hscript('set -g NOZCUTEND = {}'.format(out_frame))
        
        hou.hscript("tset `((%s-1)/$FPS)` `(%s/$FPS)`" % (head_frame, tail_frame))            
        hou.playbar.setPlaybackRange(head_frame, tail_frame)