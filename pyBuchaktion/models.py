from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

# Create your models here.

# A single book that may be ordered if activated
class Book(models.Model):
    isbn_13 = models.CharField(
        max_length=13,
        unique=True,
        verbose_name="ISBN-13",
    )
    title = models.CharField(
        max_length=42,
        verbose_name=_("title"),
    )
    ACCEPTED='AC'
    REJECTED='RJ'
    PROPOSED='PP'
    OBSOLETE='OL'
    STATE_CHOICES = (
        (ACCEPTED, _('Accepted')),
        (REJECTED, _('Rejected')),
        (PROPOSED, _('Proposed')),
        (OBSOLETE, _('Obsolete')),
    )
    state = models.CharField(
        max_length=2,
        choices=STATE_CHOICES,
        default=ACCEPTED,
        verbose_name=_("status"),
    )
    #alternative
    author = models.CharField(
        max_length=64,
        verbose_name=_("author"),
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        verbose_name=_("price"),
    )
    publisher = models.CharField(
        max_length=64,
        verbose_name=_("publisher"),
    )
    year = models.IntegerField(
        verbose_name=_("year"),
    )
    def __str__(self):
        return '%s (%s) [ISBN: %s]' % (self.title, self.author, self.isbn_13)
    def statename(self):
        return [v for s, v in self.STATE_CHOICES if s == self.state][0]
    def get_absolute_url(self):
        return reverse("pyBuchaktion:book", kwargs={'book_id': self.pk})
    def natural_key(self):
        return { "id": self.id, "isbn": self.isbn_13 }
    class Meta:
        verbose_name = _("book")
        verbose_name_plural = _("books")

# An order that a particular student has posted
class Order(models.Model):
    # Pending: The user posted a revocable order to us
    PENDING='PD'
    # Ordered: We posted the order to the bookstore, irrevocable
    ORDERED='OD'
    # Rejected: Order was rejected by us or the bookstore
    REJECTED='RJ'
    # Arrived: Order was successful, the book has arrived
    ARRIVED='AR'
    STATE_CHOICES = (
        (PENDING, _('Pending')),
        (ORDERED, _('Ordered')),
        (REJECTED, _('Rejected')),
        (ARRIVED, _('Arrived')),
    )
    status = models.CharField(
        max_length=2,
        choices=STATE_CHOICES,
        default=PENDING,
        verbose_name=_("status"),
    )
    # A note that will be displayed to the user after a status change
    hint = models.TextField(
        verbose_name=_("hint"),
    )
    book = models.ForeignKey(
        'Book',
        on_delete=models.PROTECT,
        verbose_name=_("book"),
    )
    student = models.ForeignKey(
        'Student',
        on_delete=models.PROTECT,
        verbose_name=_("student"),
    )
    order_timeframe = models.ForeignKey(
        'OrderTimeframe',
        on_delete=models.CASCADE,
        verbose_name=_("order timeframe"),
    )
    def __str__(self):
        return '%s: %s [%s]' % (self.student, self.book.title, self.order_timeframe.start_date)
    def statusname(self):
        return [v for s, v in self.STATE_CHOICES if s == self.status][0]
    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

# A student participating in the Buchaktion
class Student(models.Model):
    pass
    library_id = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name=_("library id"),
        default=0,
    )
        
    # empty until CAS login is figured out
    def __str__(self):
        return '#%d' % (self.id)
    def natural_key(self):
        return {"id": self.id}
    class Meta:
        verbose_name = _("student")
        verbose_name_plural = _("students")

# A Timeframe for a set of orders
class OrderTimeframe(models.Model):
    start_date = models.DateField(
        verbose_name=_("start date"),
    )
    end_date = models.DateField(
        verbose_name=_("end date"),
    )
    spendings = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name=_("spendings"),
    )
    semester = models.ForeignKey(
        'Semester',
        on_delete=models.CASCADE,
        verbose_name=_("semester"),
    )
    def __str__(self):
        return "%s - %s (%s)" % (self.start_date, self.end_date, self.semester)
    def natural_key(self):
        return { "from": self.start_date, "to": self.end_date }
    class Meta:
        verbose_name = _("order timeframe")
        verbose_name_plural = _("order timeframes")

# A semester containing a budget
class Semester(models.Model):
    WISE='W'
    SOSE='S'
    SEASON_CHOICES = (
        (WISE, _('Winter term')),
        (SOSE, _('Summer term')),
    )
    class Meta:
        unique_together = ('season', 'year')
        verbose_name = _("semester")
        verbose_name_plural = _("semesters")
    season = models.CharField(
        max_length=1,
        choices=SEASON_CHOICES,
        default=WISE,
        verbose_name=_("season"),
    )
    year = models.DecimalField(
        max_digits=2,
        decimal_places=0,
        verbose_name=_("year"),
    )
    budget = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name=_("budget"),
    )
    def __str__(self):
        if (self.season == 'W'):
            return _('Winter term 20%(year)d/%(next_year)d') % {
                'year': self.year, 'next_year': self.year+1
            }
        else:
            return _('Summer term 20%(year)d') % {'year': self.year}
    def natural_key(self):
        return { "id": self.id, "season": self.season, "year": "20" + str(self.year) }

# A module (e.g. Readings, Exercises, ...)
class TucanModule(models.Model):
    module_id = models.CharField(
        max_length=13,
        unique=True,
        verbose_name=_("module id"),
    )
    name = models.CharField(
        max_length=128,
        verbose_name=_("name"),
    )
    last_offered = models.ForeignKey(
        'Semester',
        on_delete=models.CASCADE,
        verbose_name=_("last offered"),
    )
    literature = models.ManyToManyField(
        'Book',
        verbose_name=_("literature"),
    )
    def __str__(self):
        return '%(name)s [%(module_id)s]' % {'name': self.name, 'module_id': self.module_id}
    def get_absolute_url(self):
        return reverse("pyBuchaktion:module", kwargs={'module_id': self.pk})
    class Meta:
        verbose_name = _("TUCaN module")
        verbose_name_plural = _("TUCaN modules")
