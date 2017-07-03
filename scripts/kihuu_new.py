#!/usr/bin/env python

import lxml.html
import os
import urllib
import sys
import time
import traceback

site_root = "http://www.kihuu.net"

save_dir = sys.argv[1]

page_id = 1
while True:
    try:
        newlist_url = 'http://www.kihuu.net/index.php?pageID={:s}'.format(str(page_id))
        print("Fetch page {:d}: {:s}".format(page_id, newlist_url))
        newlist_root = lxml.html.parse(newlist_url).getroot()
        sgf_links = newlist_root.cssselect('table.index_table a[href$=".sgf"]')
        if sgf_links and page_id <= 50:
            page_id += 1
            for each_link in sgf_links:
                sgf_url = site_root + each_link.get('href')
                save_path = os.path.join(save_dir, os.path.basename(sgf_url)) 
                try:
                    game_name = each_link.getparent().getchildren()[0].text
                except:
                    game_name = 'Unknown' 
                if not os.path.exists(save_path):
                    print(u"Downloading {:s} ({:s})".format(game_name, sgf_url))
                    urllib.urlretrieve(sgf_url, save_path)
                    time.sleep(.5)
        else:
            break
    except KeyboardInterrupt:
        break
