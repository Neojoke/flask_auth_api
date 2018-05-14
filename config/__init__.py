import settings


class GlobalSetting(object):
    def __init__(self, setting_module):
        for setting_key in dir(setting_module):
            setattr(self, setting_key, getattr(setting_module, setting_key))
        self.SETTINGS_MODULE = setting_module

    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            'cls': self.__class__.__name__,
            'settings_module': self.SETTINGS_MODULE,
        }

global_settings = GlobalSetting(settings)
