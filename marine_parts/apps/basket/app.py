from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from oscar.core.application import Application
from oscar.core.loading import get_class

from marine_parts.apps.basket.views import prueba_ajax


class BasketApplication(Application):
    name = 'basket'
    summary_view = get_class('basket.views', 'AsynBasketView')
    saved_view = get_class('basket.views', 'SavedView')
    add_view = get_class('basket.views', 'AsynBasketAddView')
    add_voucher_view = get_class('basket.views', 'VoucherAddView')
    remove_voucher_view = get_class('basket.views', 'VoucherRemoveView')

    def get_urls(self):
        urls = [
            url(r'^$', self.summary_view.as_view(), name='summary'),
            url(r'^add/(?P<pk>\d+)/$', self.add_view.as_view(), name='add'),
            url(r'^prueba/$', prueba_ajax, name="prueba"),
            url(r'^vouchers/add/$', self.add_voucher_view.as_view(),
                name='vouchers-add'),
            url(r'^vouchers/(?P<pk>\d+)/remove/$',
                self.remove_voucher_view.as_view(), name='vouchers-remove'),
            url(r'^saved/$', login_required(self.saved_view.as_view()),
                name='saved'),
        ]
        return self.post_process_urls(urls)


application = BasketApplication()