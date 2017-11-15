"""
Author: Tiago Baptista
Purpose: Config builder class for SimpleProcUtil
"""


import os
import ConfigParser


class SimpleConfig(object):
    '''
    Defines the main config and sections explicitly
    '''

    def __init__(self):
        super(SimpleConfig, self).__init__()
        self.CONFIG_FILE = 'config.ini'

    @property
    def __CONFIG_FILE(self):
        return self.CONFIG_FILE


class SimpleConfigBuilder(SimpleConfig):

    def __init__(self):
        super(SimpleConfigBuilder, self).__init__()
        self.buildConfig()

    def buildConfig(self):
        self.config = ConfigParser.ConfigParser()

        if not os.path.isfile(self.CONFIG_FILE):
            raise Exception("No config.ini file found.")
        else:
            self.config.read(self.CONFIG_FILE)
