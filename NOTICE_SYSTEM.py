# coding: utf-8
import sys
import json
from django.core.mail import EmailMessage
from django.conf import settings
from django.template import loader
from time import time
import datetime

from main.aliyun import sms
from main.models import HPUser, Project, Bounty
from common.services.wechat_client import Client as wechat_cli
from wechat.models import WechatUser
from projects.services import RankService
from spider.models import IPRank, IPUserRank
from main.utils import send_msg

reload(sys)
sys.setdefaultencoding('utf-8')

SIGN_NAME = u'海湃领客'
EMAIL_SUBJECT = u'海湃领客通知'
MEDIA_IP_CATEGORY_MAP = {
    'kids': u'亲子少儿',
    'fun': u'搞笑娱乐',
    'tech': u'科技智能',
    'life': u'生活文化',
    'food': u'美食',
    'fashion': u'时尚美妆',
    'others': u'其他'
}
WECHAT_CLIENT = wechat_cli({
    'APP_ID': settings.WECHAT_MINIPROGRAM_APPID,
    'APP_SECRET': settings.WECHAT_MINIPROGRAM_KEY
})
MINI_PATH = 'pages/direct/direct?tempId={tempId}'
INMAIL_DETAIL_TAIL = '</br></br>如果您在使用中遇到任何问题，都可以点击位于窗口右下角的蓝色按钮，激活对话窗口，我们的产品经理Tianqi会及时提供帮助。'
USER_TYPE_MAP = {
    '1': u'客户',
    '2': u'自媒体',
    '3': u'供应商'
}

NOTICE_TASKS = {
    'SUCCESSFUL_ACCOUNT_AUTHENTICATION': {
        'wechat_template_id': 'SAJlvJ9EWVnqKBsP3oWmyuLL-cHqUdPPZQ0jLeKT9X8',
        'sms_template_code': 'SMS_143710585',
        'title': u'账号认证成功',
    },
    'BIND_WECHAT_ACCOUNT': {
        # 'wechat_template_id': 'g6aMLKi6cxgZKNF9sJwT5SewmY5qJf7i1o0z4gS25-U',
        'sms_template_code': 'SMS_143716812',
        'title': u'绑定微信',
    },
    'FAIL_ACCOUNT_AUTHENTICATION': {
        'wechat_template_id': 'SYf-Fp2tp2ZtoSIckvWBteP5fum7oZA_TK-3DKrj1PU',
        'sms_template_code': 'SMS_143711256',
        'title': u'账号认证失败',
    },
    'PROJECT_UPDATE': {
        'wechat_template_id': 'vk5yB8OWMMv6vCBLcH2ojO7o_gfsfBuaysHubi4zxcA',
        'sms_template_code': 'SMS_143716152',
        'title': u'项目更新通知',
        'InMail_url': '/manage/projects/{project_id}/progress/time',
        'InMail_meta': u'查看项目信息',
    },
    'NEW_MISSION': {
        'wechat_template_id': 'DiHlwMAdbeUNLSxUwolZwn-JzaQAkiB-3CTYKFkMeTk',
        'sms_template_code': 'SMS_143711271',
        'title': u'新任务通知',
        'InMail_url': '/manage/task',
        'InMail_meta': u'查看任务详情',
    },
    'SUCCESSFUL_MEDIA_AUTHENTICATION': {
        'wechat_template_id': 'SAJlvJ9EWVnqKBsP3oWmyuLL-cHqUdPPZQ0jLeKT9X8',
        'sms_template_code': 'SMS_143716146',
        'title': u'添加自媒体认证成功',
        'InMail_url': '/manage/media',
        'InMail_meta': u'查看自媒体详情',
    },
    'FAIL_MEDIA_AUTHENTICATION': {
        'wechat_template_id': 'SYf-Fp2tp2ZtoSIckvWBteP5fum7oZA_TK-3DKrj1PU',
        'sms_template_code': 'SMS_143712295',
        'title': u'添加自媒体认证失败',
        'InMail_url': '/manage/media',
        'InMail_meta': u'查看自媒体详情',
    },
    'SUCCESSFUL_ACCOUNT_REGISTER': {
        'sms_template_code': 'SMS_143711243',
        'title': u'账号注册成功',
        'detail': u'恭喜您已经注册成功，要认证账号、绑定微信后才能解锁所有功能。我们的客户经理会在一个工作日内联系您，请保持手机畅通。'
    },
    'SUCCESSFUL_QUOTATION_ENTRY': {
        'sms_template_code': 'SMS_143711262',
        'title': u'报价录入成功',
        'InMail_url': '/manage/supplier-media',
        'InMail_meta': u'查看上传报价'
    },
    'FAIL_QUOTATION_ENTRY': {
        'sms_template_code': 'SMS_143860095',
        'title': u'报价录入失败',
        'InMail_url': '/manage/price',
        'InMail_meta': u'查看报价详情'
    },
    'ACCOUNT_VERIFY_FILE_SUBMIT': {
        'sms_template_code': 'SMS_143861131',
        'title': u'账号认证提交'
    },
    'RANKING_DATA': {
        'sms_template_code': 'SMS_143867178',
        'wechat_template_id': 'F6QpIp5MuBUPf8YxB800BAhuBfXE1fbbgbgT21RMJ6I',
        'title': u'榜单更新提醒',
        'InMail_url': '/manage/rank',
        'InMail_meta': u'查看榜单详情'
    },
    'MODIFY_ACCOUNT_COMPANY': {
        'sms_template_code': 'SMS_143860105',
        'wechat_template_id': 'gQ1wzBehtGXi4O3Ij2J68gFO2ivSUf7aaS9DGN6Egz8',
        'title': u'修改账号公司名称',
    }
}


