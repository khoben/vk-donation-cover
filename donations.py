#coding: utf-8

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from urllib import parse
from datetime import datetime

#countains all configurable constants
from config import *

import requests
import pytz
import re
import time


# Upload cover and set it
def upload_cover(image, access_token, group_id, width=ORIGINAL_COVER_WIDTH, height=ORIGINAL_COVER_HEIGHT):
    crop_url = 'https://api.vk.com/method/photos.getOwnerCoverPhotoUploadServer?' + parse.urlencode({
        "group_id": group_id,
        "crop_x": 0,
        "crop_y": 0,
        "crop_x2": width,
        "crop_y2": height,
        "access_token": access_token,
        "v": 5.67
    })
    upload_url = requests.get(crop_url).json()
    upload_url = upload_url["response"]["upload_url"]
    uploaded_data = requests.post(upload_url, files={"photo": image}).json()
    set_cover_url = 'https://api.vk.com/method/photos.saveOwnerCoverPhoto?' + parse.urlencode({
        "photo": uploaded_data["photo"],
        "hash": uploaded_data["hash"],
        "access_token": access_token,
        "v": "5.63"
    })
    upload_result = requests.get(set_cover_url).content
    return upload_result

# Wrap one-line string
def wrap(text, width):
    lines = []
    for paragraph in text.split('\n'):
        line = []
        len_line = 0
        for word in paragraph.split(' '):
            len_word = len(word)
            if len_word > MAX_WORD_LEN:
                word = word[:MAX_WORD_LEN] + '...'
                len_word = len(word)
            if len_line + len_word <= width:
                line.append(word)
                len_line += len_word + 1
            else:
                if len(line) > 0:
                    lines.append(' '.join(line))
                line = [word]
                len_line = len_word + 1
        lines.append(' '.join(line))
    lines = lines[:MAX_LINES_COMMENT]
    return '\n'.join(lines)

# Make rounded background
def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

# Draw info on sample image
def draw_basic(text, width=1, height=1, font_size=FONT_SIZE, align="center"):

    shadow_color = TEXT_COLOR_OUTLINE
    color = TEXT_COLOR

    original = Image.open(ORIGINAL_COVER_PATH)
    im = Image.new("RGBA", (width, height), TEXT_COLOR_BACKGROUND)
    draw = ImageDraw.Draw(im)

    fnt = ImageFont.truetype(FONT_PATH, font_size)
    finalText = ''

    for i in text:
        comment = wrap(i[2], MAX_LEN_STRING_COMMENT_BY_LINE)
        finalText += '{name} — {sum}RUB\n{comment}\n\n'.format(
            name=i[0], sum=i[1], comment=comment)

    # cut last new lines
    finalText = finalText[:-2]

    w, h = draw.textsize(finalText, font=fnt)
    im = Image.new("RGBA", (w + ROUNDING_RADIUS + 5, h + ROUNDING_RADIUS + 5), TEXT_COLOR_BACKGROUND)
    
    im = add_corners(im, ROUNDING_RADIUS)
    draw = ImageDraw.Draw(im)
    x, y = ( ROUNDING_RADIUS + 5 ) / 2, ( ROUNDING_RADIUS + 5 ) / 2

    # draw outline
    draw.multiline_text((x - 1, y),
                        finalText, fill=shadow_color, font=fnt, align=align)

    draw.multiline_text((x + 1, y),
                        finalText, fill=shadow_color, font=fnt, align=align)

    draw.multiline_text((x, y - 1),
                        finalText, fill=shadow_color, font=fnt, align=align)

    draw.multiline_text((x, y + 1),
                        finalText, fill=shadow_color, font=fnt, align=align)

    draw.multiline_text((x - 1, y - 1),
                        finalText, fill=shadow_color, font=fnt, align=align)

    draw.multiline_text((x + 1, y - 1),
                        finalText, fill=shadow_color, font=fnt, align=align)

    draw.multiline_text((x - 1, y + 1),
                        finalText, fill=shadow_color, font=fnt, align=align)

    draw.multiline_text((x + 1, y + 1),
                        finalText, fill=shadow_color, font=fnt, align=align)
    # draw text
    draw.multiline_text((x, y),
                        finalText, fill=color, font=fnt, align=align)

    # paste donate info on origianl image
    original.paste(im, (original.width - w - 430,
                        original.height - h - 55), im)
    
    stream = BytesIO()
    original.save(stream, format='png')
    stream.seek(0)
    img = stream.read()
    return img

#delta between now and last donation time
def getDeltaTime(time):
    dateTimeformat = '%Y-%m-%d %H:%M:%S.%f'
    convertedTime = datetime.strptime(time, dateTimeformat)
    timezone = pytz.timezone('Europe/Moscow')
    timeNow = str(datetime.now(timezone))
    timeNow = timeNow.split('+')[0]
    timeNow = datetime.strptime(timeNow, dateTimeformat)
    delta = (timeNow - convertedTime).total_seconds()
    return delta


def checkDonations(lastDonation):
    needUpdate = False
    r = requests.get(BASE_URL.format(token=TOKEN_DONATIONPAY,
                                     limit=LIMIT_DONATIONS_TO_SHOW, status=DONATION_STATUS))
    try:
        donations = r.json()['data']
    except Exception as e:
        print(e)
    else:
        # if last is none then set it
        if not lastDonation:
            lastDonation.update(donations[0])
            needUpdate = True
        else:
            # comparing last getted and new getted donation 
            if lastDonation != donations[0]:
                needUpdate = True
                lastDonation.clear()
                lastDonation = dict(donations[0])

        if needUpdate:
            print('UPDATE!')
            print(donations)
            outForImage = []

            for i in donations:
                outForImage.append(['{name}'.format(name=i['what'][:MAX_LEN_STRING_NAME]),
                                    '{sum}'.format(sum=i['sum']),
                                    '{comment}'.format(comment=i['comment'].replace('Комментарий: ', '')[:MAX_LEN_STRING_COMMENT])])
            try:
                upload_cover(draw_basic(outForImage),
                            access_token=TOKEN_VK, group_id=GROUP_ID)
            except Exception as e:
                print('cant upload cover coz {}'.format(e))
        else:
            print('wont change cover')
            print(donations)