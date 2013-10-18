#!/usr/bin/python
# -*- coding: utf-8 -*-


from domogik.tests.common.testdevice import TestDevice
from domogik.common.utils import get_sanitized_hostname


if __name__ == "__main__":

    td = TestDevice()
    td.create_device("plugin", "rfxcom", get_sanitized_hostname(), "test_device_rfxcom", "rfxcom.temperature_humidity")
    td.configure_global_parameters({"address" : "th1 0x2504"})

