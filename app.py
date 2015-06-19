# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
An app that syncs the frame range between a scene and a shot in Shotgun.

"""

import sys
import os

from tank.platform import Application
from tank.platform.qt import QtCore, QtGui
import tank


class SetFrameRange(Application):

    def init_app(self):
        """
        App entry point
        """
        # make sure that the context has an entity associated - otherwise it wont work!
        if self.context.entity is None:
            raise tank.TankError("Cannot load the Set Frame Range application! "
                                 "Your current context does not have an entity (e.g. "
                                 "a current Shot, current Asset etc). This app requires "
                                 "an entity as part of the context in order to work.")

        self.engine.register_command("Sync Frame Range with Shotgun", self.run_app)

    def destroy_app(self):
        """
        App teardown
        """
        self.log_debug("Destroying sg_set_frame_range")


    def run_app(self):
        """
        Callback from when the menu is clicked.
        """

        (new_in, new_out, new_range_in, new_range_out) = self.get_frame_range_from_shotgun()
        (current_in, current_out, current_range_in, current_range_out) = self.get_current_frame_range(self.engine.name)

        if new_in is None or new_out is None:
            message =  "Shotgun has not yet been populated with \n"
            message += "in and out frame data for this Shot."

        elif int(new_in) != int(current_in) or int(new_out) != int(current_out) or int(new_range_in) != int(current_range_in) or  int(new_range_out) != int(current_range_out):
            # change!
            message =  "Your scene has been updated with the \n"
            message += "latest frame ranges from shotgun.\n\n"
            message += "Previous start frame: %d (handle: %d)\n" % (current_in, current_range_in)
            message += "New start frame: %d (handle: %d)\n\n" % (new_in, new_range_in)
            message += "Previous end frame: %d (handle: %d)\n" % (current_out, current_range_out)
            message += "New end frame: %d (handle: %d)\n\n" % (new_out, new_range_out)
            self.set_frame_range(self.engine.name, new_in, new_out, new_range_in, new_range_out)

        else:
            # no change
            message = "Already up to date!\n\n"
            message += "Your scene is already in sync with the\n"
            message += "start and end frames in shotgun.\n\n"
            message += "No changes were made."

        # present a pyside dialog
        # lazy import so that this script still loads in batch mode
        from tank.platform.qt import QtCore, QtGui

        QtGui.QMessageBox.information(None, "Frame Range Updated", message)




    ###############################################################################################
    # implementation


    def get_frame_range_from_shotgun(self):
        """
        Returns (in, out) frames from shotgun.
        """
        # we know that this exists now (checked in init)
        entity = self.context.entity

        sg_entity_type = self.context.entity["type"]
        sg_filters = [["id", "is", entity["id"]]]

        sg_in_field = self.get_setting("sg_in_frame_field")
        sg_out_field = self.get_setting("sg_out_frame_field")

        fields = [sg_in_field, sg_out_field, "sg_head_in", "sg_tail_out"]

        data = self.shotgun.find_one(sg_entity_type, filters=sg_filters, fields=fields)

        # check if fields exist!
        if sg_in_field not in data:
            raise tank.TankError("Configuration error: Your current context is connected to a Shotgun "
                                 "%s. This entity type does not have a "
                                 "field %s.%s!" % (sg_entity_type, sg_entity_type, sg_in_field))

        if sg_out_field not in data:
            raise tank.TankError("Configuration error: Your current context is connected to a Shotgun "
                                 "%s. This entity type does not have a "
                                 "field %s.%s!" % (sg_entity_type, sg_entity_type, sg_out_field))

        if "sg_head_in" not in data:
            raise tank.TankError("Configuration error: Your current context is connected to a Shotgun "
                                 "%s. This entity type does not have a "
                                 "field %s.%s!" % (sg_entity_type, sg_entity_type, "sg_head_in"))

        if "sg_tail_out" not in data:
            raise tank.TankError("Configuration error: Your current context is connected to a Shotgun "
                                 "%s. This entity type does not have a "
                                 "field %s.%s!" % (sg_entity_type, sg_entity_type, "sg_tail_out"))            

        return ( data[sg_in_field], data[sg_out_field],  data["sg_head_in"], data["sg_tail_out"])


    def get_current_frame_range(self, engine):

        if engine == "tk-maya":
            import pymel.core as pm
            import maya.cmds as cmds
            current_in = cmds.playbackOptions(query=True, minTime=True)
            current_out = cmds.playbackOptions(query=True, maxTime=True)
            range_in = cmds.playbackOptions(query=True, animationStartTime=True)
            range_out = cmds.playbackOptions(query=True, animationEndTime=True)
        elif engine == "tk-nuke":
            import nuke
            range_in = nuke.root()["first_frame"].value()
            range_out = nuke.root()["last_frame"].value()
            Viewer = nuke.activeViewer().node()
            if Viewer: 
                val = Viewer['frame_range'].value()
                if val != '':
                    current_in, current_out = val.split("-") 
                    current_in = int(current_in)
                    current_out = int(current_out)
                else:
                    current_in = range_in
                    current_out = range_out

            else:
                current_in = range_in
                current_out = range_out


        # elif engine == "tk-motionbuilder":
        #     from pyfbsdk import FBPlayerControl, FBTime

        #     lPlayer = FBPlayerControl()
        #     current_in = lPlayer.LoopStart.GetFrame()
        #     current_out = lPlayer.LoopStop.GetFrame()

        # elif engine == "tk-softimage":
        #     import win32com
        #     xsi = win32com.client.Dispatch('XSI.Application')

        #     current_in = xsi.GetValue("PlayControl.In")
        #     current_out = xsi.GetValue("PlayControl.Out")

        # elif engine == "tk-houdini":
        #     import hou
        #     current_in, current_out = hou.playbar.playbackRange()

        elif engine == "tk-3dsmax":
            from Py3dsMax import mxs
            current_in = mxs.animationRange.start
            current_out = mxs.animationRange.end
        elif engine == "tk-3dsmaxplus":
            import MaxPlus
            ticks = MaxPlus.Core.EvalMAXScript("ticksperframe").GetInt()
            current_in = MaxPlus.Animation.GetAnimRange().Start() / ticks
            current_out = MaxPlus.Animation.GetAnimRange().End() / ticks

        else:
            raise tank.TankError("Don't know how to get current frame range for engine %s!" % engine)

        return (current_in, current_out, range_in, range_out)

    def set_frame_range(self, engine, in_frame, out_frame, in_range, out_range):

        if engine == "tk-maya":
            import pymel.core as pm
            
            # set frame ranges for plackback
            pm.playbackOptions(minTime=in_frame, 
                               maxTime=out_frame,
                               animationStartTime=in_frame,
                               animationEndTime=out_frame)
            
            # set frame ranges for rendering
            defaultRenderGlobals=pm.PyNode('defaultRenderGlobals')
            defaultRenderGlobals.startFrame.set(in_frame)
            defaultRenderGlobals.endFrame.set(out_frame)
           
        elif engine == "tk-nuke":
            import nuke

            # unlock
            locked = nuke.root()["lock_range"].value()
            if locked:
                nuke.root()["lock_range"].setValue(False)
            # set values
            nuke.root()["first_frame"].setValue(in_range)
            nuke.root()["last_frame"].setValue(out_range)

            for n in nuke.allNodes('Viewer'):
                n['frame_range_lock'].setValue(True)
                n['frame_range'].setValue('%i-%i' % (int(in_frame), int(out_frame)))

            # and lock again
            #if locked:
            nuke.root()["lock_range"].setValue(True)

        # elif engine == "tk-motionbuilder":
        #     from pyfbsdk import FBPlayerControl, FBTime

        #     lPlayer = FBPlayerControl()
        #     lPlayer.LoopStart = FBTime(0, 0, 0, in_frame)
        #     lPlayer.LoopStop = FBTime(0, 0, 0, out_frame)

        elif engine == "tk-softimage":
            import win32com
            Application = win32com.client.Dispatch('XSI.Application')
            
            # set playback control
            Application.SetValue("PlayControl.In", in_frame)
            Application.SetValue("PlayControl.Out", out_frame)
            Application.SetValue("PlayControl.GlobalIn", in_frame)
            Application.SetValue("PlayControl.GlobalOut", out_frame)       
            
            # set frame ranges for rendering
            Application.SetValue("Passes.RenderOptions.FrameStart", in_frame)
            Application.SetValue("Passes.RenderOptions.FrameEnd", out_frame)
            

        elif engine == "tk-houdini":
            import hou
            # We have to use hscript until SideFX gets around to implementing hou.setGlobalFrameRange()
            hou.hscript("tset `((%s-1)/$FPS)` `(%s/$FPS)`" % (in_frame, out_frame))            
            hou.playbar.setPlaybackRange(in_frame, out_frame)

        elif engine == "tk-3dsmax":
            from Py3dsMax import mxs
            mxs.animationRange = mxs.interval(in_frame, out_frame)
        elif engine == "tk-3dsmaxplus":
            import MaxPlus 
            ticks = MaxPlus.Core.EvalMAXScript("ticksperframe").GetInt()
            range = MaxPlus.Interval(in_frame * ticks, out_frame * ticks)
            MaxPlus.Animation.SetRange(range)
        
        else:
            raise tank.TankError("Don't know how to set current frame range for engine %s!" % engine)
