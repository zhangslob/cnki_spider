#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from selenium import webdriver

driver = webdriver.Chrome()
driver.maximize_window()


def login(account, password):
    driver.get('https://github.com/login')
    time.sleep(2)
    driver.find_element_by_id('login_field').send_keys(account)
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_xpath('//input[@class="btn btn-primary btn-block"]').click()
    # do whatever you want


if __name__ == '__main__':
    account, password = 'account', 'password'
    login(account, password)
