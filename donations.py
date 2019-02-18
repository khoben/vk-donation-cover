# coding: utf-8

import re
import time
from datetime import datetime
from io import BytesIO
from urllib import parse

import pytz
import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

import cfscrape
from config import *
from obscene_words_filter.default import get_default_filter

import html.parser as htmlparser

# id last donation
idLastDonation = -1
# swear word filter
wordFilter = get_default_filter()
# parse html codes to normal characters
parser = htmlparser.HTMLParser()



def upload_cover(
    image,
    access_token,
    group_id,
    width,
    height,
):
    """
    Upload cover and set it
    """

    crop_url = (
        "https://api.vk.com/method/photos.getOwnerCoverPhotoUploadServer?"
        + parse.urlencode(
            {
                "group_id": group_id,
                "crop_x": 0,
                "crop_y": 0,
                "crop_x2": width,
                "crop_y2": height,
                "access_token": access_token,
                "v": 5.67,
            }
        )
    )
    upload_url = requests.get(crop_url).json()
    upload_url = upload_url["response"]["upload_url"]
    uploaded_data = requests.post(upload_url, files={"photo": image}).json()
    set_cover_url = (
        "https://api.vk.com/method/photos.saveOwnerCoverPhoto?"
        + parse.urlencode(
            {
                "photo": uploaded_data["photo"],
                "hash": uploaded_data["hash"],
                "access_token": access_token,
                "v": 5.67,
            }
        )
    )
    upload_result = requests.get(set_cover_url).content
    return upload_result


def reduce_opacity(im, opacity):
    """
    Returns an image with reduced opacity.
    Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/362879
    """

    assert opacity >= 0 and opacity <= 1
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im


def wrap_header(name, sum_, maxWidth):
    """
    Wrap header string
    """

    header = "{name} — {sum}RUB".format(
        name=name,
        sum=sum_
    )
    if len(header) > maxWidth:
        header = name[:maxWidth] + "\n" + sum_ + "RUB"

    return header


def wrap_comment(text, width):
    """
    Wrap one-line string
    """

    lines = []
    for paragraph in text.split("\n"):
        line = []
        len_line = 0
        for word in paragraph.split(" "):
            len_word = len(word)
            if len_word > COMMENT_WORD_MAX_LEN:
                word = word[:COMMENT_WORD_MAX_LEN] + "..."
                len_word = len(word)
            if len_line + len_word <= width:
                line.append(word)
                len_line += len_word + 1
            else:
                if len(line) > 0:
                    lines.append(" ".join(line))
                line = [word]
                len_line = len_word + 1
        lines.append(" ".join(line))
    lines = lines[:COMMENT_MAX_LINES]
    return "\n".join(lines)


