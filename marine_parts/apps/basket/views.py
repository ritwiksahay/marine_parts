"""."""
import json
from django.contrib import messages

from django.http import HttpResponse
from django.http import JsonResponse
from django.template.loader import render_to_string

from oscar.core import ajax
from oscar.apps.basket.views import BasketAddView, BasketView
from oscar.apps.basket.formsets import BasketLineFormSet


class AsynBasketView(BasketView):

    def json_response(self, ctx, flash_messages):

        # process template for basket counter in navbar
        nav_basket_html = render_to_string(
            'partials/nav_basket.html',
            context=ctx, request=self.request)

        # default output template is basket_content
        template = "basket/partials/basket_content.html"
        # Look for a output template param from POST request
        if self.request.POST.get("output_template", False):
            template = self.request.POST.get("output_template") + ".html"
        basket_html = render_to_string(
            template,
            context=ctx, request=self.request)

        payload = {
            'nav_basket_html': nav_basket_html,
            'content_html': basket_html,
            'messages': flash_messages.as_dict()
        }

        return HttpResponse(json.dumps(payload),
                            content_type="application/json")


class AsynBasketAddView(BasketAddView):
    """Override of basket's add-view to work with Ajax requests."""

    def form_invalid(self, form):
        response = super(AsynBasketAddView, self).form_invalid(form)
        if self.request.is_ajax():
            # Clear django messages from storage since we are using ajax
            storage = messages.get_messages(self.request)
            for message in storage:
                pass
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AsynBasketAddView, self).form_valid(form)
        flash_messages = ajax.FlashMessages()

        if self.request.is_ajax():
            # Clear django messages from storage since we are using ajax
            storage = messages.get_messages(self.request)
            for message in storage:
                pass
            # push message into message's queue
            flash_messages.info(self.get_success_message(form))

            # pass Basket formset to handle the basket element
            formset = BasketLineFormSet(
                strategy=self.request.basket.strategy,
                queryset=self.request.basket.all_lines()
            )

            ctx = {"formset": formset}
            return self.json_response(ctx, flash_messages)
        else:
            return response

    def json_response(self, ctx, flash_messages):
        nav_basket_html = render_to_string(
            'partials/nav_basket.html',
            context=ctx, request=self.request)
        basket_html = render_to_string(
            'basket/partials/basket_quick.html',
            context=ctx, request=self.request)

        payload = {
            'nav_basket_html': nav_basket_html,
            'basket_html': basket_html,
            'messages': flash_messages.as_dict()
        }

        return HttpResponse(json.dumps(payload),
                            content_type="application/json")
