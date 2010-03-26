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

        return getattr(instance, self.field_name)

    def create(self, request, instance=None, *args, **kwargs):

        if not instance:
            instance = self.get_instance(**kwargs)
        if not instance:
            return rc.NOT_IMPLEMENTED

        # Check that field is empty before "create"
        if getattr(instance, self.field_name):
            return rc.DUPLICATE_ENTRY

        data = request.data.copy()
        for key in self.exclude:
            try:
                del(data[key])
            except KeyError:
                pass

        # Populate the field and save the instance
        setattr(instance, self.field_name, data)
        instance.save()

        # Return the saved data
        return getattr(instance, self.field_name)

    def update(self, request, instance=None, *args, **kwargs):

        if not instance:
            instance = self.get_instance(**kwargs)
        if not instance:
            return rc.NOT_IMPLEMENTED

        for key in request.data.keys():
            if not key in self.exclude:
                instance.__getattribute__(self.field_name)[key] = request.data[key]

        instance.save()

        # Return the saved data
        return getattr(instance, self.field_name)

    def delete(self, request, instance=None, *args, **kwargs):

        if not instance:
            instance = self.get_instance(**kwargs)
        if not instance:
            return rc.NOT_IMPLEMENTED

        # Clear the field and save the instance
        setattr(instance, self.field_name, {})
        instance.save()

        return rc.DELETED
