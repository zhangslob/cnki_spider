#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree


class BaseField(object):

    def __init__(self, css_select=None, xpath_select=None, default=None):
        self.css_select = css_select
        self.xpath_select = xpath_select
        self.default = default


class TextField(BaseField):

    def __init__(self, css_select=None, xpath_select=None, default=None):
        super(TextField, self).__init__(css_select, xpath_select, default)

    def extract_value(self, html, is_source=False):
        if self.css_select:
            value = html.cssselect(self.css_select)
        elif self.xpath_select:
            value = html.xpath(self.xpath_select)
        else:
            raise ValueError('{} field: css_select or xpath_select is expected'.format(self.__class__.__name))

        if is_source:
            return value

        if isinstance(value, list) and len(value) == 1:
            text = ''
            if isinstance(value[0], etree._Element):
                for node in value[0].itertext():
                    text += node.strip()
                value = text

            if self.default:
                value = value if value else self.default

            return value


class AttrField(BaseField):

    def __init__(self, attr, css_select=None, xpath_select=None, default=None):
        super(AttrField, self).__init__(css_select, xpath_select, default)
        self.attr = attr

    def extract_value(self, html, is_source=False):
        if self.css_select:
            value = html.cssselect(self.css_select)
            value = value[0].get(self.attr, value) if len(value) == 1 else value
        elif self.xpath_select:
            value = html.xpath(self.xpath_select)
        else:
            raise ValueError('%s field: css_select or xpath_select is expected' % self.__class__.__name__)
        if is_source:
            return value
        if self.default is not None:
            value = value if value else self.default
        return value


