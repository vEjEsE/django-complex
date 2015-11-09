from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import ContextMixin
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text


class MultipleFormsKwargsMixin(object):

    # main function
    def get_form_kwargs(self, name):
        form_kwargs = self.get_form_post_kwargs()
        form_kwargs.update(self.get_own_form_kwargs(name))
        return form_kwargs

    def get_own_form_kwargs(self, name):
        form_own_kwargs_function = 'get_{name}_form_kwargs'.format(
            name=name
        )
        if hasattr(self, form_own_kwargs_function):
            return getattr(self, form_own_kwargs_function)()
        return {}

    def get_form_post_kwargs(self):
        if self.request.method in ('POST', 'PUT', ):
            return {
                'data': self.request.POST,
                'files': self.request.FILES
            }
        return {}

class MultiFormKwargsMixin(MultipleFormsKwargsMixin):

    def get_form_kwargs(self, name):
        form_kwargs = self.get_form_post_kwargs(name)
        form_kwargs.update(self.get_own_form_kwargs(name))
        return form_kwargs

    def get_form_post_kwargs(self, name):
        if self.request.method in ('POST', 'PUT', ):
            submit_name = self.get_submit_name(name)
            if submit_name in self.request.POST:
                return {
                    'data': self.request.POST,
                    'files': self.request.FILES
                }
        return {}


class MultiSuccessUrlMixin(object):
    success_urls = None

    # main function
    def get_success_url(self, name):
        result = self.get_own_success_url_function(name)
        if result: return result
        result = self.get_own_success_url(name)
        if result: return result
        raise ImproperlyConfigured(
            _('No URL to redirect to. You did almost everything right.')
        )

    def get_own_success_url_function(self, name):
        function_name = 'get_{name}_success_url'.format(
            name=name
        )
        if hasattr(self, function_name):
            return getattr(self, function_name)()
        return None

    def get_own_success_url(self, name):
        if not self.success_urls or type(self.success_urls) is not dict:
            raise ImproperlyConfigured(
                _('No URL to redirect to. Provide a success_urls dict.')
            )
        if name not in self.success_urls:
            raise ImproperlyConfigured(
                _('No URL to redirect to. Provide url'
                  'for \'{name}\' form.').format(
                    name=name
                )
            )
        return self.success_urls[name]


class SuccessUrlMixin(object):
    success_url = None

    def get_success_url(self):
        if not self.success_url:
            raise ImproperlyConfigured(
                _('Provide a success_url string.')
            )
        return self.success_url


class MultipleFormsValidityMixin(object):

    def forms_valid(self, forms):
        return None

    def forms_invalid(self, forms):
        return None


class MultipleFormsView(TemplateResponseMixin, ContextMixin, SuccessUrlMixin,
MultipleFormsValidityMixin, MultipleFormsKwargsMixin, View):
    form_classes = None

    def get_form_classes(self):
        if not self.form_classes or type(self.form_classes) is not dict:
            raise ImproperlyConfigured(
                _('Provide a form_classes dict.')
            )
        return self.form_classes

    def get_forms(self):
        form_classes = self.get_form_classes()
        forms = {}
        for name, klass in form_classes.items():
            form_kwargs = self.get_form_kwargs(name)
            forms[name] = klass(**form_kwargs)
        return forms

    def get(self, request):
        forms = self.get_forms()
        return self.render_to_response(
            self.get_context_data(forms=forms)
        )

    def post(self, request):
        forms = self.get_forms()
        if all([form.is_valid() for form in forms.values()]):
            result = self.forms_valid(forms)
            if result:
                return result
            return HttpResponseRedirect(
                self.get_success_url()
            )
        else:
            result = self.forms_invalid(forms)
            if result: return result
        return self.render_to_response(
            self.get_context_data(forms=forms)
        )


class MultiFormValidityMixin(object):

    def form_valid(self, name, form):
        function_name = '{name}_form_valid'.format(
            name=name
        )
        if hasattr(self, function_name):
            result = getattr(self, function_name)(form)
            if result: return result
        return None

    def form_invalid(self, name, form):
        function_name = '{name}_form_invalid'.format(
            name=name
        )
        if hasattr(self, function_name):
            result = getattr(self, function_name)(form)
            if result: return result
        return None

class MultiFormSubmitNamesMixin(object):

    def get_submit_names(self):
        form_classes = self.get_form_classes()
        submit_names = {}
        for name in form_classes.keys():
            submit_names[name] = self.get_submit_name(name)
        return submit_names

    def get_submit_name(self, name):
        return name + '_submit'

    def render_forms(self, forms, submit_names):
        return self.render_to_response(
            self.get_context_data(
                forms=forms,
                submit_names=submit_names
            )
        )


