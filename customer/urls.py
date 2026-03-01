from django.urls import path

from customer.views.create_customer_view import CreateCustomerView
from customer.views.delete_customer_view import DeleteCustomerView
from customer.views.detail_customer_view import DetailCustomerView
from customer.views.list_customer_view import ListCustomerView
from customer.views.update_customer_view import UpdateCustomerView

app_name = 'customer'

urlpatterns = [
    path('', ListCustomerView.as_view(), name='list'),
    path('create/', CreateCustomerView.as_view(), name='create'),
    path('<int:pk>/', DetailCustomerView.as_view(), name='detail'),
    path('<int:pk>/update/', UpdateCustomerView.as_view(), name='update'),
    path('<int:pk>/delete/', DeleteCustomerView.as_view(), name='delete'),
]
