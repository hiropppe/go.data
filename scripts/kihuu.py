#!/usr/bin/env python

import lxml.html
import os
import urllib.request
import re
import sys
import time
import traceback

site_root = "http://www.kihuu.net"

save_dir = sys.argv[1]

prolist_root = lxml.html.parse('http://www.kihuu.net/html/prolist.htm').getroot()
for pro_a in prolist_root.cssselect('table.prolist a'):
    print(f"==> {pro_a.text}")
    try:
        page_no = 1
        while True:
            sgflist_url = site_root + pro_a.get("href") + "&pageID=" + str(page_no)
            print(f"Fetch page {page_no}: {sgflist_url}")
            prodir = re.findall(r"key=([^&]+)", sgflist_url)[0]
            os.makedirs(os.path.join(save_dir, prodir), exist_ok=True)
            sgflist_root = lxml.html.parse(sgflist_url).getroot()
            sgfurls = [site_root + sgf_a.get('href') for sgf_a in sgflist_root.cssselect('table.index_table a') if sgf_a.get('href').endswith('.sgf')]
            if sgfurls:
                for url in sgfurls:
                    save_path = os.path.join(save_dir, prodir, os.path.basename(url))
                    if not os.path.exists(save_path):
                        print(f"Downloading {url}")
                        sgfdata = urllib.request.urlopen(url).read()
                        with open(save_path, mode="w") as w:
                            print(sgfdata, file=w)
                        time.sleep(.5)
            else:
                break
            page_no += 1
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(type(e).__name__, str(e), file=sys.stderr)
