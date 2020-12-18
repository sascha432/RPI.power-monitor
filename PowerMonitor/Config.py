#
# Author: sascha_lammers@gmx.de
#

from Config import (Loader, Merger, DictType, RangeType, Param, JsonReader)
from os import path
from PowerMonitor import AppConfig

class Config:

    def __init__(self, config_dir):
        self._config_dir = path.realpath(config_dir)
        if not path.exists(self._config_dir) or not path.isdir(self._config_dir):
            raise IOError('No such file or directory: %s' % (self._config_dir))

    def get_filename(self, file):
        return path.realpath(path.join(self._config_dir, file.format(config_dir=self._config_dir)))

    def load(self, file):

        loader = Loader('app', AppConfig.App(DictType({
            'channels': AppConfig.ChannelList(RangeType(range(0, 3), AppConfig.Channel, DictType({
                'name': Param(lambda path: ('Channel %u' % (path.index + 1))),
                'calibration': AppConfig.Calibration()
            }))),
            'plot': AppConfig.Plot(DictType({
                'compression': AppConfig.PlotCompression()
            })),
            'gui': AppConfig.Gui(),
            'mqtt': AppConfig.Mqtt(),
            'backlight': AppConfig.Backlight()
        })))

        reader = JsonReader(loader.root, False)
        config = reader.loads_from(file)
        merger = Merger(loader.root)
        merger.merge(config)

        return loader.root_object
