'''
(*)~----------------------------------------------------------------------------------
 Pupil - eye tracking platform
 Copyright (C) 2012-2016  Pupil Labs

 Distributed under the terms of the GNU Lesser General Public License (LGPL v3.0).
 License details are in the file license.txt, distributed as part of this software.
----------------------------------------------------------------------------------~(*)
'''

from plugin import Plugin

import numpy as np
from pyglui import ui
import zmq
import json
import socket

import logging
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)


class My_Server(Plugin):
    PORT = "5566"
    """pupil server plugin"""
    def __init__(self, g_pool,address=""):#tcp://192.168.0.117:5566
        super(My_Server, self).__init__(g_pool)
        self.order = .9
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.address = "tcp://"+self.getLocalIP()+":"+PORT
        self.set_server(address)
        self.menu = None


    def init_gui(self):
        if self.g_pool.app == 'capture':
            self.menu = ui.Growing_Menu("My Broadcast Server")
            self.g_pool.sidebar.append(self.menu)
        elif self.g_pool.app == 'player':
            self.menu = ui.Scrolling_Menu("My Broadcast Server")
            self.g_pool.gui.append(self.menu)

        self.menu.append(ui.Button('Close',self.close))
        help_str = "Pupil Message server: Using ZMQ and the *Publish-Subscribe* scheme"
        self.menu.append(ui.Info_Text(help_str))
        self.menu.append(ui.Text_Input('address',self,setter=self.set_server,label='Address'))


    def deinit_gui(self):
        if self.menu:
            if self.g_pool.app == 'capture':
                self.g_pool.sidebar.remove(self.menu)
            elif self.g_pool.app == 'player':
                self.g_pool.gui.remove(self.menu)
            self.menu = None


    def set_server(self,new_address):
        try:
            self.socket.unbind(self.address)
            logger.debug('Detached from %s'%self.address)
        except:
            pass
        try:
            self.socket.bind(new_address)
            self.address = new_address
            logger.debug('Bound to %s'%self.address)

        except zmq.ZMQError as e:
            logger.error("Could not set Socket: %s. Reason: %s"%(new_address,e))



    def update(self,frame,events):
        """only sent pupil position on plane
        """

        for p in events.get('gaze_positions',[]):   
            plane_name = "unnamed"
            topic = 'realtime gaze on ' + plane_name 
            if p.has_key(topic) and self.inRange(p[topic]):
                self.socket.send_multipart((topic, json.dumps(p[topic])))
                logger.debug(topic+"  "+str(p[topic][0])+" "+str(p[topic][1]))

    def inRange(self, points):
        x = points[0]
        y = points[1]
        
        if 0<=x and x<=1 and 0<=y and y<=1:
            return True
        else:
            return False

    def close(self):
        self.alive = False


    def get_init_dict(self):
        return {'address':self.address}


    def cleanup(self):
        """gets called when the plugin get terminated.
        This happens either voluntarily or forced.
        """
        self.deinit_gui()
        self.context.destroy()

    def getLocalIP(self):
        return socket.gethostbyname(socket.gethostname())


            




