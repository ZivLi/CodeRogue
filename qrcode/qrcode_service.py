# coding: utf-8
import qrcode
from PIL import Image, ImageDraw, ImageFont


class QRCodeService:

    def __init__(self):
        self.QR_PREFIX = ''

    def _gen(self, qr_str):
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=0
        )
        qr.add_data(qr_str)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black')
	# 生成二维码

        newimg = img.convert("RGBA")
        source = img.split()
        R = 0
        rmask = source[R].point(lambda i: i>= 255 and 255)
        out = Image.new("RGBA", img.size, None)
        newimg.paste(out, None, rmask)
	# 转化为透明底二维码
	newimg.show()

        output = BytesIO()
        newimg.save(output, 'png', dpi=(762, 762))
        output.seek(0)
	# 返回字节流
        return output


if __name__ == '__main__':
    s = QRCodeService()
    s._gen('test')
