## Order

| Attribute | Type         | Classifier   | Description                                                                                                              | Example                   |
|-----------|--------------|--------------|--------------------------------------------------------------------------------------------------------------------------|---------------------------|
| id        | number       | required     | The ID of the order.                                                                                                     | `5862`                    |
| status    | enum[string] | semi-secured | The status of the order.                                                                                                 | `AR`                      |
| hint      | string       | optional     | A hint text including extended information about the status.                                                             | `Enough books available.` |
| book      | book         | required     | The ordered book.                                                                                                        | See `Book`.               |
| student   | account      | required     | The student who has ordered the book.                                                                                    | See `Account`.            |
| timeframe | timeframe    | required     | The timeframe in which the book order can be changed/cancelled. At the end of the timeframe the order will be processed. | See `Timeframe`.          |
