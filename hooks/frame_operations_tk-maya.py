# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import maya.cmds as cmds

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

        current_in = cmds.playbackOptions(query=True, minTime=True)
        current_out = cmds.playbackOptions(query=True, maxTime=True)
        current_head = cmds.playbackOptions(query=True, animationStartTime=True)
        current_tail = cmds.playbackOptions(query=True, animationEndTime=True)

        return (current_in, current_out, current_head, current_tail)

    def set_frame_range(self, in_frame=None, out_frame=None, head_frame=None, tail_frame=None, **kwargs):
        """
        set_frame_range will set the frame range using `in_frame` and `out_frame`

        :param int in_frame: in_frame for the current context
            (e.g. the current shot, current asset etc)

        :param int out_frame: out_frame for the current context
            (e.g. the current shot, current asset etc)

        :param int head_frame: head_frame for the current context
            (e.g. the current shot, current asset etc)

        :param int tail_frame: tail_frame for the current context
            (e.g. the current shot, current asset etc)
        """

        self.logger.debug("Setting frame range using values : in={}, out={}, head={}, tail={}".format(in_frame, out_frame, head_frame, tail_frame))

        # set frame ranges for playback
        cmds.playbackOptions(
            minTime=in_frame,  # Sets the start of the playback time range
            maxTime=out_frame,
            animationStartTime=head_frame, # Sets the start time of the animation
            animationEndTime=tail_frame
        )
        
        # set frame ranges for rendering
        cmds.setAttr("defaultRenderGlobals.startFrame", in_frame)
        cmds.setAttr("defaultRenderGlobals.endFrame", out_frame)