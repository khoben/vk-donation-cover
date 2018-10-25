from os import environ

TOKEN_DONATIONPAY = environ.get("TOKEN_DONATIONPAY")
TOKEN_VK = environ.get("TOKEN_VK")
GROUP_ID = environ.get("GROUP_ID")

BASE_URL = "http://donatepay.ru/api/v1/transactions?access_token={token}&limit={limit}\
                                                                        &status={status}"

# how many donations will requested
LIMIT_DONATIONS_TO_SHOW = 1
# 'success' for real donations
# 'user' for test donations
DONATION_STATUS = "success"
# in seconds
DONATION_UPDATE_INTERVAL = 60

# in symbols
# for whole comment
COMMENT_MAX_LEN = 300
# for single line of comment
COMMENT_LINE_MAX_LEN = 40
COMMENT_DONATOR_NAME_MAX_LEN = 20
COMMENT_MAX_LINES = 6
COMMENT_WORD_MAX_LEN = 19

ORIGINAL_COVER_WIDTH = 3180
ORIGINAL_COVER_HEIGHT = 800
ORIGINAL_COVER_PATH = r"images/original.png"

FONT_PATH = r"fonts/GothaProBol.otf"
FONT_SIZE = 65
FONT_COLOR = "#ffffff"
FONT_COLOR_OUTLINE = "#000000"

DONATION_PAD_COLOR = (0, 0, 0, 200)
DONATION_PAD_ROUNDING_RADIUS = 45

# in pixels
OFFSET_XY = 5
MARGIN_LEFT_COVER = 1760
MARGIN_RIGHT_COVER = 2724
MARGIN_TOP_COVER = 45
MARGIN_BOTTOM_COVER = 770
