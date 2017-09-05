#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import lxml.html
import os
import re
import requests
import socket
import sys
import time
import traceback

BASE_URL = 'http://kifudepot.net/'
LIST_URL = 'http://kifudepot.net/index.php'

MAX_PAGE = 300

page = 1


def retrieve_sgf(content_url, sgf_name, save_dir, attempt):
    sgf_path = os.path.join(save_dir, sgf_name)
    if os.path.exists(sgf_path):
        print(u'SGF already exists: {:s}'.format(sgf_path))
    else:
        print(u'Downloading {:s}'.format(sgf_name))
    content = requests.get(content_url).content
    root = lxml.html.fromstring(content)
    sgf = root.cssselect('textarea#sgf')[0].text

    with open(sgf_path, 'w') as f:
        f.write(sgf.encode('utf8'))


def parse_list(page, save_dir, attempt):
    try:
        print("Fetch page (attempt={:d}): {:s} page={:d}".format(attempt, LIST_URL, page))
        content = requests.post(LIST_URL, data={'page': str(page)}).content
        root = lxml.html.fromstring(content)
        data_list = root.cssselect('table.dataTable tr')
        for rownum in range(1, len(data_list)):
            try:
                data = data_list[rownum]
                content_url = os.path.join(BASE_URL, data.cssselect('td.td_ev a')[0].attrib['href'])
                game_name = data.cssselect('td.td_ev a')[0].text
                black_name = data.cssselect('td.td_pb')[0].text
                white_name = data.cssselect('td.td_pw')[0].text
                game_date = data.cssselect('td.td_dt')[0].text
                sgf_name = '_'.join([game_name, black_name, white_name, game_date])
                sgf_name = re.sub(u'(　|\s)+', '_', sgf_name) + '.sgf'
                retrieve_sgf(content_url, sgf_name, save_dir, attempt=3)
            except KeyboardInterrupt:
                sys.exit()
            except:
                err, msg, _ = sys.exc_info()
                sys.stderr.write("{} {}\n".format(err, msg))
                sys.stderr.write(traceback.format_exc())
    except KeyboardInterrupt:
        sys.exit()
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        err, msg, _ = sys.exc_info()
        sys.stderr.write("{} {}\n".format(err, msg))
        sys.stderr.write(traceback.format_exc())
        if attempt > 0:
            time.sleep(10)
            attempt -= 1
            parse_list(page, attempt)


socket.setdefaulttimeout(180)

base = os.path.dirname(os.path.abspath(__file__))
save_dir = sys.argv[1]

try:
    while page < MAX_PAGE:
        parse_list(page, save_dir, attempt=3)
        page += 1
except SystemExit:
    pass
except:
    err, msg, _ = sys.exc_info()
    sys.stderr.write("{} {}\n".format(err, msg))
    sys.stderr.write(traceback.format_exc())
