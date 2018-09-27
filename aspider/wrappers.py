#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from importlib import util
from aspider.utils import get_logger

logger = get_logger('settings')


class SettingsWrapper(object):

    def __init__(self, settings_name='settings.py'):
        self.my_settings = {}
        self.settings_name = settings_name
        self._load_settings()

    def __call__(self):
        return self.my_settings

    def settings(self):
        return self.my_settings

    def load_with_file(self, file_path):
        file_name = os.path.basename(file_path)
        if file_name[-3:] != '.py':
            logger.error('module must be a python file')

        module_spec = util.spec_from_file_location(
            file_name,
            file_path
        )

        if not module_spec:
            logger.error('Module path: {} not found Module{}'.format(file_name, file_path))
            return

        module = util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        load_settings = self._convert2dict(module)
        self.my_settings.update(load_settings)

    def load_with_dict(self, dict_params):
        self.my_settings.update(dict_params)

    def load_from_environment(self, prefix='AXPIDER_'):
        env_dict = {}
        for k, v in os.environ.items():
            if k.startswith(prefix):
                _, config_key = k.split(prefix, 1)
                try:
                    env_dict[config_key] = int(v)
                except ValueError:
                    try:
                        env_dict[config_key] = float(v)
                    except ValueError:
                        env_dict[config_key] = v
        self.my_settings.update(env_dict)

    def _load_settings(self):
        try:
            module = self._dynamic_import(self._closest_file(self.settings_name))
            self.my_settings = self._convert2dict(module)
        except ImportError:
            logger.error('No default setting found')

    def _dynamic_import(self, module_path):
        basename = os.path.basename(module_path)

        if basename[-1:] == '.py':
            basename = basename[:-3]

        module_spec = util.spec_from_file_location(
            basename, module_path
        )

        if not module_path:
            logger.error("Module path: {} not found Module:{}".format(module_path, basename))
            return

        module = util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module

    def _convert2dict(self, module):
        res = {}
        m = dir(module)
        for key in m:
            if key.startswith('__'):
                continue
            value = getattr(module, key)
            res[key] = value
        return res

    def _closest_file(self, file_name='settings.py', path='.', prev_path=None):
        if path == prev_path:
            return ''

        path = os.path.abspath(path)
        settings_file = os.path.join(path, file_name)
        if os.path.exists(settings_file):
            return settings_file
        return self._closest_file(file_name=file_name, path=os.path.dirname(path), prev_path=path)
