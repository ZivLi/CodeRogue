# coding: utf-8
import random
import time
import json
from flask import jsonify
from sqlalchemy import func, case
from itertools import chain

from application.models.models import Question, Examination, QuestionBelongTo, ExaminationPaper
from application.models import db
from application.utils.constants import TransactionType, QuestionDifficulty, QuestionStatusOption
from application.utils.redis_client import redis_client


class QuestionService():
    _model = Question

    def __init__(self, question_id=None):
        self._obj = self._model.query.get(question_id) if question_id else None

    def _delete(self):
        db.session.delete(self._obj)
        db.session.commit()

    def _query(self, page, per_page, **kwargs):
        if kwargs:
            self._query = self._model.query.filter_by(**kwargs)
        else:
            self._query = self._model.query
        if page and per_page:
            self._query = self._query.paginate(page=page, per_page=per_page)
            return self._query.total, self._query.items
        return self._query

    @classmethod
    def get_random_question(cls, **kwargs):
        return cls._model.query.filter_by(**kwargs).order_by(func.random()).first()

    @staticmethod
    def _serializer(inst, simple=False):
        if simple:
            return {
                'id': inst.id,
                'transaction_id': inst.transaction_id,
                'transaction_type': inst.transaction_type,
                'difficulty': inst.difficulty,
            }
        else:
            return inst.to_dict()

    @classmethod
    def split_question_set_for_gen_exam(cls):
        level_question_dict = {}
        level_question_group = db.session.query(cls._model.difficulty, func.group_concat(cls._model.id), func.count(cls._model.id)).group_by(cls._model.difficulty)
        for level_question in level_question_group:
            level_question_dict[level_question[0]] = level_question[1].split(',')
        return level_question_dict

    @classmethod
    def group_question_set(cls, transaction_type=TransactionType.SHOPPING.value):
        level_question_dict = {}
        level_question_group = db.session.query(cls._model.difficulty, func.group_concat(cls._model.id), func.count(cls._model.id)).filter_by(transaction_type=transaction_type).group_by(cls._model.difficulty)
        for level_question in level_question_group:
            level_question_dict[QuestionDifficulty(level_question[0]).name] = level_question[2]
        return level_question_dict


