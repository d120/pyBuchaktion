"""
    This module defines all models for the Buchaktion.

    Starting from a book and student model, there is an order model
    which students can post for a specific book. An order is assigned
    to a timeframe at the end of which all pending orders will be
    either forwarded to the bookstore or rejected.

    Timeframes are linked to a semester/term for budget calculations.
    Finally the Module model represents modules such as readings
    which may define literature recommendations as a list of books.
"""

from datetime import datetime
from isbnlib import mask

from django.db import models
from django.db.models import Sum, Prefetch
from django.db.models.signals import pre_save
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from django.dispatch import receiver

from pyTUID.models import TUIDUser

class Book(models.Model):

    """
        A single book that may be ordered if activated. Books are uniquely
        identified by their ISBN-13 number and provide information on
        title, author, publisher, price and year of publication.

        Additionally, a book may have a state that describes whether the book is
        accepted for ordering, has been rejected for ordering, has a new version
        available (obsolete) or has just been proposed for ordering.
    """

    # The International Serial Book Number in the 13 digit version.
    isbn_13 = models.CharField(
        max_length=13,
        unique=True,
        verbose_name="ISBN-13",
    )

    # The title of the book.
    title = models.CharField(
        max_length=140,
        verbose_name=_("title"),
    )

    # The state for a book that is available for ordering.
    ACCEPTED='AC'
    # The state for a book that has been proposed but rejected.
    REJECTED='RJ'
    # The state for a book that has been proposed.
    PROPOSED='PP'
    # The state for a book that has a newer version available.
    OBSOLETE='OL'

    # The list of available states
    STATE_CHOICES = (
        (ACCEPTED, _('Accepted')),
        (REJECTED, _('Rejected')),
        (PROPOSED, _('Proposed')),
        (OBSOLETE, _('Obsolete')),
    )

    # The state of this book
    state = models.CharField(
        max_length=2,
        choices=STATE_CHOICES,
        default=ACCEPTED,
        verbose_name=_("status"),
    )

    # The author(s) of this book
    author = models.CharField(
        max_length=140,
        verbose_name=_("author"),
    )

    # The estimated price for this book, used in internal budget calculations
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        verbose_name=_("price"),
    )
    # The publisher of this book
    publisher = models.CharField(
        max_length=64,
        verbose_name=_("publisher"),
    )
    # The year when this book was published
    year = models.IntegerField(
        verbose_name=_("year"),
    )

    note = models.TextField(
        verbose_name=_("hint"),
        blank=True,
    )

    # The default string output for a book as "<title> (<author>) [ISBN: <isbn>)"
    def __str__(self):
        try:
            isbn = mask(self.isbn_13)
        except Exception:
            isbn = self.isbn_13
        return '%s (%s) [ISBN: %s]' % (self.title, self.author, isbn)

    # Get the name of the current state from the options
    def statename(self):
        return [v for s, v in self.STATE_CHOICES if s == self.state][0]

    # Get the absolute url for this book via the book view, used in the admin
    def get_absolute_url(self):
        return reverse("pyBuchaktion:book", kwargs={'pk': self.pk})

    # Get the natural key for this book, used for JSON output
    def natural_key(self):
        return { "id": self.id, "isbn": self.isbn_13 }

    # Set the singular and plural names for i18n
    class Meta:
        verbose_name = _("book")
        verbose_name_plural = _("books")
        ordering = ['title']


class OrderManager(models.Manager):

    def student_semester_orders(self, student, semester, date=datetime.now()):
        return student.order_set \
            .filter(order_timeframe__semester=semester) \
            .filter(order_timeframe__start_date__lte=date)

    def student_semester_order_count(self, student, semester, date=datetime.now()):
        return self.student_semester_orders(student, semester, date).count()

    def student_book_orders(self, student, book):
        return student.order_set.filter(book=book)

    def student_book_order_count(self, student, book):
        return self.student_book_orders(student, book).count()

    def student_semester_budget_left(student, semester):
        budget_spent = self.student_semester_order_count(student, semester)
        budget_max = OrderTimeframe.objects.semester_budget(semester)
        return budget_max - budget_spent

    def student_annotate_book_queryset(self, student, queryset):
        orders = self.filter(student=student)
        return queryset.prefetch_related(Prefetch('order_set', queryset=orders, to_attr='orderset'))


