from django.contrib.auth.mixins import UserPassesTestMixin

from infra.apps.catalog.models import Node


class UserIsNodeAdminMixin(UserPassesTestMixin):

    def test_func(self):
        user = self.request.user
        node_id = self.kwargs['node_id']
        try:
            node = Node.objects.get(id=node_id)
        except Node.DoesNotExist:
            return False
        return node in user.node_set.all()
