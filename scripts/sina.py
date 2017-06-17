#!/usr/bin/env python

import os
import urllib
import re
import requests
import socket
import sys
import time
import traceback

socket.setdefaulttimeout(180)

base = os.path.dirname(os.path.abspath(__file__))
save_dir = './sina'


def request_page(sgflist_url):
    sgflist_content = requests.get(sgflist_url, timeout=180).content
    sgfurls = set(re.findall(r"JavaScript:gibo_load\('(http://.+.sgf)'\)", sgflist_content))
    for url in sgfurls:
        try:
            save_path = os.path.join(base, save_dir, os.path.basename(url).decode('gb2312'))
            if not os.path.exists(save_path):
                print("Downloading {:s}".format(url))
                urllib.urlretrieve(url, save_path)
                time.sleep(1.)
            else:
                print("SGF already exists: {:s}".format(save_path))
        except KeyboardInterrupt:
            break
        except IOError:
            print("IOError {:s}".format(url))
            print("Wait seconds then retring {:s}".format(url))
            time.sleep(10)
            urllib.urlretrieve(url, save_path)
        except:
            err, msg, _ = sys.exc_info()
            sys.stderr.write("{} {}\n".format(err, msg))
            sys.stderr.write(traceback.format_exc())


def attempt_page(sgflist_url, attempt):
    try:
        print("Fetch page (attempt={:d}): {:s}".format(attempt, sgflist_url))
        request_page(url)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        err, msg, _ = sys.exc_info()
        sys.stderr.write("{} {}\n".format(err, msg))
        sys.stderr.write(traceback.format_exc())
        if attempt > 0:
            time.sleep(10)
            attempt -= 1
            attempt_page(sgflist_url, attempt)


page_no = 0

while True:
    try:
        while page_no <= 751:
            url = 'http://duiyi.sina.com.cn/qipu/new_gibo.asp?cur_page=' + str(page_no)
            page_no += 1
            attempt_page(url, attempt=3)
        sys.exit()
    except SystemExit, KeyboardInterrupt:
        break
    except:
        err, msg, _ = sys.exc_info()
        sys.stderr.write("{} {}\n".format(err, msg))
        sys.stderr.write(traceback.format_exc())

