from grainy.core import Namespace
from .models import GrainyHandler as _GrainyHandler
from .util import Permissions
from .exceptions import (
    DecoratorRequiresNamespace,
)


class grainy_decorator(object):

    require_namespace = False

    def __init__(self, namespace=None, **kwargs):
        self.namespace = namespace
        self.extra = kwargs
        if self.require_namespace and not namespace:
            raise DecoratorRequiresNamespace(self)

    def make_grainy_handler(self, model):
        class Grainy(_GrainyHandler):
            pass
        Grainy.model = model

        if not model and not self.namespace:
            raise DecoratorRequiresNamespace(self)

        if self.namespace is not None:
            namespace = self.namespace

            @classmethod
            def namespace_model(cls):
                return namespace.lower()
            Grainy.namespace_model = namespace_model
        return Grainy



class grainy_model(grainy_decorator):

    def __call__(self, model):
        model.Grainy = self.make_grainy_handler(model)
        return model


class grainy_view(grainy_decorator):

    require_namespace = True

    def __call__(self, view):
        view.Grainy = self.make_grainy_handler(view)


class grainy_rest_view(grainy_view):
    pass


class grainy_rest_viewset(grainy_decorator):

    require_namespace = True

    def __call__(self, viewset):
        viewset.Grainy = self.make_grainy_handler(viewset)

        extra = self.extra

        class GrainyViewset(viewset):
            def list(self, request):
                response = super(GrainyViewset, self).list(request)
                perms = Permissions(request.user)
                namespace = Namespace(self.Grainy.namespace())
                for ns,p in extra.get("handlers", {}).items():
                    perms.applicator.handler(ns, **p)
                data, tail = namespace.container(response.data)
                response.data = perms.apply(data)
                return response
        GrainyViewset.__name__ = viewset.__name__
        return GrainyViewset
