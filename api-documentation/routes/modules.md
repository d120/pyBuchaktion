# Group Modules




## Multiple Modules [/modules]



### Retrieve Modules [GET /modules{?page,limit,cid,name}]

**Functionality:** Retrieves all modules matching the given criteria.


+ Parameters
    + page: `1` (optional, number) - pagination - The page to return. Defaults to `1`.
    + limit: `10` (optional, number) - pagination - The number of items per page. Defaults to `10`.
    + cid: `20-00-0004-iv` (optional, tucanid) - A comma-separated list of TUCaN course IDs to filter for.
    + name: `programming` (optional, string) - The course name to filter for. Represents a case-insensitive text search.


+ Response 200 (application/json; charset=utf-8)

    + Attributes
        + modules (required, array[modulereduced])
        + total (required, number)

    + Body


+ Response 400

    **Send if:** Wrong parameters where sent from the user.

    + Body



### Create Module [PUT /modules]

**Functionality:** Creates a new module.

**Security:** Requires an authenticated user with the role `admin`.


+ Request (application/json)
    + Attributes
        + module (required)
            + cid: `20-00-0004-iv` (required, tucanid)
            + name: `Functional and Object-oriented Programming Concepts` (required, string)
            + lastOffered (required, season)
            + literature (optional, array[string]) - The IDs of the proposed books.


+ Response 201 (application/json; charset=utf-8)

    + Attributes
        + module (required, module)

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




## Specific Moudle [/modules/{moduleId}]

+ Parameters
    + moduleId: `3234` (required, number) - The ID of the module.



### Retrieve Module [GET /modules/{moduleId}]

**Functionality:** Retrieves the specified module.


+ Parameters
    + moduleId: `3234` (required, number) - The ID of the module.


+ Response 200 (application/json; charset=utf-8)

    + Attributes
        + module (required, module)

    + Body


+ Response 404

    **Send if:** The specified module was not found.

    + Body



### Modify Module [PATCH /modules/{moduleId}]

**Functionality:** Changes the given properties of the specified module.

**Security:** Requires an authenticated user with the role `admin`.


+ Parameters
    + moduleId: `3234` (required, number) - The ID of the module.


+ Request (application/json)
    + Attributes
        + module (required)
            + cid: `20-00-0004-iv` (optional, tucanid)
            + name: `Functional and Object-oriented Programming Concepts` (optional, string)
            + lastOffered (optional, season)
            + literature (optional, array[string]) - The IDs of the proposed books.


+ Response 200 (application/json; charset=utf-8)

    + Attributes
        + module (required, module)

    + Body


+ Response 401

    **Send if:** The user is not authenticated.

    + Body


+ Response 403

    **Send if:** The user does not have the required permissions.

    + Body


+ Response 404

    **Send if:** The specified module was not found.

    + Body


+ Response 422

    **Send if:** The given item cannot be processed (e.g. if it is invalid).

    + Body



### Delete Module [DELETE /modules/{moduleId}]

**Functionality:** Deletes the specified module.

**Security:** Requires an authenticated user with the role `admin`.


+ Parameters
    + moduleId: `3234` (required, number) - The ID of the module.


+ Response 204 (application/json; charset=utf-8)

    + Body


+ Response 401

    **Send if:** The user is not authenticated.

    + Body


+ Response 403

    **Send if:** The user does not have the required permissions.

    + Body


+ Response 404

    **Send if:** The specified module was not found.

    + Body


+ Response 422

    **Send if:** The given item cannot be processed (e.g. if it is invalid).

    + Body
