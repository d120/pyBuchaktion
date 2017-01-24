## Book

| Attribute   | Type        | Classifier | Description                               | Example                                               |
|-------------|-------------|------------|-------------------------------------------|-------------------------------------------------------|
| id          | number      | required   | The ID of the module.                     | `3234`                                                |
| cid         | tucanid     | required   | The course ID of TUCaN.                   | `20-00-0004-iv`                                       |
| name        | string      | required   | The name of the course.                   | `Functional and Object-oriented Programming Concepts` |
| lastOffered | season      | required   | The season this course was last offered.  | See `Season`.                                         |
| literature  | array[book] | required   | The recommened literature of this course. | \[ See `Book`. \]                                     |
