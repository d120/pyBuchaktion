# REST API Documentation

The REST API documentation is written in [API Blueprint][2] using [Aglio][1] for rendering the documentation into HTML.


## Setup

Setting up [Aglio][1] is pretty easy, you just have to install [NodeJS][3]/[NPM][4] and then run `npm install -g aglio`.


## Development

For developing on the API you may start the [Aglio][1] server using `aglio -i api-documentation.md -s` and access the server at `http://localhost:3000`. The page is automatically refreshed when files change.


## Compiling before Pushing

Please compile the documentation before pushing your changes using `aglio -i api-documentation.md -o api-documentation.html`.


## Documentation

You can find the specification of [API Blueprint][2] here: [Specification][5]

To get the most out of [API Blueprint][2], you have to use this [tool][6].



[1]: https://github.com/danielgtaylor/aglio
[2]: https://apiblueprint.org
[3]: https://nodejs.org
[4]: https://www.npmjs.com
[5]: https://github.com/apiaryio/api-blueprint/blob/master/API%20Blueprint%20Specification.md
[6]: https://www.google.com
