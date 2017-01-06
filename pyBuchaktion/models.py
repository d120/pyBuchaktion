from django.db import models

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
		(ACCEPTED, 'Accepted'),
		(REJECTED, 'Rejected'),
		(PROPOSED, 'Proposed'),
		(OBSOLETE, 'Obsolete'),
	)
	state = models.CharField(
		max_length=2,
		choices=STATE_CHOICES,
		default=ACCEPTED,
	)
	#alternative
	author = models.CharField(max_length=64)
	price = models.DecimalField(max_digits=6, decimal_places=2)

# An order that a particular student has posted
class Order(models.Model):
	PENDING='PD'
	ORDERED='OD'
	REJECTED='RJ'
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
	hint = models.CharField(max_length=42)
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

# A student participating in the Buchaktion
class Student(models.Model):
	tu_id = models.CharField(
		max_length=8,
		unique=True,
	)
	email = models.CharField(max_length=64)
	name = models.CharField(max_length=42)

# A Timeframe for a set of orders
class OrderTimeframe(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()
	spendings = models.DecimalField(max_digits=7, decimal_places=2)
	semester = models.ForeignKey(
		'Semester',
		on_delete=models.CASCADE
	)

# A semester containing a budget
class Semester(models.Model):
	name = models.CharField(
		max_length=25,
		unique=True
	)
	budget = models.DecimalField(max_digits=7, decimal_places=2)

# A module (Reading & Exercises)
class Module(models.Model):
	module_id = models.CharField(
		max_length=13,
		unique=True,
	)
	name = models.CharField(max_length=42)
	last_offered = models.ForeignKey(
		'Semester',
		on_delete=models.CASCADE
	)
	literature = models.ManyToManyField('Book')
