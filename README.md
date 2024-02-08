# Setup

To install dependencies for docs generator, first build the docker image as follows:

`docker build -t docs-gen docs-gen`

Then you can use the docker image to run the crawler as follows:

`python -m docs_gen.crawler.crawler`

Or you can use the docker image to run the openai chat completion as follows:

`python -m docs_gen.open_ai.open_ai`