def add_corners(im, rad):
    """
    Make rounded corner
    """

    circle = Image.new("L", (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new("L", im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)

    _, _, _, opacity = DONATION_PAD_COLOR

    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity / 255)
    im.putalpha(alpha)

    return im


def draw_outline(draw, x, y, finalText, shadow_color, fnt, align, spacing):
    """
    draw outline
    """

    draw.multiline_text(
        (x - 1, y), finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing
    )

    draw.multiline_text(
        (x + 1, y), finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing
    )

    draw.multiline_text(
        (x, y - 1), finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing
    )

    draw.multiline_text(
        (x, y + 1), finalText, fill=shadow_color, font=fnt, align=align, spacing=spacing
    )

    draw.multiline_text(
        (x - 1, y - 1),
        finalText,
        fill=shadow_color,
        font=fnt,
        align=align,
        spacing=spacing,
    )

    draw.multiline_text(
        (x + 1, y - 1),
        finalText,
        fill=shadow_color,
        font=fnt,
        align=align,
        spacing=spacing,
    )

    draw.multiline_text(
        (x - 1, y + 1),
        finalText,
        fill=shadow_color,
        font=fnt,
        align=align,
        spacing=spacing,
    )

    draw.multiline_text(
        (x + 1, y + 1),
        finalText,
        fill=shadow_color,
        font=fnt,
        align=align,
        spacing=spacing,
    )


def render_donation(
    text,
    obscene_filter=True,
    path_to_cover=ORIGINAL_COVER_PATH,
    font_size=FONT_SIZE,
    shadow_color=FONT_COLOR_OUTLINE,
    color=FONT_COLOR,
    font_outline=False,
    align="center",
    spacing=int(FONT_SIZE / 4),
):
    """
    Draw info on sample image
    """

    # load cover
    original = Image.open(path_to_cover)

    # get the Draw object
    draw = ImageDraw.Draw(original)

    # load font
    fnt = ImageFont.truetype(FONT_PATH, font_size)
    finalText = ""

    # calc max amount symbol per line
    availableWidthPx = (MARGIN_RIGHT_COVER - MARGIN_LEFT_COVER)
    widthFontLetterPx = fnt.getsize('a')[0]

    maxSymbolPerLine = int(availableWidthPx/widthFontLetterPx)

    # build output string
    for i in text.values():
        header = wrap_header(
            name=i["name"][:COMMENT_DONATOR_NAME_MAX_LEN],
            sum_=i["sum"],
            maxWidth=maxSymbolPerLine)
        body = wrap_comment(
            text=i["comment"][:COMMENT_MAX_LEN],
            width=maxSymbolPerLine)
        if body:
            finalText += header+"\n"+body+"\n\n"

    # cut last new lines
    finalText = finalText[:-2]

    # swear filter
    if obscene_filter is True:
        finalText = filterBadWords(finalText)

    # amount lines
    linesInFinalText = len(finalText.split("\n")) - 1

    # calc size for picture
    w, h = draw.textsize(finalText, font=fnt)

    # create donation pad
    im = Image.new(
        "RGBA",
        (
            w + DONATION_PAD_ROUNDING_RADIUS + OFFSET_XY,
            h + DONATION_PAD_ROUNDING_RADIUS + OFFSET_XY + spacing * linesInFinalText,
        ),
        DONATION_PAD_COLOR,
    )

    # make it rounded
    im = add_corners(im, DONATION_PAD_ROUNDING_RADIUS)
    # get the Draw of donation pad
    draw = ImageDraw.Draw(im, mode="RGBA")
    x, y = (
        (DONATION_PAD_ROUNDING_RADIUS + OFFSET_XY) / 2,
        (DONATION_PAD_ROUNDING_RADIUS + OFFSET_XY) / 2,
    )

    # draw outline
    if font_outline:
        draw_outline(draw, x, y, finalText, shadow_color, fnt, align, spacing)

    # draw text
    draw.multiline_text(
        (x, y), finalText, fill=color, font=fnt, align=align, spacing=spacing
    )

    # paste donate info on original image
    original.paste(
        im,
        (
            MARGIN_LEFT_COVER +
            max(int((MARGIN_RIGHT_COVER - MARGIN_LEFT_COVER - w) / 2), 0),
            MARGIN_BOTTOM_COVER - (h + spacing * (linesInFinalText + 2)),
        ),
        im,
    )

    stream = BytesIO()
    original.save(stream, format="png")
    stream.seek(0)
    img = stream.read()
    return img, original.width, original.height


def getDeltaTime(time):
    """
    Calc delta between now and last donation time
    """

    dateTimeformat = "%Y-%m-%d %H:%M:%S.%f"
    convertedTime = datetime.strptime(time, dateTimeformat)
    timezone = pytz.timezone("Europe/Moscow")
    timeNow = str(datetime.now(timezone))
    timeNow = timeNow.split("+")[0]
    timeNow = datetime.strptime(timeNow, dateTimeformat)
    delta = (timeNow - convertedTime).total_seconds()
    return delta


def filterBadWords(message):
    """
    Filter swears
    """

    return wordFilter.mask_bad_words(message)


def checkDonations(proxies):
    """
    Check new donation and render it
    """

    global idLastDonation

    needUpdate = False

    # True : if all right
    dataStatus = False
    sess = requests.session()
    sess.proxies.update(proxies)
    r = sess.get(
        BASE_URL.format(
            token=TOKEN_DONATIONPAY,
            limit=LIMIT_DONATIONS_TO_SHOW,
            status=DONATION_STATUS,
        ), headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
    )
    try:
        donations = r.json()["data"]
    except Exception as e:
        print("Bad answer from server: {}".format(str(e)))
        print("Trying use cloudflare bypass...")
        try:
            # clouflare bypass
            cloudFlareBypass = cfscrape.create_scraper(sess=sess, delay=10)
            r = cloudFlareBypass.get(
                BASE_URL.format(
                    token=TOKEN_DONATIONPAY,
                    limit=LIMIT_DONATIONS_TO_SHOW,
                    status=DONATION_STATUS,
                ),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
                }
            )
            donations = r.json()["data"]
        except Exception as e:
            print("Bad answer from server: {}".format(str(e)))
        else:
            dataStatus = True
    else:
        dataStatus = True

    if dataStatus is True:
        # if last is none then set it
        if idLastDonation == -1:
            idLastDonation = donations[0]["id"]
            needUpdate = True
        else:
            # comparing last getted and new getted donation
            if idLastDonation != donations[0]["id"]:
                needUpdate = True
                idLastDonation = donations[0]["id"]

        if needUpdate:
            print("UPDATE!")
            print(donations)
            outForImage = {}

            for i in donations:
                message = i["comment"].replace("Комментарий: ", "")

                message = parser.unescape(message)

                outForImage[i["id"]] = {
                    "name": i["what"],
                    "sum": i["sum"],
                    "comment": message,
                }
            try:
                donation_image, width, height = render_donation(
                    text=outForImage
                )
                upload_cover(
                    image=donation_image, access_token=TOKEN_VK, group_id=GROUP_ID, width=width, height=height
                )
            except Exception as e:
                print("Error: Cant upload cover: {}".format(str(e)))
        else:
            print("Won`t change cover")
            print(donations)
            