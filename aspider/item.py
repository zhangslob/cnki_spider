#!/usr/bin/env python
# -*- coding: utf-8 -*-

from inspect import iscoroutinefunction

from lxml import etree

from aspider.field import BaseField
from aspider.request import Request


class ItemMeta(type):

    def __new__(cls, name, bases, attrs):
        __fields = dict(
            {(field_name, attrs.pop(field_name)) for field_name, object in
             list(attrs.items()) if isinstance(object, BaseField)}
        )
        attrs['__fields'] = __fields
        new_class = type.__new__(cls, name, bases, attrs)
        return new_class


class Item(metaclass=ItemMeta):

    def __init__(self):
        self.results = dict()

    @classmethod
    async def _get_html(cls, html, url, *args, **kwargs):
        if not html and not url:
            raise ValueError("html(url or html_tree) is expected")
        if not html:
            request = Request(url, **kwargs)
            response = await request.fetch()
            html = response.html
        return etree.HTML(html)

    @classmethod
    async def get_item(cls, *, html: str='', url: str='', html_etree: etree._Element=None, **kwargs) -> list:
        if not html_etree:
            etree_result = await cls._get_html(html, url, **kwargs)
        else:
            etree_result = html_etree

        items_field = getattr(cls, '__fields', {}).get('target_item', None)
        if items_field:
            items = items_field.extract_value(etree_result, True)
            if items:
                tasks = [cls._parse_html(etree_result=i) for i in items]
                all_item = []
                for task in tasks:
                    all_item.append(await task)
                return all_item

            else:
                raise ValueError("Get target_item's value Error")

        else:
            raise ValueError("target_item is expected")

    @classmethod
    async def _parse_html(cls, etree_result: etree._Element) -> object:
        if not etree_result or not isinstance(etree_result, etree._Element):
            raise ValueError("etree._Element is expected")

        item_ins = dict()
        for field_name, field_value in getattr(item_ins, '__fields', {}).items():
            if not field_name.startwith('target_'):
                clean_method = getattr(item_ins, 'clean_{}'.format(field_name), None)
                value = field_value.extract_value(etree_result) if isinstance(field_value, BaseField) \
                    else field_value

                if clean_method:
                    if iscoroutinefunction(clean_method):
                        value = await clean_method(value)
                    else:
                        value = clean_method(value)
                setattr(item_ins, field_name, value)
                item_ins.results[field_name] = value
            return item_ins

    def __str__(self):
        return f"<Item {self.results}>"




