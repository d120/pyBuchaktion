# Group GROUP




## SECTION [PATH]



### OPERATION_TITLE [METHOD PATH]

**Functionality:** N/A

**Notice:** N/A

**Security:** Requires an authenticated user.
**Security:** Requires an authenticated user with the role `admin`.


+ Parameters
    + PARAMETER: `EXAMPLE` (optional,required, TYPE) - DESCRIPTION


+ Request (application/json)
    + Attributes
        + ATTRIBUTE (optional,required, TYPE)


+ Response CODE (application/json; charset=utf-8)

    **Send if:** SEND_IF

    + Attributes
        + ATTRIBUTE (optional,required, TYPE)

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


+ Response 422

    **Send if:** The given item cannot be processed (e.g. if it is invalid).

    + Body



### next operation
## next section
# next group
