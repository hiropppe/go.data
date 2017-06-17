#!/usr/bin/env python

import lxml.html
import os
import urllib
import sys
import time
import traceback

site_root = "http://www.kihuu.net"

base = os.path.dirname(os.path.abspath(__file__))
save_dir = 'kihuu'

prolist_root = lxml.html.parse('http://www.kihuu.net/html/prolist.htm').getroot()
for pro_a in prolist_root.cssselect('table.prolist a'):
    print("==> " + pro_a.text)
    try:
        page_no = 1
        while True:
            sgflist_url = site_root + pro_a.get('href') + '&pageID=' + str(page_no)
            print("Fetch page {:d}: {:s}".format(page_no, sgflist_url))
            sgflist_root = lxml.html.parse(sgflist_url).getroot()
            sgfurls = [site_root + sgf_a.get('href') for sgf_a in sgflist_root.cssselect('table.index_table a') if sgf_a.get('href').endswith('.sgf')]
            if sgfurls and page_no <= 50:
                page_no += 1
                for url in sgfurls:
                    save_path = os.path.join(base, save_dir, os.path.basename(url))
                    if not os.path.exists(save_path):
                        print("Downloading {:s}".format(url))
                        urllib.urlretrieve(url, save_path)
                        time.sleep(.5)
            else:
                break
    except KeyboardInterrupt:
        break
    except:
        err, msg, _ = sys.exc_info()
        sys.stderr.write("{} {}\n".format(err, msg))
        sys.stderr.write(traceback.format_exc())
