from django.db.models import PositiveIntegerField
from django.core.exceptions import ObjectDoesNotExist


class OrderField(PositiveIntegerField):
    def __init__(self, fields=None, *args, **kwargs):
        self.fields = fields
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:
            try:
                qs = self.model.objects.all()
                if self.fields:
                    query = {field: getattr(model_instance, field)\
                             for field in self.fields}
                    qs = qs.filter(**query)
                last_item = qs.latest(self.attname)
                value = getattr(last_item, self.attname) + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)