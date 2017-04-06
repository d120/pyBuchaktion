from django import template

register = template.Library()

@register.inclusion_tag('bootstrap/alert_dismiss_button.html')
def alert_dismiss_button():
	return {}

@register.inclusion_tag('bootstrap/form_field.html')
def form_field(field):
    return {
        'field_output': field.as_widget(attrs={'class': "form-control", 'placeholder':field.label}),
        'field': field,
    }

@register.inclusion_tag('bootstrap/form_field_static.html')
def form_field_static(field):
    return {
        'field': field,
    }

@register.inclusion_tag('bootstrap/form.html')
def form(form):
    return {'form' : form}

@register.inclusion_tag('bootstrap/form_labeled_field.html')
def form_labeled_field(field):
    return {
        'field': field.as_widget(attrs={'class': "form-control"}),
        'id_for_label': field.id_for_label,
        'label': field.label,
        'errors': field.errors,
        'label_tag': field.label_tag,
        'help_text': field.help_text,
    }

@register.inclusion_tag('bootstrap/form_errors.html')
def form_errors(errors):
    return {'errors': errors}
