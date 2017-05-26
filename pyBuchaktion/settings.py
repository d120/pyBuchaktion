from django.conf import settings

BUCHAKTION_STUDENT_LDAP_GROUP = getattr(settings, 'BUCHAKTION_STUDENT_LDAP_GROUP', "cn=_fb_20,ou=STUD,o=TU")