class Order(models.Model):

    """
        An order that a student has posted for a particular book. The order
        traverses the stages 'pending', 'ordered', 'rejected' and/or 'arrived'.

        In addition to the book and student in question, an order is associated
        with a timeframe that defines when a book was ordered and when the current
        orders will be forwarded to the merchant.
    """

    objects = OrderManager()

    # Pending: The user posted a revocable order to us
    PENDING='PD'
    # Ordered: The order was posted to the bookstore, irrevocable
    ORDERED='OD'
    # Rejected: Order was rejected by this system or the bookstore
    REJECTED='RJ'
    # Arrived: Order was successful, the book has been delivered.
    ARRIVED='AR'

    # The possible states for an order
    STATE_CHOICES = (
        (PENDING, _('Pending')),
        (ORDERED, _('Ordered')),
        (REJECTED, _('Rejected')),
        (ARRIVED, _('Arrived')),
    )

    # The status of an order
    status = models.CharField(
        max_length=2,
        choices=STATE_CHOICES,
        default=PENDING,
        verbose_name=_("status"),
    )

    # A note that will be displayed to the user after a status change
    hint = models.TextField(
        verbose_name=_("hint"),
        blank=True,
    )

    # The book that is ordered
    book = models.ForeignKey(
        'Book',
        on_delete=models.PROTECT,
        verbose_name=_("book"),
    )

    # The student ordering the book
    student = models.ForeignKey(
        'Student',
        on_delete=models.PROTECT,
        verbose_name=_("student"),
    )

    # The timeframe in which this book should be ordered
    order_timeframe = models.ForeignKey(
        'OrderTimeframe',
        on_delete=models.CASCADE,
        verbose_name=_("order timeframe"),
    )

    # Get the default order display as "<student>: <book__title> [<order_timeframe__end_date>]"
    def __str__(self):
        return '%s: %s [%s]' % (self.student, self.book.title, self.order_timeframe.end_date)

    # Get the name of the current status from the options
    def statusname(self):
        if self.status == Order.PENDING and self.book.state == Book.PROPOSED:
            return _("proposal")
        return [v for s, v in self.STATE_CHOICES if s == self.status][0]

    # Set the singular and plural names for i18n
    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")


class StudentManager(models.Manager):

    def from_tuid(self, tuid_user):
        if not tuid_user:
            return None
        return self.filter(tuid_user=tuid_user).first()


class Student(models.Model):

    """
        A student participating in the Buchaktion. A student is someone that
        may log in via the CAS system and is approved for ordering on this
        system either manually or via LDAP group membership for the department
        of computer science.
    """

    # The custom manager
    objects = StudentManager()

    # The library id for this student
    library_id = models.CharField(
        max_length=12,
        unique=True,
        verbose_name=_("library id"),
        null=True,
        blank=True,
        default="",
    )

    tuid_user = models.OneToOneField(
        'pyTUID.TUIDUser',
        on_delete = models.CASCADE,
        verbose_name = _("TUID User"),
    )

    email = models.EmailField(
        verbose_name=_('email')
    )

    LANG_UNDEFINED = ''
    LANG_DE = 'de'
    LANG_EN = 'en'

    # The possible states for an order
    LANG_CHOICES = (
        (LANG_UNDEFINED, _('Not selected')),
        (LANG_DE, _('German')),
        (LANG_EN, _('English')),
    )

    # The status of an order
    language = models.CharField(
        max_length=2,
        choices=LANG_CHOICES,
        default=LANG_UNDEFINED,
        verbose_name=_("preferred language"),
        blank=True,
    )

    # Get the default string representation as "#<id>"
    def __str__(self):
        return "{0} ({1})".format(self.tuid_user.name(), self.tuid_user.uid)

    # Get the natural (foreign reference) key used in JSON serialization
    def natural_key(self):
        return {"id": self.id}

    # Set the singular and plural names for i18n
    class Meta:
        verbose_name = _("student")
        verbose_name_plural = _("students")


