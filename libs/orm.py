import datetime

from django.db import models
from django.db.models import query
from common.keys import MODEL_KEY
from common.times import MODEL_CACHE_TIMEOUT
from libs.cache import rds
import logging

info_log = logging.getLogger('inf')


def get(self, *args, **kwargs):
    ''' get data from db with cache '''
    id = kwargs.get('pk') or kwargs.get('id')
    if id is not None:
        model_key = MODEL_KEY % (self.model.__name__, id)
        model_obj = rds.get(model_key)
        if isinstance(model_obj, self.model):
            info_log.debug(f'Found in Cache: model key is ({model_key})')
            return model_obj

    model_obj = self._get(*args, **kwargs)
    model_key = MODEL_KEY % (self.model.__name__, id)
    info_log.debug(f'Not Found in Cache, Get from DB: model key is ({model_key})')
    rds.set(model_key, model_obj, MODEL_CACHE_TIMEOUT)
    info_log.debug(f'Save into Cache: model key is ({model_key})')
    return model_obj


def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    ''' save data to db with cache '''
    self._save(force_insert=False, force_update=False, using=None, update_fields=None)
    model_key = MODEL_KEY % (self.__class__.__name__, self.pk)
    info_log.debug(f'Save into Cache and DB: model key is ({model_key})')
    rds.set(model_key, self, MODEL_CACHE_TIMEOUT)


def to_dict(self,exclude=()):
    ''' model can transform to dict '''
    attr_dict = {}
    for field in self._meta.fields:
        if field.attname not in exclude:
            key = field.attname
            value = getattr(self, key)
            datetime_types = (datetime.date, datetime.time, datetime.datetime)
            if isinstance(value, datetime_types):
                value = str(value)
            attr_dict[key] = value
    return attr_dict

def model_patch():
    ''' change orm model by 'Monkey Patch'. '''
    models.Model._save = models.Model.save
    models.Model.save = save
    query.QuerySet._get = query.QuerySet.get
    query.QuerySet.get = get
    models.Model.to_dict = to_dict
