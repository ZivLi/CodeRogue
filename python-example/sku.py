# coding: utf-8
import redis
import time
from collections import defaultdict
from itertools import chain

from config import app_config
from application.models.models import Sku
from application.models import db
from application.utils.constants import SkuShelvesStatus


redis_client = redis.StrictRedis(host=app_config.REDIS_HOST,
                                 port=app_config.REDIS_PORT,
                                 decode_responses=True,
                                 db=0)

class SKUService:

    _model = Sku
    CACHE_KEY_PREFIX = 'sku_'

    def __init__(self, sku=None):
        if isinstance(sku, self._model):
            self._obj = sku
        elif sku:
            self._obj = Sku.query.get(sku)

    @classmethod
    def add_exclusive_sku_ids(cls, base_sku_id, exclusive_sku_ids):
        cache_key = f'{cls.CACHE_KEY_PREFIX}{base_sku_id}'
        updated_exclusivce_skus = [{'id': base_sku_id, 'exclusive_sku_list': ','.join(exclusive_sku_ids)}]

        exists_sku_ids = redis_client.smembers(cache_key)
        new_sku_ids = exclusive_sku_ids - exists_sku_ids
        remove_sku_ids = exists_sku_ids - exclusive_sku_ids

        for new_sku_id in new_sku_ids:
            new_sku_key = f'{cls.CACHE_KEY_PREFIX}{new_sku_id}'
            redis_client.sadd(new_sku_key, base_sku_id)
            updated_exclusivce_skus.append({
                'id': new_sku_id, 'exclusive_sku_list': ','.join(cls.get_exclusive_sku_ids(new_sku_id))
            })
        for remove_sku_id in remove_sku_ids:
            remove_sku_key = f'{cls.CACHE_KEY_PREFIX}{remove_sku_id}'
            redis_client.srem(remove_sku_key, base_sku_id)
            updated_exclusivce_skus.append({
                'id': remove_sku_id, 'exclusive_sku_list': ','.join(cls.get_exclusive_sku_ids(remove_sku_id))
            })
        redis_client.delete(cache_key)
        if exclusive_sku_ids:
            redis_client.sadd(cache_key, *exclusive_sku_ids)
        cls.sync_into_db(updated_exclusivce_skus)

    @classmethod
    def filter_off_shelves(cls, sku_list):
        return [sku.id for sku in cls._model.query.filter(Sku.id.in_(sku_list)).filter(Sku.shelves_status.notin_([SkuShelvesStatus.ON.value])).all()]

    @classmethod
    def series_and_only_skus(cls, sku_list):
        series_skus = list(cls._model.query.filter(Sku.parent_series.in_(sku_list)).values('name', 'img_src', 'parent_series'))
        sku_num, base_num = len(sku_list), 20
        series_skus_dict = defaultdict(list)
        if series_skus:
            for series_sku in series_skus:
                series_skus_dict[series_sku[2]].append({
                    'img_src': series_sku[1], 'name': series_sku[0]
                })
            sku_num, base_num = sku_num - len(series_skus_dict) + len(series_skus), 25
        return {'series_skus': series_skus_dict,  'sku_num': sku_num, 'base_num': base_num}

    @classmethod
    def sync_into_db(cls, updated_exclusivce_skus):
        db.session.bulk_update_mappings(cls._model, updated_exclusivce_skus)
        db.session.flush()
        db.session.commit()

    @classmethod
    def exclusive_sku_nums(cls, base_sku_id):
        return redis_client.scard(cls.CACHE_KEY_PREFIX + base_sku_id)

    @classmethod
    def get_exclusive_sku_ids(cls, base_sku_id):
        return redis_client.smembers(cls.CACHE_KEY_PREFIX + base_sku_id)

    @classmethod
    def get_template_email_skus(cls, template_sku_ids):
        template_skus = list(cls._model.query.filter(Sku.id.in_(template_sku_ids)).values('name', 'outer_id', 'id'))
        template_base_sku_msg = [sku[1] for sku in template_skus]

        series_sku_list = list(cls._model.query.filter(Sku.parent_series.in_(template_sku_ids)).values('name', 'outer_id', 'parent_series'))
        series_sku_dict = defaultdict(list)
        template_has_series = series_sku_list != []
        for series_sku in series_sku_list:
            series_sku_dict[series_sku[2]].append((series_sku[0], series_sku[1]))

        expand_sku_msg = []
        for sku_msg in template_skus:
            if sku_msg[2] in series_sku_dict:
                expand_sku_msg.extend(series_sku_dict[sku_msg[2]])
            else:
                expand_sku_msg.append((sku_msg[0], sku_msg[1]))

        return expand_sku_msg, template_base_sku_msg, template_has_series

    def get_belong_series(self, sku_ids=None):
        if sku_ids:
            return set(chain(*self._model.query.filter(Sku.id.in_(sku_ids)).values('parent_series')))
        else:
            return set([self._obj.parent_series])

    def is_series(self):
        return self._model.query.filter_by(parent_series=self._obj.id).count()

    @classmethod
    def get_selected_exclusive_skus(cls, sku_ids):
        selected_exclusive_skus = set()
        for sku_id in sku_ids:
            service_inst = SKUService(sku_id)
            if service_inst.is_series():
                series_skus = service_inst.get_series_skus()
                for series_sku in series_skus:
                    series_sku_exclusive_set = SKUService(series_sku).get_self_exclusive_set()
                    selected_exclusive_skus = selected_exclusive_skus | series_sku_exclusive_set
            else:
                self_exclusive_set = service_inst.get_self_exclusive_set()
                selected_exclusive_skus = selected_exclusive_skus | self_exclusive_set
        return selected_exclusive_skus

    def get_self_exclusive_set(self):
        # This is a single sku.
        self_exclusive_set = self.get_exclusive_sku_ids(str(self._obj.id))
        self_exclusive_sku_belong_series_set = set([str(series_id) for series_id in self.get_belong_series([int(_id) for _id in self_exclusive_set] + [self._obj.id])])
        return self_exclusive_set | self_exclusive_sku_belong_series_set | set([str(self._obj.id)])  # It self exclusive skus. SET() | it's belong series id. SET() | it SELF.

    def get_series_skus(self):
        """
            Return: chain obj(iterable). So maybe you should convert to list or set first when you use it.
        """
        skus = list(self._model.query.filter_by(parent_series=self._obj.id).values('id'))
        return chain(*skus)

    def get_exclusive_sku_msg(self):
        keys = ['name', 'id', 'img_src']
        exclusive_sku_ids = SKUService.get_exclusive_sku_ids(str(self._obj.id))
        sku_msgs = self._model.query.filter(Sku.id.in_(exclusive_sku_ids)).values(*keys)
        return [dict(zip(keys, sku)) for sku in sku_msgs]

    def _query(self, on_shelves=False, **kwargs):
        page, per_page = kwargs.pop('page'), kwargs.pop('per_page')
        query = self._model.query.order_by(Sku.update_time.desc())

        if on_shelves:
            query = query.filter_by(shelves_status=SkuShelvesStatus.ON.value)
        if 'name_keyword' in kwargs:
            query = query.filter(Sku.name.like(f"%{kwargs.pop('name_keyword')}%"))
        if kwargs:
            query = query.filter_by(**kwargs)

        if 'page'and 'per_page':
            query = query.paginate(page, per_page)
            return query.items, query.total
        else:
            return query

from sqlalchemy import case
ep=Examination.query.filter(Examination.id.in_([6,7,8])).order_by(case(((Examination.id == 7, 1), (Examination.id != 7, 2))), '-create_time').paginate(1,4)
# CASE and multi order in sqlalchemy.