class Task(object):

    def __init__(self, _dict):
        self.wechat_temp_id = _dict.get('wechat_template_id')
        self.sms_template_code = _dict.get('sms_template_code')
        self.email_template_name = _dict.get('email_template_name')
        self.InMail_url = _dict.get('InMail_url', '/manage/settings')
        self.InMail_meta = _dict.get('InMail_meta', u'查看账号信息')
        self.title = _dict.get('title')


class EmailTemplateData(object):

    def __init__(self, hpuser, task_key, attach):
        self.hpuser = hpuser
        self.params = dict(name=hpuser.name or '')
        self.func = getattr(self, task_key.lower()) if hasattr(self, task_key.lower()) else None
        self.attach = attach

    @property
    def receiver_data(self):
        if self.func is None:
            return self.func
        self.func()
        return {
            'email': self.hpuser.user.email,
            'content': self.get_html_content(self.params)
        }

    def new_mission(self):
        self.params.update({
            'context': u"""任务大厅有新的任务更新，请登录海湃领客，进入任务大厅查看。<br>
            如果对任务有意向，请点击网站上的按钮“有意向”，我们的PGC经理将会与您联系。（配图）"""
        })

    def successful_account_authentication(self):
        self.params.update({
            'context': u'您的账号认证审核通过，可以开始使用了。'
        })

    def project_update(self):
        proj = Project.objects.get(id=self.attach['project_id'])
        self.params.update({
            'context': u'您的项目“{}”的进度有更新，点击查看详情。'.format(proj.title)
        })

    def bind_wechat_account(self):
        now = datetime.datetime.now()
        date_time = now.strftime(u'%m月%d号 %H:%M')

        wechat_user = WechatUser.objects.get(id=self.attach['wechat_user_id'])

        self.params.update({
            'context': u'您的账号于{}绑定了微信账号：{}。该微信将收到您账号相关的消息，还可自动登录海湃领客小程序。'.format(
                date_time, wechat_user.nickname)
        })

    def fail_account_authentication(self):
        self.params.update({
            'context': u'您的账号认证审核未通过，未通过原因：{}'.format(self.attach['remark'])
        })

    def account_verify_file_submit(self):
        self.params.update({
            'context': u'您的账号认证提交成功，我们的工作人员会在两个工作日内审核完成。'
        })

    def successful_media_authentication(self):
        self.params.update({
            'context': u'您的自媒体{}已认证成功了。请再次确认您已经在账号设置页面扫码绑定了微信小程序，一旦有符合该账号的的任务，我们将会以微信通知+邮件通知+手机通知到您。'.format(self.attach['pgc_ip_name'])
        })

    def fail_media_authentication(self):
        self.params.update({
            'context': u'您申请认证的自媒体{}认证失败了。<br>原因是： {}'.format(self.attach['pgc_ip_name'], self.attach['reason'])
        })

    def successful_quotation_entry(self):
        self.params.update({
            'context': u'您的报价已经录入成功了，在“我的报价”可以检索、查看和选择性导出您的报价了。'
        })

    def fail_quotation_entry(self):
        self.params.update({
            'context': self.attach['reason']
        })

    def ranking_data(self):
        self.params.update({
            'context': u'您关注的自媒体{}上周总榜第{}名、{}榜第{}名。'.format(
                self.attach['name'], self.attach['rank'], self.attach['category'], self.attach['categoryrank']
        )})

    def modify_account_company(self):
        now = datetime.datetime.now()
        date_time = now.strftime(u'%m月%d号 %H:%M')
        self.params.update({
            'context': u'您的账号于{} 公司名称修改为{}，若不是您的操作请修改密码或联系微信：haipailingke_。'.format(date_time, self.attach['company_name'])
        })

    @staticmethod
    def get_html_content(param_dict, template_path='mail.html'):
        return loader.render_to_string(template_path, param_dict)


