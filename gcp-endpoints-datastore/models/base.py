
from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.ext.db import BadRequestError
from shared.ndb_json_helpers import entity_to_dict

import datetime
import logging
# import settings


DATE_FORMAT = "%Y-%m-%d %H:%M:%S" # settings.get('date_format')


class ModelMetaclass(ndb.MetaModel):
    def __new__(cls, name, bases, attrs):
        return super(ModelMetaclass, cls).__new__(cls, name, bases, attrs)


class ModelBase(ndb.Model):
    __metaclass__ = ModelMetaclass
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    updated_on = ndb.DateTimeProperty(auto_now=True)

    MANDATORY_FIELDS = []
    INSERTABLE_FIELDS = []
    DEFAULT_DATE_FIELDS = ['created_on', 'updated_on']
    DATE_FIELDS = []
    INDEXABLE = False
    NON_EXPORTABLE = []
    errors = {}

    def _post_put_hook(self, future):
        if self.INDEXABLE:
            fields = self.to_index()
            facets = self.get_facets()

            try:
                doc = search.Document(doc_id=str(self.key.id()), fields=fields, facets=facets)
                search.Index(self.INDEX_NAME).put(doc)
            except search.Error:
                logging.exception('Put failed')

    @classmethod
    def _post_delete_hook(cls, key, future):
        if cls.INDEXABLE:
            try:
                search.Index(cls.INDEX_NAME).delete(str(key.id()))
            except search.Error:
                logging.exception('Delete failed')

    def to_dict(self):
        result = entity_to_dict(self)
        return result

    def to_json(self, includes=None, excludes=None):
        if excludes is None:
            excludes = []

        self.DATE_FIELDS = self.DATE_FIELDS + self.DEFAULT_DATE_FIELDS
        excludes = excludes + self.DATE_FIELDS + self.NON_EXPORTABLE

        result = entity_to_dict(self, includes, excludes)
        result = self.convert_date_fields(result)
        return result

    def convert_date_fields(self, result):
        if hasattr(self, 'DATE_FIELDS'):
            if self.DATE_FIELDS != []:
                for field in self.DATE_FIELDS:
                    t = type(getattr(self, field))
                    if t is datetime.datetime:
                        date_before = getattr(self, field)
                        date_after = date_before.strftime(DATE_FORMAT)
                        result[field] = date_after
                    elif t is list:
                        dates_before = getattr(self, field)
                        dates_after = [d.strftime(DATE_FORMAT) for d in dates_before]
                        result[field] = dates_after
                    else:
                        v = getattr(self, field)
                        if v is not None:
                            logging.debug('type %s not allowed of the field %s' % (t, field))

        return result

    def build(self, params):
        if hasattr(self, 'INSERTABLE_FIELDS'):
            for key in self.INSERTABLE_FIELDS:
                if key in self.to_dict() and key in params.keys():
                    setattr(self, key, params[key])

    def validate_mandatory_fields(model):
        missing = []

        if hasattr(model, 'MANDATORY_FIELDS'):
            for key in model.MANDATORY_FIELDS:
                value = getattr(model, key)
                if not value:
                    missing.append(key)

        return missing

    def put(self):
        self.errors = {}
        missing = self.validate_mandatory_fields()
        if len(missing) > 0:
            self.errors['missing'] = missing

        if (len(self.errors) == 0):
            super(ModelBase, self).put()
            return True
        else:
            return False

    def error_messages(self):
        if len(self.errors) > 0:
            return {"message": "Invalid request. Missing parameters",
                    "missing": self.errors['missing']}
        else:
            return []

    @classmethod
    def delete(self, id):
        ndb.Key(self, int(id)).delete()

    @classmethod
    def all(self, order=None):
        return self.query().fetch()


    @classmethod
    def find_by_key(self, token):
        q = None
        try:
            key = ndb.Key(urlsafe=token)
            q = key.get()
        except BadRequestError:
            q = None
        return q


def fetch_data(query, args):
    limit = 20
    if 'limit' in args:
        limit = int(args['limit'])

    offset = 0
    if 'offset' in args:
        offset = int(args['offset'])

    return query.fetch(limit, offset=offset)
