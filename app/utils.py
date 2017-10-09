# -*- coding: utf-8 -*-

import math

# 生成分布的页码
def paginate(page, per_page, total):
    pagination = {'page':page}
    tmp_pages = range(1, int(math.ceil(total/float(per_page)))+1)
    idx = tmp_pages.index(page)
    if len(tmp_pages) <= 10:
        pagination['pages'] = tmp_pages
    else:
        if idx - 5 >= 0:
            start = idx-5
        else:
            start = 0
        if idx + 5 <= len(tmp_pages):
            end = idx + 5
        else:
            end = len(tmp_pages)
        pagination['pages'] = tmp_pages[start:end+1]

    if idx != 0:
        pagination['prev'] = tmp_pages[idx-1]
    else:
        pagination['prev'] = None
    if idx != len(tmp_pages) -1:
        pagination['next'] = tmp_pages[idx+1]
    else:
        pagination['next'] = None
    return pagination
