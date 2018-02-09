from django.conf.urls import url
from oscar.core.application import DashboardApplication
import views

class BulkPriceUpdaterApplication(DashboardApplication):
    name = None
    default_permissions = ['is_staff', ]
    permissions_map = {
        'index': ['is_staff'],
    }

    def get_urls(self):
        urls = [
            url(r'^$', views.UploadFileView.as_view(), name='bulk-price-updater-index'),
            url(r'review/$', views.ReviewUpdater.as_view(), name='bulk-price-updater-review')

        ]
        return self.post_process_urls(urls)


application = BulkPriceUpdaterApplication()