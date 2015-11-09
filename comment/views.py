from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import JsonResponse

from braces.views import JSONResponseMixin

from utils.views import MultipleFormsView, MultiFormView, ComplexFormsView

from .forms import CommentForm, RequestForm, RegisterForm


class QweANDAsdView(MultipleFormsView):
    form_classes = {
        'register': RegisterForm,
        'comment': CommentForm
    }
    template_name = 'qwe_and_asd.html'
    success_url = reverse_lazy('qweasd')

    def get_register_form_kwargs(self):
        return {
            'initial': {
                'username': 'qwe',
                'password': 'qweqwe'
            }
        }

    def get_comment_form_kwargs(self):
        return {
            'initial': {
                'name': 'asd',
                'message': 'Asd asd asd asd asd asd asd asd asd.'
            },
            'prefix': 'asd'
        }

    def forms_valid(self, forms):
        print forms
        return JsonResponse(
            {
                'qwe': 123,
                'asd': 456
            }
        )


class QweORAsdView(MultiFormView):
    form_classes = {
        'comment': CommentForm,
        'request': RequestForm
    }
    template_name = 'qwe_or_asd.html'
    success_urls = {
        'comment': reverse_lazy('qwe'),
        'request': reverse_lazy('asd')
    }

    def get_comment_form_kwargs(self):
        return {
            'initial': {
                'name': 'qwe',
                'message': 'Qwe qwe qwe qwe qwe qwe qwe qwe qwe qwe qwe.'
            },
            'prefix': 'zxc'
        }

    def get_request_form_kwargs(self):
        return {
            'initial': {
                'email': 'asd@asd.asd',
                'request': 'Asd asd asd asd.'
            }
        }

    def comment_form_valid(self, form):
        print form
        return JsonResponse({
            'qwe': 123
        })

    def comment_form_invalid(self, form):
        print form

    def request_form_valid(self, form):
        print form

    def request_form_invalid(self, form):
        print form

    def get_request_success_url(self):
        return reverse('qwe')


class QweANDAsdORZxcView(ComplexFormsView):
    form_classes = {
        'first_comment': {
            'register': RegisterForm,
            'comment': CommentForm
        },
        'request': RequestForm
    }
    template_name = 'qwe_and_asd_or_zxc.html'
    success_urls = {
        'first_comment': 'qweasd',
        'request': 'qwe'
    }

    def get_register_form_kwargs(self):
        return {
            'initial': {
                'username': 'qwe',
                'password': 'qweqwe'
            },
            'prefix': 'qwe'
        }

    def get_comment_form_kwargs(self):
        return {
            'initial': {
                'name': 'asd',
                'message': 'Asd asd asd asd asd asd asd asd.'
            }
        }

    def get_request_form_kwargs(self):
        return {
            'initial': {
                'email': 'zxc@zxc.zxc',
                'request': 'Zxc zxc zxc zxc zxc zxc.'
            }
        }

    def first_comment_forms_valid(self, forms):
        print 'comment: ' + str(forms)

    def request_form_valid(self, form):
        print form
