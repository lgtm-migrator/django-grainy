from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .helpers import request_method_to_flag
from .util import check_permissions


class ModelViewSetPermissions(BasePermission):

    """
    Use as a permission class on a ModelRestViewSet
    to automatically wire up the following views
    to the correct permissions based on the handled object

    - retrieve
    - list
    - create
    - destroy
    - update
    - partial update
    """

    def has_permission(self, request: Request, view: View):
        if hasattr(view, "Grainy"):
            flag = request_method_to_flag(request.method)
            return check_permissions(request.user, view, flag)

        # view has not been grainy decorated

        return True

    def has_object_permission(self, request: Request, view: View, obj: object):
        flag = request_method_to_flag(request.method)
        return check_permissions(request.user, obj, flag)
