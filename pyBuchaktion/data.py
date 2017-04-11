from django.utils.translation import ugettext_lazy as _

from .models import Student, Book, Order, OrderTimeframe

def _model_to_dict(instance, fields=None, exclude=None):
    """
    Returns a dict containing the data in ``instance`` along with any foreign
    keys returned as their respective natural key, if available.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    opts = instance._meta
    data = {}
    for f in opts.get_fields():
        if not getattr(f, 'editable', False):
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        val = f.value_from_object(instance)

        if (isinstance(val, QuerySet)):
            data[f.name] = [i.natural_key() for i in val]
            continue
        if (isinstance(f, ForeignKey)):
            obj = f.rel.to.objects.get(pk=val)
            if (hasattr(obj, 'natural_key')):
                data[f.name] = obj.natural_key()
            else:
                data[f.name] = val
            continue
        data[f.name] = val
    return data
