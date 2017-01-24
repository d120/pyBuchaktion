# Group Books




## Multiple Books [/books]



### Retrieve Books [GET /books{?page,limit,isbn,title,state,author,orderBy}]

**Functionality:** Retrieves all books matching the given criteria.


+ Parameters
    + page: `1` (optional, number) - pagination - The page to return. Defaults to `1`.
    + limit: `10` (optional, number) - pagination - The number of items per page. Defaults to `10`.
    + isbn: `9783836218023` (optional, isbn) - The ISBN to filter for.
    + title: `Java ist auch eine Insel` (optional, string) - The title to filter for. Represents a text search.
    + state: `AC` (optional, enum[string]) - The state to filter for.
        + `AC` Accepted
        + `RJ` Rejected
        + `PP` Proposed
        + `OL` Obsolete
    + author: `Christian Ullenboom` (optional, string) - The author to filter for. Represents a text search.
    + orderBy: `author` (optional, enum[string]) - The field to order by. Defaults to no specific order.
        + `isbn` Order by the ISBN.
        + `title` Order by the title.
        + `state` Order by the state.
        + `author` Order by the author.


+ Response 200 (application/json; charset=utf-8)

    + Attributes
        + books (required, array[book])

    + Body


+ Response 400

    **Send if:** Wrong parameters where sent from the user.

    + Body



### Propose Book [PUT /books]

**Functionality:** Proposes a new book that has to be approved by an administrator. If this endpoint.

**Security:** Requires an authenticated user.


+ Request Create by ISBN (application/json)
    + Attributes
        + book (required)
            + isbn: `9783836218023` (optional, isbn)


+ Request Create by Author/Title (application/json)
    + Attributes
        + book (required)
            + title: `Java ist auch eine Insel` (optional, string)
            + author: `Christian Ullenboom` (optional, string)


+ Response 201 (application/json; charset=utf-8)

    **Send if:** The book was created an accepted (this is only possible if the proposal was sent by an administrator).

    + Attributes
        + book (required, book)

    + Body


+ Response 202 (application/json; charset=utf-8)

    **Send if:** The book was created and is waiting for approval.

    + Attributes
        + book (required, book)

    + Body


+ Response 401

    **Send if:** The user is not authenticated.

    + Body


+ Response 403

    **Send if:** The user does not have the required permissions.

    + Body


+ Response 404

    **Send if:** The given book was not found.

    + Body


+ Response 409

    **Send if:** The book already exists.

    + Body


+ Response 422

    **Send if:** The given item cannot be processed (e.g. if it is invalid).

    + Body




## Specific Book [/books/{bookId}]

+ Parameters
    + bookId: `2444` (required, number) - The ID of the book.



### Retrieve Book [GET /books/{bookId}]

**Functionality:** Retrieves the specified book.


+ Parameters
    + bookId: `2444` (required, number) - The ID of the book.


+ Response 200 (application/json; charset=utf-8)

    + Attributes
        + book (required, book)

    + Body


+ Response 404

    **Send if:** The specified book is not available.

    + Body



### Modify Book [PATCH /books/{bookId}]

**Functionality:** Changes the given properties of the specified book.

**Security:** Requires an authenticated user with the role `admin`.


+ Parameters
    + bookId: `2444` (required, number) - The ID of the book.


+ Request (application/json)
    + Attributes
        + isbn: `9783836218023` (optional, isbn)
        + title: `Java ist auch eine Insel` (optional, string)
        + state: `AC` (optional, enum[string])
            + `AC` Accepted
            + `RJ` Rejected
            + `PP` Proposed
            + `OL` Obsolete
        + author: `Christian Ullenboom` (optional, string)
        + price: `49.90` (optional, number)


+ Response 200 (application/json; charset=utf-8)

    + Attributes
        + book (required, book)

    + Body


+ Response 401

    **Send if:** The user is not authenticated.

    + Body


+ Response 403

    **Send if:** The user does not have the required permissions.

    + Body


+ Response 404

    **Send if:** The specified book is not available.

    + Body


+ Response 422

    **Send if:** The given item cannot be processed (e.g. if it is invalid).

    + Body



### Delete Book [DELETE /books/{bookId}]

**Functionality:** Deletes the specified book.

**Security:** Requires an authenticated user with the role `admin`.


+ Parameters
    + bookId: `2444` (required, number) - The ID of the book.


+ Response 200 (application/json; charset=utf-8)

    + Body


+ Response 401

    **Send if:** The user is not authenticated.

    + Body


+ Response 403

    **Send if:** The user does not have the required permissions.

    + Body


+ Response 422

    **Send if:** The given item cannot be processed (e.g. if it is invalid).

    + Body
