# Group Account




## Account Management [/account]

**Notice:** An account is bound to the currently logged in user. Therefore these operations may not return the same data for different users.



### Retrieve Account [GET /account]

**Functionality:** Retrieves the current account.

**Security:** Requires an authenticated user.


+ Response 200 (application/json; charset=utf-8)

    + Attributes
        + account (required, account)

    + Body


+ Response 401

    **Send if:** The user is not authenticated.

    + Body


+ Response 403

    **Send if:** The user does not have the required permissions.

    + Body



### Modify Account [PATCH /account]

**Functionality:** Changes the given properties of the current account.

**Security:** Requires an authenticated user.


+ Request (application/json)
    + Attributes
        + account (required)
            <!-- TODO: To be updated. -->


+ Response 200 (application/json; charset=utf-8)

    + Attributes
        + account (required, account)

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



### Delete Account Data [DELETE /account]

**Functionality:** Deletes the data of the current account.

**Security:** Requires an authenticated user.


+ Response 204 (application/json; charset=utf-8)

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



### Retrieve Orders [GET /account/orders{?page,limit,status,orderBy}]

**Functionality:** Retrieves the orders of the current account matching the given criteria.

**Security:** Requires an authenticated user.


+ Parameters
    + page: `1` (optional, number) - pagination - The page to return. Defaults to `1`.
    + limit: `10` (optional, number) - pagination - The number of items per page. Defaults to `10`.
    + status: `OD` (optional, enum[string]) - A comma-separated list of states to filter for.
        + `PD` Pending
        + `OD` Ordered
        + `RJ` Rejected
        + `AR` Arrived
    + orderBy: `status` (optional, enum[string]) - The field to order by. Defaults to no specific order.
        + `status` Order by the status.
        + `timeframe` Order by the timeframe.


+ Response 200 (application/json; charset=utf-8)

    + Attributes
        + orders (required, array[order])
        + total: `10` (required, number)

    + Body


+ Response 400

    **Send if:** Wrong parameters where sent from the user.

    + Body


+ Response 401

    **Send if:** The user is not authenticated.

    + Body


+ Response 403

    **Send if:** The user does not have the required permissions.

    + Body
