## Book

| Attribute | Type         | Classifier | Description              | Example                     |
|-----------|--------------|------------|--------------------------|-----------------------------|
| id        | number       | required   | The ID of the book.      | `2444`                      |
| isbn      | isbn         | required   | The status of the order. | `9783836218023`             |
| title     | string       | required   | The title of the book.   | `Java ist auch eine Insel.` |
| state     | enum[string] |            | The state of the book.   | `AC`                        |
| author    | string       | required   | The author of the book.  | `Christian Ullenboom`       |
| price     | number       |            | The price of the book.   | `49.90`                     |
