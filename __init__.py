from piston.handler import BaseHandler
from piston.utils import rc


class JSONFieldHandler(BaseHandler):
    """
    Django Piston handler for JSONField.
    """

    instance = None
    field_name = None

    def get_instance(self, **kwargs):

        pkfield = self.model._meta.pk.name
        if pkfield not in kwargs:
            return None
        try:
            return self.queryset(request).get(pk=kwargs.get(pkfield))
        except (self.model.DoesNotExist, self.model.MultipleObjectsReturned):
            return None

    def filter_data(self, data):

        filtered = {}
        if self.fields:
            for field in self.fields:
                filtered[field] = data[field]
        else:
            filtered = data.copy()
        for key in self.exclude:
            if filtered.has_key(key):
                del(filtered[key])
        return filtered

    def exists(self, **kwargs):

        try:
            return hasattr(self.model.objects.get(**kwargs), self.field_name)
        except self.model.DoesNotExist:
            return False

    def read(self, request, instance=None, *args, **kwargs):

        if not instance:
            instance = self.get_instance(**kwargs)
        if not instance:
            return rc.NOT_IMPLEMENTED

        # Field not found
        if not hasattr(instance, self.field_name):
            return rc.NOT_IMPLEMENTED

        return self.filter_data(getattr(instance, self.field_name))

    def create(self, request, instance=None, *args, **kwargs):

        if not instance:
            instance = self.get_instance(**kwargs)
        if not instance:
            return rc.NOT_IMPLEMENTED

        # Check that field is empty before "create"
        if getattr(instance, self.field_name):
            return rc.DUPLICATE_ENTRY

        data = self.filter_data(request.data)

        # Populate the field and save the instance
        setattr(instance, self.field_name, data)
        instance.save()

        # Return the saved data
        return self.filter_data(getattr(instance, self.field_name))

    def update(self, request, instance=None, *args, **kwargs):

        if not instance:
            instance = self.get_instance(**kwargs)
        if not instance:
            return rc.NOT_IMPLEMENTED

        for key in request.data.keys():
            if key in self.fields and not key in self.exclude:
                instance.__getattribute__(self.field_name)[key] = request.data[key]

        instance.save()

        # Return the saved data
        return self.filter_data(getattr(instance, self.field_name))

    def delete(self, request, instance=None, *args, **kwargs):

        if not instance:
            instance = self.get_instance(**kwargs)
        if not instance:
            return rc.NOT_IMPLEMENTED

        # Clear the field and save the instance
        setattr(instance, self.field_name, {})
        instance.save()

        return rc.DELETED
