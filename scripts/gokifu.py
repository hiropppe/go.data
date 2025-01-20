#!/usr/bin/env python3

import lxml.html
import os
import urllib.request
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
        print(f"Fetch page: {url}")
        content = requests.get(url).content
        root = lxml.html.fromstring(content)
        data_list = root.cssselect('div#gamelist div.game_type a:nth-child(2)')
        for rownum in range(1, len(data_list)):
            try:
                data = data_list[rownum]
                download_url = data.attrib['href']
                save_path = os.path.join(save_dir, os.path.basename(download_url))
                if not os.path.exists(save_path):
                    print(f"Downloading {download_url}")
                    sgfdata = urllib.request.urlopen(download_url).read()
                    with open(save_path, mode="w") as w:
                        print(sgfdata, file=w)
                else:
                    print(f"SGF already exists: {save_path}")
            except KeyboardInterrupt:
                sys.exit()
            except IOError:
                print("IOError {:s}".format(download_url))
                print("Wait seconds then retring {download_url}")
                time.sleep(10)
                sgfdata = urllib.request.urlopen(download_url).read()
                with open(save_path, mode="w") as w:
                    print(sgfdata, file=w)
            except Exception as e:
                print(type(e).__name__, str(e), file=sys.stderr)
    except KeyboardInterrupt:
        sys.exit()
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
        print(type(e).__name__, str(e), file=sys.stderr)
        if attempt > 0:
            time.sleep(10)
            attempt -= 1
            parse_list(page, attempt)


socket.setdefaulttimeout(180)

save_dir = sys.argv[1]

try:
    while page < MAX_PAGE:
        parse_list(page, save_dir, attempt=3)
        page += 1
except SystemExit:
    pass
except Exception as e:
    print(type(e).__name__, str(e), file=sys.stderr)