class WechatTemplateData(object):

    def __init__(self, hpuser, wechat_template_id, task_key, kwargs):
        self.hpuser = hpuser
        self.wechat_users = self.hpuser.wechat.all()
        self.wechat_temp_id = wechat_template_id
        self.func = getattr(self, task_key.lower())
        self.attach = kwargs

    @property
    def receiver_data(self):
        return self.func(self.hpuser, self.attach['wechat_user_id']) if 'wechat_user_id' in self.attach else [self.format_receiver_data(u) for u in self.wechat_users]

    def format_receiver_data(self, wechat_user):
        data = self.func(self.hpuser, wechat_user)
        page_path = self.format_mini_page_path_url(data)
        return {
            'form_id': wechat_user.form_id,
            'touser': wechat_user.mini_openid,
            'template_id': self.wechat_temp_id,
            'page': page_path,
            'data': data,
            # 'emphasis_keyword': ''
        }

    def format_mini_page_path_url(self, data):
        url_params = ''
        for k, v in data.items():
            url_params += '&{}={}'.format(k, v.get('value'))
        return MINI_PATH.format(tempId=self.wechat_temp_id) + url_params

    def new_mission(self, *args, **kwargs):
        mission = Bounty.objects.get(id=self.attach['bounty_id'])
        return {
            'keyword1': {'value': mission.title},
            'keyword2': {'value': mission.details}
        }

    def modify_account_company(self, hpuser, *args, **kwargs):
        now = datetime.datetime.now()
        date_time = now.strftime(u'%m月%d号 %H:%M')
        return {
            'keyword1': {'value': u'公司名称修改为{}'.format(self.attach['company_name'])},
            'keyword2': {'value': date_time},
            'keyword3': {'value': u'若不是您的操作请修改密码或联系微信haipailingke_'}
        }

    def successful_media_authentication(self, hpuser, *args, **kwargs):
        now = datetime.datetime.now()
        return {
            'keyword1': {'value': '{}({})'.format(hpuser.company, hpuser.phone)},
            'keyword2': {'value': u'自媒体认证（{})'.format(self.attach['pgc_ip_name'])},
            'keyword3': {'value': u'{}年{}月{}日'.format(now.year, now.month, now.day)},
            'keyword4': {'value': u'{}已认证为您旗下的账号，请注意接收相关的任务通知。'.format(self.attach['pgc_ip_name'])}
        }

    def fail_media_authentication(self, hpuser, *args, **kwargs):
        now = datetime.datetime.now()
        return {
            'keyword1': {'value': '{}({})'.format(hpuser.company, hpuser.phone)},
            'keyword2': {'value': u'自媒体认证（{})'.format(self.attach['pgc_ip_name'])},
            'keyword3': {'value': u'{}年{}月{}日'.format(now.year, now.month, now.day)},
            'keyword4': {'value': self.attach['reason']}
        }

    @staticmethod
    def successful_account_authentication(hpuser, *args, **kwargs):
        now = datetime.datetime.now()
        return {
            'keyword1': {'value': '{}({})'.format(hpuser.company, hpuser.phone)},
            'keyword2': {'value': u'账号认证'},
            'keyword3': {'value': u'{}年{}月{}日'.format(now.year, now.month, now.day)},
            'keyword4': {'value': u'认证通过'}
        }

    def fail_account_authentication(self, hpuser, *args, **kwargs):
        now = datetime.datetime.now()
        return {
            'keyword1': {'value': '{}({})'.format(hpuser.company, hpuser.phone)},
            'keyword2': {'value': u'账号认证'},
            'keyword3': {'value': u'{}年{}月{}日'.format(now.year, now.month, now.day)},
            'keyword4': {'value': self.attach['remark']}
        }

    @staticmethod
    def bind_wechat_account(hpuser, wechat_user_id):
        wechat_user = WechatUser.objects.get(id=wechat_user_id)
        return {
            'keyword1': {'value': '{}({})'.format(hpuser.company, hpuser.phone)},
            'keyword2': {'value': USER_TYPE_MAP[hpuser.user_type]},
            'keyword3': {'value': wechat_user.nickname},
            'keyword4': {'value': u'该微信将收到您账号相关的消息，还可自动登录海湃领客小程序。'}
        }

    def ranking_data(self, *args, **kwargs):
        now = datetime.datetime.now()
        period = NoticeServer.get_last_weeks_period()
        rank_name = u'周榜（{}第{}周 --- {}）'.format(period[:4], period[-2:], self.attach['name'])
        rank_data = u'{}-{}-{} \n\n总榜排名：{}\n\n{}榜排名：{}'.format(
            now.year, now.month, now.day, self.attach['rank'], self.attach['category'], self.attach['categoryrank'])
        return {
            'keyword1': {'value': rank_name},
            'keyword2': {'value': rank_data}
        }

    def project_update(self, *args, **kwargs):
        proj = Project.objects.get(id=self.attach['project_id'])
        return {
            'keyword1': {'value': proj.title},
            'keyword2': {'value': u'项目进度更新'},
            'keyword3': {'value': proj.hpuser.name},
            'keyword4': {'value': proj.status}
        }


