#!/usr/bin/python

from domogik.tests.common.helpers import configure, delete_configuration
from domogik.common.utils import get_sanitized_hostname


delete_configuration("plugin", "rfxcom", get_sanitized_hostname())
configure("plugin", "rfxcom", get_sanitized_hostname(), "configured", True)
configure("plugin", "rfxcom", get_sanitized_hostname(), "rfxcom_device", "/dev/rfxcom")
