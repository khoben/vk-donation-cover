#coding: utf-8

import re
import time
from datetime import datetime
from io import BytesIO
from urllib import parse

import pytz
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from config import *
from obscene_words_filter.default import get_default_filter

# id last donation
idLastDonation = -1
# swear word filter
wordFilter = get_default_filter()


def upload_cover(image, access_token, group_id, width=ORIGINAL_COVER_WIDTH, height=ORIGINAL_COVER_HEIGHT):
    """
    Upload cover and set it
    """

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
        "v": 5.67
    })
    upload_result = requests.get(set_cover_url).content
    return upload_result


def ReduceOpacity(im, opacity):
    """
    Returns an image with reduced opacity.
    Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/362879
    """

    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im


def wrap(text, width):
    """
    Wrap one-line string
    """

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


def add_corners(im, rad):
    """
    Make rounded corner
    """

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

    _, _, _, opacity = TEXT_COLOR_BACKGROUND

    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity / 255)
    im.putalpha(alpha)

    return im


def draw_outline(draw, x, y, finalText, shadow_color, fnt, align, spacing):
    """
    draw outline
    """

    draw.multiline_text((x - 1, y),
                        finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing)

    draw.multiline_text((x + 1, y),
                        finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing)

    draw.multiline_text((x, y - 1),
                        finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing)

    draw.multiline_text((x, y + 1),
                        finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing)

    draw.multiline_text((x - 1, y - 1),
                        finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing)

    draw.multiline_text((x + 1, y - 1),
                        finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing)

    draw.multiline_text((x - 1, y + 1),
                        finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing)

    draw.multiline_text((x + 1, y + 1),
                        finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing)


def draw_basic(text, width=1, height=1, font_size=FONT_SIZE, font_outline=False, align="center", spacing=int(FONT_SIZE/4)):
    """
    Draw info on sample image
    """

    shadow_color = TEXT_COLOR_OUTLINE
    color = TEXT_COLOR

    original = Image.open(ORIGINAL_COVER_PATH)
    im = Image.new('RGBA', (width, height), TEXT_COLOR_BACKGROUND)
    draw = ImageDraw.Draw(im)

    fnt = ImageFont.truetype(FONT_PATH, font_size)
    finalText = ''

    for i in text:
        # i[0] -- name
        # i[1] -- sum
        # i[2] -- comment
        comment = wrap(i[2], MAX_LEN_STRING_COMMENT_BY_LINE)
        finalText += '{name} — {sum}RUB\n{comment}\n\n'.format(
            name=i[0], sum=i[1], comment=comment)

    # cut last new lines
    finalText = finalText[:-2]
    linesInFinalText = len(finalText.split('\n')) - 1

    w, h = draw.textsize(finalText, font=fnt)
    im = Image.new('RGBA', (w + ROUNDING_RADIUS + 5, h +
                            ROUNDING_RADIUS + spacing * linesInFinalText + 5), TEXT_COLOR_BACKGROUND)

    im = add_corners(im, ROUNDING_RADIUS)
    draw = ImageDraw.Draw(im, mode='RGBA')
    x, y = (ROUNDING_RADIUS + 5) / 2, (ROUNDING_RADIUS + 5) / 2

    # draw outline

    if font_outline:
        draw_outline(draw, x, y, finalText, shadow_color, fnt, align, spacing)

    # draw text
    draw.multiline_text((x, y),
                        finalText, fill=color, font=fnt, align=align, spacing=spacing)

    # paste donate info on origianl image
    original.paste(im, (original.width - w - 430,
                        original.height - h - 55 - spacing * linesInFinalText), im)

    stream = BytesIO()
    original.save(stream, format='png')
    stream.seek(0)
    img = stream.read()
    return img


def getDeltaTime(time):
    """
    Calc delta between now and last donation time
    """

    dateTimeformat = '%Y-%m-%d %H:%M:%S.%f'
    convertedTime = datetime.strptime(time, dateTimeformat)
    timezone = pytz.timezone('Europe/Moscow')
    timeNow = str(datetime.now(timezone))
    timeNow = timeNow.split('+')[0]
    timeNow = datetime.strptime(timeNow, dateTimeformat)
    delta = (timeNow - convertedTime).total_seconds()
    return delta


def filterBadWords(message):
    """
    Filter swears
    """

    return wordFilter.mask_bad_words(message)


def checkDonations():
    """
    Check new donation and render it
    """

    global idLastDonation
    needUpdate = False
    r = requests.get(BASE_URL.format(token=TOKEN_DONATIONPAY,
                                     limit=LIMIT_DONATIONS_TO_SHOW, status=DONATION_STATUS))
    try:
        donations = r.json()['data']
    except Exception as e:
        print('Bad answer from server: {}'.format(str(e)))
    else:
        # if last is none then set it
        if idLastDonation == -1:
            idLastDonation = donations[0]['id']
            needUpdate = True
        else:
            # comparing last getted and new getted donation
            if idLastDonation != donations[0]['id']:
                needUpdate = True
                idLastDonation = donations[0]['id']

        if needUpdate:
            print('UPDATE!')
            print(donations)
            outForImage = []

            for i in donations:
                message = i['comment'].replace('Комментарий: ', '')[
                    :MAX_LEN_STRING_COMMENT]
                message = filterBadWords(message)
                outForImage.append(['{name}'.format(name=i['what'][:MAX_LEN_STRING_NAME]),
                                    '{sum}'.format(sum=i['sum']),
                                    '{comment}'.format(comment=message)])
            try:
                upload_cover(draw_basic(outForImage),
                             access_token=TOKEN_VK, group_id=GROUP_ID)
            except Exception as e:
                print('Error: Cant upload cover: {}'.format(str(e)))
        else:
            print('Won`t change cover')
            print(donations)
