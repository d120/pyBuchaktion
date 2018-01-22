from django.conf import settings

BUCHAKTION_STUDENT_LDAP_GROUP = getattr(settings, 'BUCHAKTION_STUDENT_LDAP_GROUP', "FB20")
BUCHAKTION_MESSAGES_DEBUG = getattr(settings, 'BUCHAKTION_MESSAGES_DEBUG', True)
