# coding: utf-8
import os
import sys
import datetime
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart


def send_mail(receivers, subject, context):
    mail_host = "smtp.zhangyue.com"
    mail_password = "11211010_Lxy"  # change me.
    mail_user = "lixinyi@zhangyue.com"  # change me.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = mail_user
    msg['To'] = receivers.replace(',', ';')
    msg.attach(context)

    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user,mail_password)
        s.sendmail(mail_user, receivers, msg.as_string())
        s.close()
        return True
    except Exception as e:
        print e
        return False


def format_file_data(filename):
    with open(filename, 'rb') as f:
        array_data = convert_to_2d_array(
            f.readlines()
        )
    return array_data


def convert_to_2d_array(data):
    array_data = [
        d.decode('gbk').strip('\n').strip('\r').split('\t')
        for d in data
    ]
    return array_data


def generate_title_html_content(title):
    return """
     <tr>
        {}
     </tr>
     """.format(
        '\n'.join(
            map(lambda t: """<td width="400"><strong>{}</strong></td>""".format(t), title)
        )
    )


def generate_form_data_content(data):
    content = ""
    for row in data:
        content += """<tr>"""
        for col in row:
            col = col.encode('utf-8')
            if col.startswith('0.'):
                col = "%.2f" % (float(col)*100) + "%"
            elif col.replace('.', '').isdigit():
                col = str(int(round(float(col))))
            content += '\n' + \
                """<td width="400">{}</td>""".format(col)
        content += """</tr>"""
    return content


def get_date_subject():
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    return '{}渠道核心指标日监控'.format(yesterday)


if __name__ == '__main__':
    subject = get_date_subject()

    receivers = sys.argv[1]
    title = sys.argv[2].split(',')
    send_file_number = int(sys.argv[3])

    html_content = ""
    for index in xrange(send_file_number):
        filename = sys.argv[4+index]
        data = format_file_data(filename)

        html_content += """<div id="container">
                <p><strong>{}</strong></p>
                <div id="content">
                    <table border="2" bordercolor="black" cellspacing="0" cellpadding="0">
                    """.format(os.path.split(filename)[1].split('.')[0]) \
                        + generate_title_html_content(title) \
                        + generate_form_data_content(data) + """
                    </table>
                </div>
            </div>"""

    html = """\
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

        <body>""" + html_content + """
        </body>
    </head>
    </html>
      """
    context = MIMEText(html, _subtype='html', _charset='utf-8')
    if send_mail(receivers, subject, context):
        print ("Send successfully.")
    else:
        print("Failed to send.")
