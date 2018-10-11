def draw_pic(category, data, title):
    path = BASE_PATH + 'bd/{}.png'.format(category)
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