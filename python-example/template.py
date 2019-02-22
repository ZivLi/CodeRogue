# coding: utf-8
import datetime
import json
import time
from tempfile import TemporaryDirectory

from application.models.models import Template, TemplateSkuLink, Sku
from application.models.models import AlgorithmModel
from application.models.model_base import db
from application.dao import business as business_dao
from application.utils.email_helper import TEMPLATE_CREATE_NOTICE, send_email
from application.utils.time_util import DEFAULT_TZ
from erp.controllers.sku import SKUService


def algorithm_auth_check(APP, SECRET):
    return APP == 'fridge_alg' and SECRET == 'f447777e148d11e99b3c8c85905f179d'

class TemplateService:

    _model = Template

    def __init__(self, template):
        if isinstance(template, self._model):
            self._obj = template
        else:
            self._obj = self._model.query.get(template)

    def notice_algorithm_team(self, business_id):
        business_name = business_dao.get_business(business_id).name
        bind_sku_ids = [sku[0] for sku in TemplateSkuLink.query.filter_by(template_id=self._obj.id).values('sku_id')]

        skus_msg, template_base_sku_msg, template_has_series = SKUService.get_template_email_skus(bind_sku_ids)
        bind_sku_num = len(skus_msg)

        algorithm_model = self.algorithm_model_adapt(set([sku[1] for sku in skus_msg]))
        if algorithm_model:
            return self.auto_bind_model_name(algorithm_model)

        body_str = "<br>".join([", ".join([sku[0], sku[1]]) for sku in skus_msg])
        current_date = datetime.datetime.now(tz=DEFAULT_TZ).strftime('%Y-%m-%d')

        TEMPLATE_CREATE_NOTICE['html_body'] = TEMPLATE_CREATE_NOTICE['html_body'].format(body_str=body_str, sku_num=bind_sku_num, template_id=self._obj.id)
        TEMPLATE_CREATE_NOTICE['subject'] = TEMPLATE_CREATE_NOTICE['subject'].format(create_date=current_date, business_name=business_name)

        with TemporaryDirectory() as td:
            file_names = ['sku.txt']
            with open(td+file_names[0], 'w') as sku_file:
                for sku in skus_msg:
                    sku_file.writelines(sku[1] + '\n')
                sku_file.seek(0)
            if template_has_series:
                file_names.append('template_series_sku.txt')
                with open(td+file_names[1], 'w') as template_sku_file:
                    for template_sku in template_base_sku_msg:
                        template_sku_file.writelines(template_sku + '\n')
                    template_sku_file.seek(0)
            send_email(file_obj=[td+file_name for file_name in file_names],
                file_name=file_names, **TEMPLATE_CREATE_NOTICE)

    def algorithm_model_adapt(self, sku_outer_ids):
        algo_models = AlgorithmService._model.query.all()
        algo_values = [{
            'create_time': algo.create_time, 'skus': set(json.loads(algo.sku_details).keys()), 'model_name': algo.model_name
        } for algo in algo_models]

        sorted_algo_values = sorted(algo_values, key=lambda x: (len(x['skus']), -x['create_time']))
        # Sort existed algorithm models by sku num first (asc), and create_time second (desc).

        for algo_model in sorted_algo_values:
            if not sku_outer_ids - algo_model['skus']:
                return algo_model['model_name']
        return None

    def auto_bind_model_name(self, algorithm_model):
        algo_service = AlgorithmService({'template_id': self._obj.id})
        algo_service.bind_template_algorithm_id(algorithm_model)

    @classmethod
    def has_created_times(cls, business_id, create_user_id):
        base_time = (datetime.datetime.today().replace(day=1)).timestamp()
        return 3 - \
            Template.query.filter(Template.create_time >= base_time).filter_by(
                create_user=create_user_id, business_id=business_id).count()


class AlgorithmService:

    _model = AlgorithmModel

    def __init__(self, api_callback_json):
        self.algorithm_data = api_callback_json.get('algorithm_data')
        self.template_id = api_callback_json.get('template_id')

    def save(self):
        self.algorithm_data['sku_details'] = json.dumps(self.algorithm_data['sku_details'])
        self.algorithm_data['quality'] = json.dumps(self.algorithm_data['quality'])
        self.algorithm_data['file_name'] = f"{self.algorithm_data['model_name']}.json"
        self.algorithm_data['create_time'] = self.algorithm_data['update_time'] = int(time.time())
        alg = self._model(**self.algorithm_data)
        db.session.add(alg)
        db.session.commit()

        self.bind_template_algorithm_id(alg.model_name)

    def bind_template_algorithm_id(self, algorithm_model_name):
        db.session.query(Template).filter_by(id=self.template_id).update({'algo_identity': algorithm_model_name})
        db.session.commit()

    @classmethod
    def is_model_name_exist(cls, model_name):
        return cls._model.query.filter_by(model_name=model_name).count()
