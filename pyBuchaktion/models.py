from django.db import models
from django.utils.translation import ugettext as _

# Create your models here.

# A single book that may be ordered if activated
class Book(models.Model):
	isbn_13 = models.CharField(
		max_length=13,
		unique=True,
	)
	title = models.CharField(max_length=42)
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
	)
	#alternative
	author = models.CharField(max_length=64)
	price = models.DecimalField(
		max_digits=6,
		decimal_places=2,
		null=True,
	)
	def __str__(self):
		return '%s (%s) [ISBN: %s]' % (self.title, self.author, self.isbn_13)
	def statename(self):
		return [v for s, v in self.STATE_CHOICES if s == self.state][0]

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
		(PENDING, 'Pending'),
		(ORDERED, 'Ordered'),
		(REJECTED, 'Rejected'),
		(ARRIVED, 'Arrived'),
	)
	status = models.CharField(
		max_length=2,
		choices=STATE_CHOICES,
		default=PENDING
	)
	# A note that will be displayed to the user after a status change
	hint = models.TextField()
	book = models.ForeignKey(
		'Book',
		on_delete=models.PROTECT,
	)
	student = models.ForeignKey(
		'Student',
		on_delete=models.PROTECT,
	)
	order_timeframe = models.ForeignKey(
		'OrderTimeframe',
		on_delete=models.CASCADE,
	)
	def __str__(self):
		return '%s: %s [%s]' % (self.student, self.book.title, self.order_timeframe.start_date)

# A student participating in the Buchaktion
class Student(models.Model):
	pass
	# empty until CAS login is figured out
	def __str__(self):
		return '#%d' % (self.id)

# A Timeframe for a set of orders
class OrderTimeframe(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()
	spendings = models.DecimalField(
		max_digits=7,
		decimal_places=2,
	)
	semester = models.ForeignKey(
		'Semester',
		on_delete=models.CASCADE
	)
	def __str__(self):
		return "%s - %s (%s)" % (self.start_date, self.end_date, self.semester)

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
	season = models.CharField(
		max_length=1,
		choices=SEASON_CHOICES,
		default=WISE
	)
	year = models.DecimalField(
		max_digits=2,
		decimal_places=0,
	)
	budget = models.DecimalField(max_digits=7, decimal_places=2)
	def __str__(self):
		if (self.season == 'W'):
			return _('Winter term 20%d/%d') % (self.year, self.year+1)
		else:
			return _('Summer term 20%d') % (self.year)

# A module (e.g. Readings, Exercises, ...)
class TucanModule(models.Model):
	module_id = models.CharField(
		max_length=13,
		unique=True,
	)
	name = models.CharField(max_length=128)
	last_offered = models.ForeignKey(
		'Semester',
		on_delete=models.CASCADE
	)
	literature = models.ManyToManyField('Book')
	def __str__(self):
		return '%(name)s [%(module_id)s]' % {'name': self.name, 'module_id': self.module_id}