class SMSTemplateData(object):

    def __init__(self, hpuser, template_code, task_key, attach):
        self.hpuser = hpuser
        self.template_code = template_code
        self.func = getattr(self, task_key.lower()) if hasattr(self, task_key.lower()) else None
        self.attach = attach

    @property
    def receiver_data(self):
        template_params = self.func() if self.func is not None else self.func
        __business_id = int(time())
        return [
            __business_id, self.hpuser.phone, SIGN_NAME, self.template_code, template_params
        ]

    def project_update(self):
        proj = Project.objects.get(id=self.attach['project_id'])
        return json.dumps({'project_name': proj.title})

    def bind_wechat_account(self):
        now = datetime.datetime.now()
        date_time = now.strftime(u'%m月%d号 %H:%M')
        wechat_user = WechatUser.objects.get(id=self.attach['wechat_user_id'])
        return json.dumps({
            'date_time': date_time,
            'wechat_account': wechat_user.nickname
        })

    def successful_media_authentication(self):
        return json.dumps({'name': self.attach['pgc_ip_name']})

    def fail_media_authentication(self):
        return json.dumps({'name': self.attach['pgc_ip_name'], 'reason': self.attach['reason']})

    def fail_quotation_entry(self):
        return json.dumps({'reason': u'详情请登录网站查看站内信'})

    def modify_account_company(self):
        now = datetime.datetime.now()
        date_time = now.strftime(u'%m月%d号 %H:%M')
        return json.dumps({'name': self.attach['company_name'], 'date_time': date_time})

    def ranking_data(self):
        return json.dumps(self.attach)


