#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

import lxml.html
import os
import urllib
import requests
import socket
import sys
import time
import traceback

LIST_URL = 'http://gokifu.com/index.php?p={:d}'

MAX_PAGE = 2000

page = 1


def parse_list(page, save_dir, attempt):
    try:
        url = LIST_URL.format(page)
        print("Fetch page (attempt={:d}): {:s}".format(attempt, url))
        content = requests.get(url).content
        root = lxml.html.fromstring(content)
        data_list = root.cssselect('div#gamelist div.game_type a:nth-child(2)')
        for rownum in range(1, len(data_list)):
            try:
                data = data_list[rownum]
                download_url = data.attrib['href']
                save_path = os.path.join(save_dir, os.path.basename(download_url))
                if not os.path.exists(save_path):
                    print("Downloading {:s}".format(download_url))
                    urllib.urlretrieve(download_url, save_path)
                else:
                    print("SGF already exists: {:s}".format(save_path))
            except KeyboardInterrupt:
                sys.exit()
            except IOError:
                print("IOError {:s}".format(download_url))
                print("Wait seconds then retring {:s}".format(download_url))
                time.sleep(10)
                urllib.urlretrieve(download_url, save_path)
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
