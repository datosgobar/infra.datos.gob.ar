from django.contrib.auth.mixins import UserPassesTestMixin

from infra.apps.catalog.models import Node


class UserIsNodeAdminMixin(UserPassesTestMixin):

    def check_user_is_node_admin(self, user, node_id):
        try:
            node = Node.objects.get(id=node_id)
        except Node.DoesNotExist:
            return False
        if user.is_superuser:
            return True
        return node in user.node_set.all()

    def test_func(self):
        user = self.request.user
        node_id = self.kwargs['node_id']
        return self.check_user_is_node_admin(user, node_id)