class InMailTemplateData(object):

    def __init__(self, hpuser, detail, url, meta, title):
        self.hpuser = hpuser
        self.detail = detail + INMAIL_DETAIL_TAIL
        self.url = url
        self.meta = meta
        self.title = title

    def send(self):
        send_msg(self.hpuser, category='sys', detail=self.detail, url=self.url, meta=self.meta, title=self.title)


class NoticeServer(object):

    def __init__(self, task_key, hpuser_id, **kwargs):
        self._task = {}
        self.task_key = task_key
        self.hpuser = HPUser.objects.get(id=hpuser_id)
        self.attach = kwargs
        if self.task_key == 'RANKING_DATA':
            self.get_hpuser_fav_best_media()

    def get_hpuser_fav_best_media(self):
        if self.hpuser.user_type == '2':
            self.get_my_best_media_rank()
        else:
            self.get_my_fav_ip_rank()

    def get_my_fav_ip_rank(self):
        rank_server = RankService(self.get_last_weeks_period())
        rank_datas = rank_server.get_data('favorite', self.hpuser, None)
        rank_top = rank_datas.get('rank_data')[0]
        self.update_info_to_attach(rank_top)

    def update_info_to_attach(self, rank_top):
        self.attach.update({
            'name': rank_top['name'],
            'categoryrank': rank_top['category_rank'],
            'rank': rank_top['rank'],
            'category': MEDIA_IP_CATEGORY_MAP[rank_top['category']]
        })

    @staticmethod
    def get_last_weeks_period():
        now_week = datetime.datetime.now().isocalendar()
        period = '{}{}'.format(now_week[0], now_week[1]-1)
        return period

    def get_my_best_media_rank(self):
        rank_server = RankService(self.get_last_weeks_period())
        rank = IPRank.objects.get(period=rank_server.period)

        ips = [_ip.IP for _ip in self.hpuser.pgcip_set.all()]
        best_media = IPUserRank.objects.filter(rank=rank, ip__in=ips).order_by('ranking').first().get_rank
        self.update_info_to_attach(best_media)

    @property
    def task(self):
        return self.get_task()

    def get_task(self):
        task_inst = Task(NOTICE_TASKS[self.task_key])
        email_template = EmailTemplateData(self.hpuser, self.task_key, self.attach)
        self._task.update({'email': email_template.receiver_data})
        InMail_detail = email_template.params.get('context') if 'context' in email_template.params else None
        if InMail_detail:
            self._task.update({'InMail': InMailTemplateData(self.hpuser, InMail_detail, task_inst.InMail_url, task_inst.InMail_meta, task_inst.title)})
        if task_inst.sms_template_code:
            self._task.update({'sms': SMSTemplateData(self.hpuser, task_inst.sms_template_code, self.task_key, self.attach).receiver_data})
        if task_inst.wechat_temp_id:
            self._task.update({'wechat_mini_program': WechatTemplateData(
                self.hpuser, task_inst.wechat_temp_id, self.task_key, self.attach).receiver_data})
        return self._task

    def send(self):
        for pub_channel, receiver in self.task.items():
            if receiver:
                getattr(self, 'send_{}'.format(pub_channel))(receiver)

    def send_InMail(self, receiver):
        receiver.send()

    def send_sms(self, receiver):
        res = sms.send_sms(*receiver)
        json_res = json.loads(res)
        if not json_res['Message'] == 'OK':
            print json_res['Message']

    def send_email(self, receiver):
        email = receiver.get('email')
        html_content = receiver.get('content')
        e = EmailMessage(EMAIL_SUBJECT, html_content, to=[email])
        e.content_subtype = 'html'
        try:
            e.send()
        except Exception as e:
            print e

    def send_wechat_mini_program(self, receivers):
        for r in receivers:
            try:
                WECHAT_CLIENT.template_msg_push(r)
            except Exception as e:
                print e
