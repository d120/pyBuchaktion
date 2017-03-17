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