@receiver(pre_save, sender=Student)
def save_student(sender, **kwargs):
    """
        Set all empty string values to NULL, so that the libraryID can
        be optional and unique at the same time, while not blocking
        saving in the admin when the field is left empty.
    """
    if not kwargs['instance'].library_id:
        kwargs['instance'].library_id = None


class OrderTimeframeManager(models.Manager):

    def semester_budget(self, semester, date=None):
        if not date:
            date = datetime.now()
        return semester.ordertimeframe_set \
            .filter(start_date__lte=date) \
            .aggregate(Sum('allowed_orders'))['allowed_orders__sum']

    def current(self, date=None):
        if not date:
            date = datetime.now()
        try:
            return self \
                .filter(start_date__lte=date) \
                .filter(end_date__gte=date) \
                .earliest('end_date')
        except OrderTimeframe.DoesNotExist as e:
            return None

    def upcoming(self, date=None):
        if not date:
            date = datetime.now()
        try:
            return self.filter(start_date__gt=date).earliest('end_date')
        except OrderTimeframe.DoesNotExist as e:
            return None


class OrderTimeframe(models.Model):

    """
        A Timeframe for a set of orders. A time frame has a start and an
        end date and is associated with a semester for budget calculations.
    """

    objects = OrderTimeframeManager()

    # The start date of this timeframe
    start_date = models.DateField(
        verbose_name=_("start date"),
    )

    # The end date for this timeframe
    end_date = models.DateField(
        verbose_name=_("end date"),
    )

    # The orders which this field adds
    allowed_orders = models.IntegerField(
        default = 0,
        verbose_name=_("allowed orders"),
    )

    # The amout of money that has already been spent in this timeframe
    spendings = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name=_("spendings"),
    )

    # The semester (and by that budget) this timeframe is associated with
    semester = models.ForeignKey(
        'Semester',
        on_delete=models.CASCADE,
        verbose_name=_("semester"),
    )

    # Get the default string representation as "<start> to <end> (<semester>)"
    def __str__(self):
        start = _("{:%Y-%m-%d}").format(self.start_date)
        end = _("{:%Y-%m-%d}").format(self.end_date)
        return _("%(start)s to %(end)s (%(semester)s)") % {
            'start': start,
            'end': end,
            'semester': self.semester,
        }

    # Get the natural (foreign reference) key for serialization
    def natural_key(self):
        return { "from": self.start_date, "to": self.end_date }

    def student_count(self):
        return self.order_set.values('student').distinct().count()

    # Set the singular and plural names for i18n
    class Meta:
        verbose_name = _("order timeframe")
        verbose_name_plural = _("order timeframes")

class Semester(models.Model):

    """
        A semester containing a budget. A semester may be in summer or winter
        and has a year associated to it by the last two digits. The year is always
        the one in which the semester starts, so it is W16 for winter semester 2016/2017.
    """

    # The winter term season key
    WISE='W'
    # The summer term season key
    SOSE='S'

    # The options for seasons available
    SEASON_CHOICES = (
        (WISE, _('Winter term')),
        (SOSE, _('Summer term')),
    )

    # The season for this semester
    season = models.CharField(
        max_length=1,
        choices=SEASON_CHOICES,
        default=WISE,
        verbose_name=_("season"),
    )

    # The last two digits of the year this semester starts in
    year = models.DecimalField(
        max_digits=2,
        decimal_places=0,
        verbose_name=_("year"),
    )

    # The budget available for spending this semester
    budget = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name=_("budget"),
    )

    # Get the default string representation of a year as "[Winter|Summer] term 20<year>[/<year+1>]"
    def __str__(self):
        if (self.season == 'W'):
            return _('Winter term 20%(year)d/%(next_year)d') % {
                'year': self.year, 'next_year': self.year+1
            }
        else:
            return _('Summer term 20%(year)d') % {'year': self.year}

    # Get the natural (foreign reference) key for a semester
    def natural_key(self):

        return { "id": self.id, "season": self.season, "year": "20" + str(self.year) }

    # Set the singular and pluar names for i18n, and (season, year) as the unique
    class Meta:
        unique_together = ('season', 'year')
        verbose_name = _("semester")
        verbose_name_plural = _("semesters")

