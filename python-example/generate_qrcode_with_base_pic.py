import qrcode
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


env = os.environ.get("FRIDGE_SERVER_ENV")


class QRCodeService:

    def __init__(self):
	self.QR_PREFIX = ""

    def _gen(self, qr_str):
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=0
        )
        qr.add_data(qr_str)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img


class DeviceQRCodeService(QRCodeService):

    BASE_IMG_PATH = 'application/utils/static/blank.png'
    BASE_FONT_PATH = 'application/utils/static/PingFang-sc.ttf'
    STD_DEVICE_ID_POSITION = (2324, 4644)
    OLD_DEVICE_ID_POSITION_LINE_1 = (2200, 4606)
    OLD_DEVICE_ID_POSITION_LINE_2 = (2200, 4746)
    OLD_DEVICE_ID_LINE_1_SPLIT = 19
    DEVICE_NAME_POSITION = (1275, 5768)
    DEVICE_LOCATION_POSITION = (1275, 6119)
    QRCODE_SIZE = (1860, 1860)
    SOFT_FONT_COLOR = '#5e5e5e'
    BLACK_FONT_COLOR = '#282B31'
    STD_DEVICE_ID_LENGTH = 12

    def __init__(self, device_id, device_name, device_location):
        super(DeviceQRCodeService, self).__init__()
        self.device_id = device_id
        self.device_name = device_name
        self.device_location = device_location
        self.img_base = Image.open(self.BASE_IMG_PATH).convert('RGBA')
        self._font = ImageFont.truetype(self.BASE_FONT_PATH, 140)
        self.old_device_id_font = ImageFont.truetype(self.BASE_FONT_PATH, 120)


    def gen_qrcode(self):
	# Just implement draw picture as PHOTOSHOP.
        qr_str = self.QR_PREFIX + self.device_id
        img = self._gen(qr_str)
        buf = BytesIO()
        img.save(buf)
        _q = Image.open(buf).convert('RGBA').resize(self.QRCODE_SIZE, Image.ANTIALIAS)
        txt = Image.new('RGBA', self.img_base.size, (255, 255, 255, 0))
        d = ImageDraw.Draw(txt)

        if len(self.device_id) <= self.STD_DEVICE_ID_LENGTH:
            d.text(self.STD_DEVICE_ID_POSITION, f'xx编号：{self.device_id}'.encode().decode('utf-8'), font=self._font, fill=self.SOFT_FONT_COLOR)
        else:
            d.text(
                self.OLD_DEVICE_ID_POSITION_LINE_1,
                f'xx编号：{self.device_id[:self.OLD_DEVICE_ID_LINE_1_SPLIT]}'.encode().decode('utf-8'),
                font=self.old_device_id_font, fill=self.SOFT_FONT_COLOR)
            d.text(
                self.OLD_DEVICE_ID_POSITION_LINE_2,
                f'{self.device_id[self.OLD_DEVICE_ID_LINE_1_SPLIT:]}'.encode().decode('utf-8'),
                font=self.old_device_id_font, fill=self.SOFT_FONT_COLOR)
        d.text(self.DEVICE_NAME_POSITION, f'xx名称：{self.device_name}'.encode().decode('utf-8'), font=self._font, fill=self.BLACK_FONT_COLOR)
        d.text(self.DEVICE_LOCATION_POSITION, f'xx位置：{self.device_location}'.encode().decode('utf-8'), font=self._font, fill=self.BLACK_FONT_COLOR)

        self.img_base.paste(_q, (2218, 2708))
        qrcode_img = Image.alpha_composite(self.img_base, txt)
        output = BytesIO()
        qrcode_img.save(output, 'png', dpi=(762, 762))
        output.seek(0)
        return output
