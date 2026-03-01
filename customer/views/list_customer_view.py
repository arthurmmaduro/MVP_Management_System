from django.core.paginator import Paginator
from django.views.generic import TemplateView

from customer.application.list_customer import ListCustomerService
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository


class ListCustomerView(TemplateView):
    template_name = 'customer/list_customer.html'
    paginate_by = 10

    def get_service(self) -> ListCustomerService:
        repository = DjangoCustomerRepository()
        return ListCustomerService(repository)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        output = self.get_service().execute()
        paginator = Paginator(output.customers, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['customers'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        return context
