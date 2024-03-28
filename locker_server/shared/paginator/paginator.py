from math import ceil

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.pagination import PageNumberPagination
from django.utils.translation import gettext_lazy as _


class CustomCountPaginator(Paginator):
    def validate_number(self, number):
        """Validate the given 1-based page number."""
        try:
            if isinstance(number, float) and not number.is_integer():
                raise ValueError
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger(_('That page number is not an integer'))
        if number < 1:
            raise EmptyPage(_('That page number is less than 1'))
        return number

    def page(self, number):
        number = self.validate_number(number)
        return self._get_page(self.object_list, number, self)


class CustomCountPageNumberPagination(PageNumberPagination):
    count = None
    django_paginator_class = CustomCountPaginator

    def get_paginated_response(self, data):
        if self.count is not None:
            self.page.paginator.count = self.count
            self.page.paginator.count = self.count
            hits = max(1, self.count)
            self.page.paginator.num_pages = ceil(hits / self.page.paginator.per_page)
        return super().get_paginated_response(data)
