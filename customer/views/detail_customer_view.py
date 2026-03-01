from django.http import Http404
from django.views.generic import TemplateView

from customer.application.detail_customer import DetailCustomerService
from customer.domain.dto.detail_customer_dto import CustomerDetailInput
from customer.domain.exceptions.customer_exceptions import CustomerNotFound
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository


class DetailCustomerView(TemplateView):
    template_name = 'customer/detail_customer.html'

    def get_service(self) -> DetailCustomerService:
        repository = DjangoCustomerRepository()
        return DetailCustomerService(repository)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            output = self.get_service().execute(
                CustomerDetailInput(customer_id=self.kwargs['pk'])
            )
        except CustomerNotFound as exc:
            raise Http404(str(exc)) from exc

        context['customer'] = output
        return context
