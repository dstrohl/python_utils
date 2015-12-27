
from .exceptions import UnknownDataTypeException

class FieldManager(object):

    def __init__(self, *fields):
        self._fields = {}
        self._field_choices = []
        self.register_field(*fields)
        self._field_ranking = []

    def register_field(self, *fields):
        for field in fields:
            self._fields[field.field_type] = field
            self._field_choices = (field.field_type, field.field_type_name)
            self._field_ranking.append(dict(
                field_type=field.field_type,
                rank=field.detection_rank,
                coerce=False,
            ))
            if field.detection_coercable:
                self._field_ranking.append(dict(
                    field_type=field.field_type,
                    rank=field.detection_coerce_rank,
                    coerce=True,
                ))
        self._field_ranking.sort(key=lambda k: k['rank'])

    def detect_type(self, sample_data):
        for field in self._field_ranking:
            if self[field['field_type']].check_data_type(sample_data, try_coercing=field['coerce']):
                return field['field_type']
        raise UnknownDataTypeException(sample_data)

    def __getitem__(self, field):
        return self._fields[field]

    def __call__(self, field_type=None, **kwargs):
        tmp_field = self[field_type](**kwargs)
        return tmp_field


