from __future__ import annotations

from django.db import models


class CustomerQueryset(models.QuerySet):
    def active(self) -> CustomerQueryset:
        return self.filter(is_active=True)

    def inactive(self) -> CustomerQueryset:
        return self.filter(is_active=False)

    def search(self, query: str) -> CustomerQueryset:
        return self.filter(name__icontains=query)

    def order_by_name(self) -> CustomerQueryset:
        return self.order_by('name')