class Module(models.Model):

    """
        A module (e.g. readings, exercise groups, ...) that porvides literature
        recommendations which can be looked up through the system. A module has
        a dedicated module_id from the university campus management system,
        as well as a name and information on when it was last offered.

        The name TUCaN refers to the TU Darmstadt CampusNet management system.
    """

    # The custom id for a module
    module_id = models.CharField(max_length=13, unique=True, verbose_name=_("module id"))

    # The german name of the module
    name_de = models.CharField(max_length=128, verbose_name=_("german name"))

    # The english name of the module
    name_en = models.CharField(max_length=128, verbose_name=_("english name"), blank = True)

    # The semester when the module was last offered
    last_offered = models.ForeignKey('Semester', on_delete=models.CASCADE, verbose_name=_("last offered"))

    # The literature that is recommended by this module
    literature = models.ManyToManyField('Book', through='Literature', verbose_name=_("literature"))

    # The category that this module will appear in
    category = models.ForeignKey('ModuleCategory', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('category'))

    # Get the default string representation as "<name> [<module_id>]"
    def __str__(self):
        return '%(name)s [%(module_id)s]' % {'name': self.name, 'module_id': self.module_id}

    @property
    def name(self):
        return self.name_en if get_language() == 'en' and self.name_en else self.name_de

    # Get the frontend url for this module via the module view
    def get_absolute_url(self):
        return reverse("pyBuchaktion:module", kwargs={'module_id': self.pk})

    # Set the singular and plural names for i18n
    class Meta:
        verbose_name = _("module")
        verbose_name_plural = _("modules")
        ordering = ['module_id']


class Literature(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='literature_info', verbose_name=_('module'))
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='literature_info', verbose_name=_('book'))

    STAFF='SF'
    STUDENT='SD'
    TUCAN='TC'

    # The options for seasons available
    SOURCE_CHOICES = (
        (TUCAN, _('TUCaN Export')),
        (STAFF, _('Module Staff')),
        (STUDENT, _('Student')),
    )

    # The season for this semester
    source = models.CharField(
        max_length=2,
        choices=SOURCE_CHOICES,
        default=TUCAN,
        verbose_name=_("source"),
    )

    in_tucan = models.BooleanField(
        default=True,
        verbose_name=_("in TUCaN")
    )

    active = models.BooleanField(
        default=True,
        verbose_name=_("active")
    )

    class Meta:
        unique_together = ('book', 'module')
        verbose_name = _("literature")
        verbose_name_plural = _("literature")


class ModuleCategory(models.Model):

    # The name for this category
    name_de = models.CharField(max_length = 128, verbose_name = _("german name"))

    # The name for this category
    name_en = models.CharField(max_length = 128, verbose_name = _("english name"), blank = True)

    # Whether the category should be visible
    visible = models.BooleanField(default=True, verbose_name = _("visible"))

    # Get the displayed name: english if given and active, else german
    def name(self):
        return self.name_en if get_language() == 'en' and self.name_en else self.name_de

    def __str__(self):
        return self.name()

    class Meta:
        verbose_name = _("module category")
        verbose_name_plural = _("module categories")


class DisplayMessage(models.Model):

    # The key used to display this message
    key = models.CharField(max_length = 250, unique=True, verbose_name = _("key"))

    # The german text for this message
    text_de = models.TextField(max_length = 4000, verbose_name = _("german text"))

    # The english text for this message
    text_en = models.TextField(max_length = 4000, verbose_name = _("english text"))

    def text(self):
        return self.text_en if get_language() == 'en' and self.text_en else self.text_de

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = _("display message")
        verbose_name_plural = _("display messages")