class MultiFormView(TemplateResponseMixin, ContextMixin,
MultiFormSubmitNamesMixin, MultiSuccessUrlMixin, MultiFormValidityMixin,
MultipleFormsKwargsMixin, View):
    form_classes = None

    def get_form_classes(self):
        if not self.form_classes or type(self.form_classes) is not dict:
            raise ImproperlyConfigured(
                _('Provide a form_classes dict.')
            )
        return self.form_classes

    def get_forms(self):
        form_classes = self.get_form_classes()
        forms = {}
        for name, klass in form_classes.items():
            form_kwargs = self.get_form_kwargs(name)
            forms[name] = klass(**form_kwargs)
        return forms

    def get(self, request):
        forms = self.get_forms()
        submit_names = self.get_submit_names()
        return self.render_forms(forms, submit_names)

    def post(self, request):
        forms = self.get_forms()
        for name in forms.keys():
            submit_name = self.get_submit_name(name)
            if submit_name in request.POST:
                if forms[name].is_valid():
                    result = self.form_valid(name, forms[name])
                    if result:
                        return result
                    return HttpResponseRedirect(
                        self.get_success_url(name)
                    )
                result = self.form_invalid(name, forms[name])
                if result:
                    return result
        submit_names = self.get_submit_names()
        return self.render_forms(forms, submit_names)

    def get_form_post_kwargs(self, name):
        if self.request.method in ('POST', 'PUT', ):
            submit_name = self.get_submit_name(name)
            if submit_name in self.request.POST:
                return {
                    'data': self.request.POST,
                    'files': self.request.FILES
                }
        return {}


class ComplexFormsValidityMixin(object):

    def forms_valid(self, name, forms):
        function_name = '{name}_forms_valid'.format(
            name=name
        )
        if hasattr(self, function_name):
            result = getattr(self, function_name)(forms)
            if result: return result
        return None

    def forms_invalid(self, name, forms):
        function_name = '{name}_forms_invalid'.format(
            name=name
        )
        if hasattr(self, function_name):
            result = getattr(self, function_name)(forms)
            if result: return result
        return None


class ComplexFormsView(TemplateResponseMixin, ContextMixin,
MultiFormSubmitNamesMixin, MultiSuccessUrlMixin, MultiFormKwargsMixin,
ComplexFormsValidityMixin, MultiFormValidityMixin, View):
    form_classes = None

    def get_form_classes(self):
        if not self.form_classes or type(self.form_classes) is not dict:
            raise ImproperlyConfigured(
                _('Provide a form_classes dict '
                  '(it can contain a second level dict).')
            )
        return self.form_classes

    def get_forms(self):
        form_classes = self.get_form_classes()
        forms = {}
        for iname, iklass in form_classes.items():
            if type(iklass) is dict:
                forms[iname] = {}
                for jname, jklass in iklass.items():
                    form_kwargs = self.get_form_kwargs(jname, iname)
                    forms[iname][jname] = jklass(**form_kwargs)
            else:
                form_kwargs = self.get_form_kwargs(iname, iname)
                forms[iname] = iklass(**form_kwargs)
        return forms

    def get_form_kwargs(self, name, group_name):
        form_kwargs = self.get_form_post_kwargs(group_name)
        form_kwargs.update(self.get_own_form_kwargs(name))
        return form_kwargs

    def get(self, request):
        forms = self.get_forms()
        submit_names = self.get_submit_names()
        return self.render_forms(forms, submit_names)

    def post(self, request):
        forms = self.get_forms()
        for name in forms.keys():
            submit_name = self.get_submit_name(name)
            if submit_name in request.POST:
                if type(forms[name]) is dict:
                    if all([form.is_valid() for form in forms[name].values()]):
                        result = self.forms_valid(name, forms[name])
                        if result:
                            return result
                        return HttpResponseRedirect(
                            self.get_success_url(name)
                        )
                    result = self.forms_invalid(name, forms[name])
                    if result:
                        return result
                else:
                    if forms[name].is_valid():
                        result = self.form_valid(name, forms[name])
                        if result:
                            return result
                        return HttpResponseRedirect(
                            self.get_success_url(name)
                        )
                    result = self.form_invalid(name, forms[name])
                    if result:
                        return result
        submit_names = self.get_submit_names()
        return self.render_forms(forms, submit_names)