class ExamService():
    _model = Examination
    _obj = None
    user_id = None

    def __init__(self, exam_id=None, user_id=None):
        if exam_id:
            self._obj = self._model.query.get(exam_id)
        if user_id and user_id != 3:
            # TODO if current_user is not superadmin.
            self.user_id = user_id

    def get_exam_list(self, name_kw=None, page=1, per_page=15):
        self._query = self._model.query
        if name_kw:
            self._query = self._query.filter(self._model.name.like('%' + name_kw + '%'))

        if self.user_id:
            during_exam = self.get_during_exam(self.user_id)
            during_exam = 7  # TODO Just for test.
            exam_paper_msg = {exam_paper.exam_id: exam_paper.finished_time for exam_paper in ExaminationPaper.query.filter_by(user_id=self.user_id).all()}
            if during_exam:
                exam_pagination = self._query.filter(self._model.id.in_(exam_paper_msg.keys())).order_by(
                    case((
                        (self._model.id == during_exam, 1),
                        (self._model.id != during_exam, 2)
                    )),
                    self._model.create_time.desc()).paginate(page, per_page)
            else:
                exam_pagination = self._query.filter(self._model.id.in_(exam_paper_msg.keys())).order_by('-create_time').paginate(page, per_page)
            finished_exams = [ep.exam_id for ep in ExaminationPaper.query.filter_by(user_id=self.user_id).filter(ExaminationPaper.performance!='').all()]
            total, exam_list = exam_pagination.total, [
                {
                    'id': exam.id,
                    'name': exam.name,
                    'create_time': exam.create_time,
                    'question_num': exam.question_num,
                    'finish_time': exam_paper_msg.get(exam.id),
                    'option': self.map_exam_status(exam.id, during_exam, finished_exams, exam.begin_time, exam.end_time)
                } for exam in exam_pagination.items
            ]

        else:
            # Self.user_id is None means the current_user is superadmin.
            exam_pagination = self._query.order_by('-create_time').paginate(page, per_page)
            current_page_exam_ids = [exam.id for exam in exam_pagination.items]

            finished_examinees_nums = dict(db.session.query(ExaminationPaper.exam_id, func.count(ExaminationPaper.user_id)).filter(ExaminationPaper.exam_id.in_(current_page_exam_ids)).filter(ExaminationPaper.performance!='').group_by(ExaminationPaper.exam_id).order_by(func.field(ExaminationPaper.exam_id, *current_page_exam_ids)))
            total, exam_list = exam_pagination.total, [
                {
                    'id': exam.id,
                    'name': exam.name,
                    'question_num': exam.question_num,
                    'create_time': exam.create_time,
                    'finished_examinees_num': finished_examinees_nums.get(exam.id, 0),
                } for _index, exam in enumerate(exam_pagination.items)
            ]
        return total, exam_list

    def map_exam_status(self, exam_id, during_exam, finished_exams, exam_begin_time, exam_end_time):
        current_time = int(time.time())
        if exam_id in finished_exams:
            return QuestionStatusOption.REPORT.value
        else:
            if during_exam is not None:
                if exam_id == during_exam:
                    return QuestionStatusOption.DURING.value
                else:
                    return QuestionStatusOption.NOENTRANCE.value
            else:
                if exam_begin_time <= current_time <= exam_end_time:
                    return QuestionStatusOption.ENTRANCE.value
                else:
                    return QuestionStatusOption.NOENTRANCE.value

    def get_during_exam(self, user_id):
        return redis_client.get(user_id)

    @classmethod
    def create_examination(cls, name, easy_num, middle_num, hard_num, begin_time, end_time, examinees=[], duration=120):
        try:
            questions = cls.gen_exam_question_set(easy_num, middle_num, hard_num)
        except (ValueError, KeyError):
            return None
        exam_inst = cls._create(name, sum((easy_num, middle_num, hard_num)), begin_time, end_time, duration)
        cls._bind_questions_belong_exam(exam_inst.id, questions)
        cls._bind_examinees(exam_inst.id, examinees)
        return exam_inst.id

    @classmethod
    def _bind_examinees(cls, exam_id, examinees):
        create_time = int(time.time())
        objects = [
            ExaminationPaper(exam_id=exam_id, user_id=examinee, create_time=create_time) for examinee in examinees
        ]
        db.session.bulk_save_objects(objects)
        db.session.commit()

    @classmethod
    def _bind_questions_belong_exam(cls, exam_id, question_ids):
        create_time = int(time.time())
        objects = [
            QuestionBelongTo(question_id=qid, exam_id=exam_id, create_time=create_time)
            for qid in question_ids
        ]
        db.session.bulk_save_objects(objects)
        db.session.commit()

    @classmethod
    def _create(cls, name, question_num, begin_time, end_time, duration):
        create_time = int(time.time())
        _inst = cls._model(
            name=name,
            question_num=question_num,
            begin_time=begin_time,
            end_time=end_time,
            duration=duration,
            create_time=create_time,
            creator=3  # TODO Implement creator super admin.
        )
        db.session.add(_inst)
        db.session.commit()
        return _inst

    @classmethod
    def gen_exam_question_set(cls, *level_num):
        level_question_dict = QuestionService.split_question_set_for_gen_exam()

        random_select_questions = [
            random.sample(level_question_dict[_index+1], level_num[_index]) for _index, _ in enumerate(level_num)
        ]
        select_questions = list(chain(*random_select_questions))
        return select_questions

    def get_reports(self):
        _query = ExaminationPaper.query.filter_by(exam_id=self._obj.id)
        if self.user_id:
            _query = _query.filter_by(user_id=self.user_id)
        reports = _query.values('finished_time', 'performance')
        return dict(zip(('finished_time', 'performance'), reports))

    def statistic_answer(self, user_id, question_id, answer, start_time):
        exam_paper = ExaminationPaper.query.filter_by(exam_id=self._obj.id, user_id=user_id).first()
        if exam_paper.performance_base:
            performance_base = json.loads(exam_paper.performance_base)
        else:
            performance_base = {
                'total': self._obj.question_num,
                'total_cost_time': 0,
                'correct': 0,
                'wrong': 0,
                'order_question_num': 0,
                'order_correct_num': 0,
                'tally_question_num': 0,
                'tally_correct_num': 0
            }

        question_inst = Question.query.get(question_id)
        transaction_type = question_inst.transaction_type

        current_question_cost_time = self.cal_current_question_cost_time(start_time)
        performance_base['total_cost_time'] = self.second_convert_to_time(performance_base['total_cost_time'] + current_question_cost_time)
        performance_base[f'{transaction_type}_avg_time'] = self._update_answer_time(performance_base['f{transaction_type}_question_num'], performance_base[f'{transaction_type}_avg_time'], current_question_cost_time)
        performance_base[f'{transaction_type}_question_num'] = self._autoincrement(performance_base[f'{transaction_type}_question_num'])

        question_answer = question_inst.standard_answer
        if question_answer == answer:
            performance_base = self._update_correct_answer(performance_base, question_transacton_type)
        else:
            performance_base = self._update_wrong_answer(performance_base, question_transaction_type)

        performance_base[f'{transaction_type}_correct_rate'] = self.convert_to_percent(
            performance_base[f'{transaction_type}_correct_num'] / performance_base[f'{transaction_type}_question_num']
        )
        self.update_exam_paper_performance(exam_paper, performance_base)

    def update_exam_paper_performance(self, exam_paper, performance):
        exam_paper.performance = json.dumps(performance)
        exam_paper.save()

    def cal_current_question_cost_time(self, start_time):
        return (int(time.time()) - start_time) / 1000

    def second_convert_to_time(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)

    def _update_answer_time(old_question_num, old_avg_time, current_question_cost_time):
        return (old_question_num * old_avg_time + current_question_cost_time) / (old_question_num + 1)

    def _autoincrement(self, x):
        return x + 1

    def convert_to_percent(self, x):
        return '{:.2%}'.format(x)

    def _update_correct_answer(self, _base, _type):
        _base['correct'] = self._autoincrement(_base['corrent'])
        _base['correct_rate'] = self.convert_to_percent(_base['correct'] / _base['total'])
        key = f'{_type}_corrent_num'
        _base[key] = self._autoincrement(_base[key])
        return _base

    def _update_wrong_answer(self, _base, _type):
        _base['wrong'] = self._autoincrement(_base['wrong'])
        return _base

    def get_next_question_id_total_and_NO(self, question_id):
        question_ids = [
            qb.question_id for qb in QuestionBelongTo.query.filter_by(exam_id=self._obj.id).order_by(QuestionBelongTo.id).all()
        ]
        question_index = question_ids.index(question_id)
        if question_id is None:
            next_question_id = question_ids[0]
        elif question_index + 1 == len(question_ids):
            next_question_id = None
        else:
            next_question_id = question_ids[question_index+1]
        return next_question_id, len(question_id), question_index + 1
