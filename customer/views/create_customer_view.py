from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView

from common.domain.exceptions.base_exception import DomainException
from customer.application.create_customer import CreateCustomerService
from customer.forms.customer_forms import CreateCustomerForm
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository


class CreateCustomerView(FormView):
    template_name = 'customer/form_customer.html'
    form_class = CreateCustomerForm
    success_url = reverse_lazy('customer:list')

    def get_service(self) -> CreateCustomerService:
        repository = DjangoCustomerRepository()
        return CreateCustomerService(repository)

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('customer:list')
        context['is_update'] = False
        return context

    def form_valid(self, form: CreateCustomerForm) -> HttpResponse:
        user_id = self.request.user.id
        if user_id is None:
            form.add_error(
                None, 'É necessário estar autenticado para cadastrar cliente.'
            )
            return self.form_invalid(form)

        try:
            self.get_service().execute(form.to_dto(created_by=user_id))
        except DomainException as exc:
            form.apply_domain_error(exc)
            return self.form_invalid(form)

        messages.success(
            self.request, f'Cliente {form.cleaned_data["name"]} salvo com sucesso.'
        )
        return super().form_valid(form)
