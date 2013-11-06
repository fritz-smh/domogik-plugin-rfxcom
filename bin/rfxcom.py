#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

RFXCOM

Implements
==========

- RfxcomManager

@author: Fritz <fritz.smh@gmail.com>
@copyright: (C) 2007-2013 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.xpl.common.xplmessage import XplMessage
from domogik.xpl.common.plugin import XplPlugin

from domogik_packages.plugin_rfxcom.lib.rfxcom import Rfxcom
from domogik_packages.plugin_rfxcom.lib.rfxcom import RfxcomException
import threading
import traceback


class RfxcomManager(XplPlugin):
    """ Manage the RFXCOM usb device
    """

    def __init__(self):
        """ Init plugin
        """
        XplPlugin.__init__(self, name='rfxcom')

        # check if the plugin is configured. If not, this will stop the plugin and log an error
        if not self.check_configured():
            return

        # get the devices list
        # for this plugin, if no devices are created we won't be able to use devices.
        # but.... if we stop the plugin right now, we won't be able to detect existing device and send events about them
        # so we don't stop the plugin if no devices are created
        self.devices = self.get_device_list(quit_if_no_device = False)

        # get the rfxcom device address in the filesystem
        self.rfxcom_device = self.get_config("device")
        self.rfxcom_manager = Rfxcom(self.log, self.send_xpl, self.get_stop(), self.rfxcom_device, self.device_detected, self.send_xpl, self.register_thread, self.options.test_option)

        # create listeners for commands send over xPL
        # TODO

        # Open the RFXCOM device
        try:
            self.rfxcom_manager.open()
        except RfxcomException as e:
            self.log.error(e.value)
            print(e.value)
            self.force_leave()
            return
            
        # Start reading RFXCOM
        rfxcom_process = threading.Thread(None,
                                   self.rfxcom_manager.listen,
                                   "rfxcom-process-reader",
                                   (self.get_stop(),),
                                   {})
        self.register_thread(rfxcom_process)
        rfxcom_process.start()

        self.ready()


    def send_xpl(self, message = None, schema = None, data = {}):
        """ Send xPL message on network
        """
        if message != None:
            self.log.debug("send_xpl : send full message : {0}".format(message))
            self.myxpl.send(message)

        else:
            self.log.debug("send_xpl : Send xPL message xpl-trig : schema:{0}, data:{1}".format(schema, data))
            msg = XplMessage()
            msg.set_type("xpl-trig")
            msg.set_schema(schema)
            for key in data:
                msg.add_data({key : data[key]})
            self.myxpl.send(msg)



if __name__ == "__main__":
    RfxcomManager()
