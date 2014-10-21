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

    def test_0100_type50_temperature_sensor(self):
        """ check if all the xpl messages for a temperature sensor are sent
            Example : 
            Rfxcom trame : 500110000180BC69
            Sample messages : 
 
            xpl-trig : schema:sensor.basic, data:{'device': 'temp1 0x0001', 'current': 21.2, 'units': 'c', 'type': 'temp'}
            xpl-trig : schema:sensor.basic, data:{'device': 'temp1 0x0001', 'current': 10, 'type': 'battery'}
            xpl-trig : schema:sensor.basic, data:{'device': 'temp1 0x0001', 'current': 31, 'type': 'rssi'}

            Notice that for this test, the same message will be received from the fake rfxcom device 5 times! 
        """
        #global address
        #global device_id
        global devices

        # set interval betwwen each message
        interval = 30  # seconds

        # set constants for values in xpl messages
        # temp1 0x0001 : 500110000180BC69
        # temp1 0xFB01 : 50021DFB0100D770
        tests = [ {
                     'address' : "temp1 0x0001",
                     'temperature' : -18.8,
                     'battery' : 100,
                     'rssi' : 37
                  },
                  {
                     'address' : "temp2 0xfb01",
                     'temperature' : 21.5,
                     'battery' : 10,
                     'rssi' : 43
                  }]

        for test in tests:
            self.test_feature(test['address'], 
                              devices[test['address']], 
                              interval, 
                              test['temperature'], 
                              test['battery'], 
                              test['rssi'])

    def test_feature(self, address, device_id, interval, temperature, battery, rssi):
        """ Do the tests 
            @param address : device address
            @param device_id : device id
            @param interval : timeout (max time before we assume the message is not sent)
            @param temperature
            @param battery
            @param rssi
        """

        # test temperature
        print(u"Device address = {0}".format(address))
        print(u"Device id = {0}".format(device_id))
        print(u"Check that a message about temperature is sent.")
        
        self.assertTrue(self.wait_for_xpl(xpltype = "xpl-trig",
                                          xplschema = "sensor.basic",
                                          xplsource = "domogik-{0}.{1}".format(self.name, get_sanitized_hostname()),
                                          data = {"type" : "temp", 
                                                  "device" : address,
                                                  "current" : temperature},
                                          timeout = interval))
        print(u"Check that the value of the xPL message has been inserted in database")
        sensor = TestSensor(device_id, "temperature")
        self.assertTrue(sensor.get_last_value()[1] == self.xpl_data.data['current'])

        # test battery
        print(u"Check that a message about battery is sent.")
        
        self.assertTrue(self.wait_for_xpl(xpltype = "xpl-trig",
                                          xplschema = "sensor.basic",
                                          xplsource = "domogik-{0}.{1}".format(self.name, get_sanitized_hostname()),
                                          data = {"type" : "battery", 
                                                  "device" : address,
                                                  "current" : battery},
                                          timeout = interval))
        print(u"Check that the value of the xPL message has been inserted in database")
        sensor = TestSensor(device_id, "battery")
        self.assertTrue(sensor.get_last_value()[1] == self.xpl_data.data['current'])

        # test rssi
        print(u"Check that a message about rssi is sent.")
        
        self.assertTrue(self.wait_for_xpl(xpltype = "xpl-trig",
                                          xplschema = "sensor.basic",
                                          xplsource = "domogik-{0}.{1}".format(self.name, get_sanitized_hostname()),
                                          data = {"type" : "rssi", 
                                                  "device" : address,
                                                  "current" : rssi},
                                          timeout = interval))
        print(u"Check that the value of the xPL message has been inserted in database")
        sensor = TestSensor(device_id, "rssi")
        self.assertTrue(sensor.get_last_value()[1] == self.xpl_data.data['current'])




if __name__ == "__main__":

    test_folder = os.path.dirname(os.path.realpath(__file__))

    ### global variables
    # the key will be the device address
    devices = { "temp1 0x0001" : 0,
                "temp2 0xfb01" : 0
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
    cfg['test_option'] = "{0}/type_50_data.json".format(test_folder)
   

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
        params = td.get_params(client_id, "rfxcom.temperature_humidity")
   
        for dev in devices:
            # fill in the params
            params["device_type"] = "rfxcom.temperature_humidity"
            params["name"] = "test_device_rfxcom_type52_{0}".format(dev)
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
    suite.addTest(RfxcomTestCase("test_0100_type50_temperature_sensor", xpl_plugin, name, cfg))

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


