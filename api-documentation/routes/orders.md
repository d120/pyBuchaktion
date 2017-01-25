# Group Orders




## Multiple Orders [/orders]



### Retrieve Orders [GET /orders{?page,limit,userId,status,orderBy}]

**Functionality:** Retrieves all orders that are visible to the current user (that is, only the orders of the logged in user or all orders if the logged in user as the role `admin`).

**Security:** Requires an authenticated user.


+ Parameters
    + page: `1` (optional, number) - pagination - The page to return. Defaults to `1`.
    + limit: `10` (optional, number) - pagination - The number of items per page. Defaults to `10`.
    + userId: `1987` (optional, number) - A comma-separated list of user IDs to filter for. This property does not have any functionality if the current user does not have the role `admin`.
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




## Specific Order [/orders/{orderId}]

+ Parameters
    + orderId: `5862` (required, number) - The ID of the order.



### Modify Order [PATCH /orders/{orderId}]

**Functionality:** Changes the given properties of the specified order.

**Security:** Requires an authenticated user with the role `admin`.


+ Parameters
    + orderId: `5862` (required, number) - The ID of the order.


+ Request (application/json)
    + Attributes
        + order (required)
            + status: `OD` (optional, enum[string])
                + `PD` Pending
                + `OD` Ordered
                + `RJ` Rejected
                + `AR` Arrived
            + hint: `Enough books available.` (optional, string)


+ Response 200 (application/json; charset=utf-8)

    + Attributes
        + order (required, order)

    + Body


+ Response 401

    **Send if:** The user is not authenticated.

    + Body


+ Response 403

    **Send if:** The user does not have the required permissions.

    + Body


+ Response 404

    **Send if:** The specified order was not found.

    + Body


+ Response 422

    **Send if:** The given item cannot be processed (e.g. if it is invalid).

    + Body



### Delete Order [DELETE /orders/{orderId}]

**Functionality:** Deletes the specified order.

**Security:** Requires an authenticated user with the role `admin` or the user who has created the order.


+ Parameters
    + orderId: `5862` (required, number) - The ID of the order.


+ Response 204 (application/json; charset=utf-8)

    + Body


+ Response 401

    **Send if:** The user is not authenticated.

    + Body


+ Response 403

    **Send if:** The user does not have the required permissions.

    + Body


+ Response 404

    **Send if:** The specified order was not found.

    + Body
