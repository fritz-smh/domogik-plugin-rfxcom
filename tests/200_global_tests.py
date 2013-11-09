#!/usr/bin/python
# -*- coding: utf-8 -*-

from domogik.xpl.common.plugin import XplPlugin
from domogik.tests.common.plugintestcase import PluginTestCase
from domogik.tests.common.testplugin import TestPlugin
from domogik.tests.common.testdevice import TestDevice
from domogik.tests.common.testsensor import TestSensor
from domogik.common.utils import get_sanitized_hostname
from datetime import datetime
import unittest
import sys
import os
import traceback

class RfxcomTestCase(PluginTestCase):

    def test_0100_dummy(self):
        """ dummy test
        """
        pass



if __name__ == "__main__":
    ### configuration

    # set up the xpl features
    xpl_plugin = XplPlugin(name = 'test', 
                           daemonize = False, 
                           parser = None, 
                           nohub = True,
                           test  = True)

    # set up the plugin name
    name = "rfxcom"

    # set up the configuration of the plugin
    # configuration is done in test_0010_configure_the_plugin with the cfg content
    # notice that the old configuration is deleted before
    cfg = { 'configured' : True }
    cfg = { 'device' : '/dev/rfxcom' }
   

    ### start tests

    # load the test devices class
    td = TestDevice()

    # delete existing devices for this plugin on this host
    client_id = "{0}-{1}.{2}".format("plugin", name, get_sanitized_hostname())
    try:
        td.del_devices_by_client(client_id)
    except: 
        print(u"Error while deleting all the test device for the client id '{0}' : {1}".format(client_id, traceback.format_exc()))
        sys.exit(1)

    # create a test device
    # for this test we don't create any device
    
    ### prepare and run the test suite
    suite = unittest.TestSuite()
    # check domogik is running, configure the plugin
    suite.addTest(RfxcomTestCase("test_0001_domogik_is_running", xpl_plugin, name, cfg))
    suite.addTest(RfxcomTestCase("test_0010_configure_the_plugin", xpl_plugin, name, cfg))
    
    # start the plugin
    suite.addTest(RfxcomTestCase("test_0050_start_the_plugin", xpl_plugin, name, cfg))

    # do the specific plugin tests
    suite.addTest(RfxcomTestCase("test_0100_dummy", xpl_plugin, name, cfg))

    # do some tests comon to all the plugins
    suite.addTest(RfxcomTestCase("test_9900_hbeat", xpl_plugin, name, cfg))
    suite.addTest(RfxcomTestCase("test_9990_stop_the_plugin", xpl_plugin, name, cfg))

    # quit
    res = unittest.TextTestRunner().run(suite)
    xpl_plugin.force_leave()
    sys.exit(res.wasSuccessful())

