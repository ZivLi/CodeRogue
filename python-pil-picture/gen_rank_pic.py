# coding: utf-8
import requests
from PIL import Image, ImageDraw, ImageFont
import datetime
import urllib2 as urllib
from cStringIO import StringIO
from main.aliyun.alioss import OSS


UPPER_NUM = u'十一二三四五六七八九'
CATEGORIES = ['all', 'kids', 'fashion', 'food', 'fun', 'tech', 'life']
RANK_URL = 'https://www.haipailink.com/api/projects/rank/all/{category}/{_date}/'
TITLE = u'第{}期 ({} - {})'
BASE_PATH = 'spider/static/'


def fetch_rank_data(category, _date):
    url = RANK_URL.format(category=category, _date=_date)
    response = requests.get(url)
    result = response.json()
    return result.get('rank_data') if category == 'all' else result.get('rank_data')[:10]


def extract_haipai_data(category, _dict):
    return [{
        'rank': dic.get('rank'),
        'name': dic.get('name'),
        'trend': dic.get('trend') if category == 'all' else dic.get('category_trend'),
        'score': dic.get('score'),
        'avatar': dic.get('avatar')
    } for dic in _dict]


def draw_pic(category, data, title):
    path = BASE_PATH + '/bd/{}.png'.format(category)
    fnt = ImageFont.truetype(BASE_PATH + 'PingFang.ttf', 35)
    title_fnt = ImageFont.truetype(BASE_PATH + 'PingFang.ttf', 32)
    base = Image.open(path).convert('RGBA')
    mask = Image.open(BASE_PATH + 'ell.png').convert('RGBA')
    up_arrow = Image.open(BASE_PATH + 's.png').convert('RGBA').resize((30, 40), Image.ANTIALIAS)
    down_arrow = Image.open(BASE_PATH + 'x.png').convert('RGBA').resize((30, 40), Image.ANTIALIAS)
    line = Image.open(BASE_PATH + 'heng.png').convert('RGBA').resize((30, 40), Image.ANTIALIAS)
    r, g, b, mask_alpha = mask.split()
    r, g, b, up_alpha = up_arrow.split()
    r, g, b, down_alpha = down_arrow.split()
    r, g, b, line_alpha = line.split()
    txt = Image.new('RGBA', base.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    name_x, name_y = 320, 1226
    for i, _data in enumerate(data):
        d.text((name_x, name_y + i * 131), _data.get('name'), font=fnt, fill='#676C75')
        d.text((name_x + 328, name_y + i *131), str(_data.get('score')), font=fnt, fill='#676C75')
        if _data.get('trend') == '0' or _data.get('trend') == '-':
            base.paste(line, (name_x + 480, name_y + 7 + i * 131), mask=line_alpha)
        elif _data.get('trend').startswith('-'):
            trend = _data.get('trend')[1:]
            d.text((name_x + 528, name_y + i * 131), str(trend), font=fnt, fill='#676C75')
            base.paste(down_arrow, (name_x + 480, name_y + 7 + i * 131), mask=down_alpha)
        else:
            d.text((name_x + 528, name_y + i * 131), str(_data.get('trend')), font=fnt, fill='#676C75')
            base.paste(up_arrow, (name_x + 480, name_y + 7 + i * 131), mask=up_alpha)
        avatar_pic = circle_new(_data.get('avatar'))
        base.paste(avatar_pic, (name_x - 97, name_y - 15 + i * 131))
        base.paste(mask, (name_x - 97, name_y - 15 + i * 131), mask=mask_alpha)  # You can work around this by using the same image as both source image and mask.
    d.text((250, 635), title, font=title_fnt)
    pic = Image.alpha_composite(base, txt)
    pic.show()
    return pic


def circle_new(pic_path):
    r = 81
    img_file = urllib.urlopen(pic_path)
    im = StringIO(img_file.read())
    img = Image.open(im)
    img = img.resize((r, r), Image.ANTIALIAS)
    circle = Image.new('L', (r, r), 0)
    _draw = ImageDraw.Draw(circle)
    _draw.ellipse((0, 0, r, r), fill='#ffffff')
    alpha = Image.new('L', (r, r), 255)
    alpha.paste(circle, (0, 0))
    img.putalpha(alpha)
    return img


def get_date_and_title_format():
    now = datetime.datetime.now()
    start = (now - datetime.timedelta(now.weekday() +  7)).strftime('%Y/%m/%d')
    end = (now - datetime.timedelta(now.weekday() +  1)).strftime('%Y/%m/%d')
    week_n = now.isocalendar()[1]
    return (str(now.year) + str(week_n - 1),
        TITLE.format(convert_upper_number(week_n - 33), start, end))


def convert_upper_number(n):
    if n == 10:
        return UPPER_NUM[0]
    elif n < 10:
        return UPPER_NUM[n]
    else:
        ten_digit, unit_n = n / 10, n % 10
        return UPPER_NUM[ten_digit] + '十' + UPPER_NUM[unit_n]


def main():
    _date, title = get_date_and_title_format()
    for c in CATEGORIES:
        total_data = fetch_rank_data(c, _date)
        image = draw_pic(c, extract_haipai_data(c, total_data), title)
        key = 'rank_{}_{}.png'.format(_date, c)
        oss = OSS()
        output = StringIO()
        image.save(output, 'png')
        output.seek(0)
        res = oss.upload_to_oss(key, output)
        return res


if __name__ == '__main__':
    main()
