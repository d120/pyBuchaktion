# Data Structures

## date (string) YYYY-MM-DD
## isbn (string) ISBN-13
## tucanid (string) XX-XX-XXXX-XX

<!-- TODO: To be updated. -->
## account (object)
+ id: `0987` (required, number) - The ID of the account.

## book (object)
+ id: `2444` (required, number) - The ID of the book.
+ isbn: `9783836218023` (required, isbn) - The ISBN of the book.
+ title: `Java ist auch eine Insel` (required, string) - The title of the book.
+ state: `AC` (enum[string]) - secured - The state of the book.
    + `AC` Accepted
    + `RJ` Rejected
    + `PP` Proposed
    + `OL` Obsolete
+ author: `Christian Ullenboom` (required, string) - The author of the book.
+ price: `49.90` (number) - secured - The price of the book.

## order (object)
+ id: `5862` (required, number) - The ID of the order.
+ status: `AR` (enum[string]) - semi-secured - The status of the order.
    + `PD` Pending
    + `OD` Ordered
    + `RJ` Rejected
    + `AR` Arrived
+ hint: `Enough books available.` (optional, string) - A hint text including extended information about the status.
+ book (required, book) - The ordered book.
+ student (required, account) - The student who has ordered the book.
+ timeframe (required, timeframe) - The timeframe in which the book order can be changed/cancelled. At the end of the timeframe the order will be processed.

## module (object)
+ id: `3234` (required, number) - The ID of the module.
+ cid: `20-00-0004-iv` (required, tucanid) - The course ID of TUCaN.
+ name: `Functional and Object-oriented Programming Concepts` (required, string) - The name of the course.
+ lastOffered (required, season) - The season this course was last offered.
+ literature (required, array[book]) - The recommened literature of this course.

## modulereduced (object)
+ id: `3234` (required, number) - The ID of the module.
+ cid: `20-00-0004-iv` (required, tucanid) - The course ID of TUCaN.
+ name: `Functional and Object-oriented Programming Concepts` (required, string) - The name of the course.
+ lastOffered (required, season) - The season this course was last offered.

<!-- TODO: To be updated. -->
## season (object)
+ id: `2156` (required, number) - The ID of the season.
+ season: `W` (required, enum[string]) - The season.
    + `W` Winter term
    + `S` Summer term
+ year: `2017` (required, string) - The year of the season.

## timeframe (object)
+ from: `2017-02-01` (required, date) - The from-date of the timeframe (inclusive).
+ to: `2017-03-01` (required, date) - The to-date of the timeframe (inclusive).



# Group Data Structures

## Classifier Explanation

The 'Classifier' describes how an attribute has to be applied. The following classifiers are available and can be combined (with some exceptions):
- `optional` The attribute does not have to exit. Cannot be combined with `required`.
- `required` The attribute has to exist. Cannot be combined with `optional`.
- `secured` The attribute may only be read by administrators. Cannot be combined with `semi-secured`.
- `semi-secured` The attribute may only be read by administrators and users that are strongly coupled to the object. Cannot be combined with `secured`.
- `transient` The attribute is not stored and is calculated on demand by the server. Therefore it is not required to set this attribute when sending an object to the server.

If neither `optional` nor `required` are set either `secured` or `semi-secured` have to be set.

If either `secured` or `semi-secured` have been set, the following rules apply:
- If the user is not permitted to see the attribute it must not be available (really not set, not even `null` or `undefined`).
- If the user is permitted to see the attribute and neither `optional` nor `required` are set it must be available.
- If the user is permitted to see the attribute and either `optional` or `required` are set, these rules apply.

<!-- include(account.md) -->
<!-- include(basic.md) -->
<!-- include(book.md) -->
<!-- include(module.md) -->
<!-- include(order.md) -->
<!-- include(season.md) -->
<!-- include(timeframe.md) -->
