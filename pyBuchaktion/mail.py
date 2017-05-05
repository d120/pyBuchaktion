from django.utils import translation
from django.utils.translation import ugettext as _
from django.core.mail.message import EmailMessage


class BuchaktionMessage(EmailMessage):

    def get_content(self):
        return _('This message does not have any content')

    def get_body(self):
        return self.get_intro().format(self.student.tuid_user.name()) \
                    + "\n\n" + self.get_content() + "\n\n" + _(self.get_sign())

    def get_tag(self):
        return "[Buchaktion]"

    def get_intro(self):
        return _("Dear {0}")

    def get_sign(self):
        return _("The Buchaktion Team")

    def get_reply_to(self):
        return ["buchaktion@fachschaft.informatik.tu-darmstadt.de"]

    def get_subject(self):
        return "No Subject"

    def __init__(self, student):

        self.student = student

        super().__init__(
            to = [student.tuid_user.email,]
        )

        f_subject = []
        f_body = []

        for lang in ('de', 'en'):
            with translation.override(lang):
                f_subject += [self.get_subject(),]
                f_body += [self.get_body(),]

        self.subject = self.get_tag() + " " + " / ".join(f_subject)
        self.body = ("\n\n" + "-" * 30 + "\n\n").join(f_body)
        self.reply_to = self.get_reply_to()


class OrderStatusMessage(BuchaktionMessage):

    def get_status_message(self):
        return ""

    def get_content(self):
        book = self.order.book

        fields = (
            (_("Title"), book.title),
            (_("Author"), book.author),
            (_("Published"), ', '.join([book.publisher, str(book.year)])),
            (_("ISBN-13"), book.isbn_13),
        )

        content = self.get_status_message() + "\n"*2
        content += "\n".join([key + ': ' + value for key, value in fields])
        if self.order.hint:
            content += "\n" + _("Hint") + ": " + self.order.hint

        return content

    def __init__(self, order):
        self.order = order
        super().__init__(order.student)


class OrderAcceptedMessage(OrderStatusMessage):

    def get_status_message(self):
        return _("Your order for the book below has been accepted and forwarded to our book retailer. " + \
            "We will inform you when it has arrived at the university library.")

    def get_subject(self):
        return _("Order accepted")


class OrderRejectedMessage(OrderStatusMessage):

    def get_status_message(self):
        return _("Your order for the book below has been rejected. " + \
            "Additional information may be provided in the hint below.")

    def get_subject(self):
        return _("Order rejected")


class OrderArrivedMessage(OrderStatusMessage):

    def get_status_message(self):
        return _("Your ordered book has arrived at the university library. " + \
            "Please pick it up within the next week.")

    def get_subject(self):
        return _("Order arrived")
