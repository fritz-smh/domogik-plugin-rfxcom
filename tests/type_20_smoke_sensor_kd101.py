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

from domogik_packages.plugin_rfxcom.conversion.from_normal_panic_to_DT_Switch import from_normal_panic_to_DT_Switch

class RfxcomTestCase(PluginTestCase):

    def test_0100_type20_smoke_sensor(self):
        """ check if all the xpl messages for a smoke sensor are sent
            Example : 
            Rfxcom trame : 200325b67e000650
            Sample messages : 
            xpl-trig : schema:x10.security, data:{'device': '0xb67e00', 'type': 'cn', 'command': 'panic'}
            xpl-trig : schema:x10.security, data:{'device': '0xb67e00', 'type': 'cn', 'command': 'normal'}

        """
        global devices
        address = "0xb67e00"
        device_id = devices[address]
        interval = 30

        print(u"Device address = {0}".format(address))
        print(u"Device id = {0}".format(device_id))
        print(u"Check that a message about alarm triger is sent.")
        
        self.assertTrue(self.wait_for_xpl(xpltype = "xpl-trig",
                                          xplschema = "x10.security",
                                          xplsource = "domogik-{0}.{1}".format(self.name, get_sanitized_hostname()),
                                          data = {"type" : "cn", 
                                                  "device" : address,
                                                  "command" : "panic"},
                                          timeout = interval))
        print(u"Check that the value of the xPL message has been inserted in database")
        sensor = TestSensor(device_id, "smoke")
        last_value = int(sensor.get_last_value()[1])
        self.assertTrue(last_value == from_normal_panic_to_DT_Switch(self.xpl_data.data['command']))

        # chekc the "normal" message when alarm is finished (manually handled by the plugin 2 seconds after the 
        # panic message
        print(u"Check that a message about end of alarm triger is sent.")
        
        self.assertTrue(self.wait_for_xpl(xpltype = "xpl-trig",
                                          xplschema = "x10.security",
                                          xplsource = "domogik-{0}.{1}".format(self.name, get_sanitized_hostname()),
                                          data = {"type" : "cn", 
                                                  "device" : address,
                                                  "command" : "normal"},
                                          timeout = interval))
        print(u"Check that the value of the xPL message has been inserted in database")
        sensor = TestSensor(device_id, "smoke")
        last_value = int(sensor.get_last_value()[1])
        self.assertTrue(last_value == from_normal_panic_to_DT_Switch(self.xpl_data.data['command']))




if __name__ == "__main__":

    test_folder = os.path.dirname(os.path.realpath(__file__))

    ### global variables
    # the key will be the device address
    devices = { "0xb67e00" : 0
              }

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
    cfg = { 'configured' : True,
            'device' : '/dev/rfxcom' }
    # specific configuration for test mdode (handled by the manager for plugin startup)
    cfg['test_mode'] = True 
    cfg['test_option'] = "{0}/type_20_data.json".format(test_folder)
   

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
    try:
        params = td.get_params(client_id, "rfxcom.smoke_sensor")
   
        for dev in devices:
            # fill in the params
            params["device_type"] = "rfxcom.smoke_sensor"
            params["name"] = "test_device_rfxcom_type20_{0}".format(dev)
            params["reference"] = "reference"
            params["description"] = "description"
            # global params
            pass # there are no global params for this plugin
            # xpl params
            for the_param in params['xpl']:
                if the_param['key'] == "device":
                    the_param['value'] = dev
            print params['xpl']
            # create
            device_id = td.create_device(params)['id']
            devices[dev] = device_id

    except:
        print(u"Error while creating the test devices : {0}".format(traceback.format_exc()))
        sys.exit(1)

    
    ### prepare and run the test suite
    suite = unittest.TestSuite()
    # check domogik is running, configure the plugin
    suite.addTest(RfxcomTestCase("test_0001_domogik_is_running", xpl_plugin, name, cfg))
    suite.addTest(RfxcomTestCase("test_0010_configure_the_plugin", xpl_plugin, name, cfg))
    
    # start the plugin
    suite.addTest(RfxcomTestCase("test_0050_start_the_plugin", xpl_plugin, name, cfg))

    # do the specific plugin tests
    suite.addTest(RfxcomTestCase("test_0100_type20_smoke_sensor", xpl_plugin, name, cfg))

    # do some tests comon to all the plugins
    #suite.addTest(RfxcomTestCase("test_9900_hbeat", xpl_plugin, name, cfg))
    suite.addTest(RfxcomTestCase("test_9990_stop_the_plugin", xpl_plugin, name, cfg))
    
    # quit
    res = unittest.TextTestRunner().run(suite)
    if res.wasSuccessful() == True:
        rc = 0   # tests are ok so the shell return code is 0
    else:
        rc = 1   # tests are ok so the shell return code is != 0
    xpl_plugin.force_leave(return_code = rc)


