# Loom

Loom is the backend of InkWeaver, produced by [Plotypus](plotypus.github.io).

## Installation

These steps explain the installation procedure for the Loom backend of InkWeaver.

### Requirements

* Python 3.6+
* MongoDB 3.2+

Additionally, the following Python libraries are installed by following the steps in the next section:

* `decorator` -- 4.0.10
* `motor` -- 1.0
* `nltk` -- 3.2.2
* `passlib` -- 1.7.0
* `pytest` -- 3.0.5
* `pytest-asyncio` -- 0.5.0
* `pytest-cov` -- 2.4.0
* `python-coveralls` -- 2.9.0
* `tornado` -- 4.4.1

### Step-by-Step Instructions

These instructions assume some familiarity with terminal-based navigation. It is also assumed that your Python 3 binary
is named `python` and that your PIP binary is named `pip`.

First, clone the git repository and move inside of it.

```
$ git clone https://github.com/Plotypus/loom.git
$ cd loom
```

Next, we'll install the Python libraries. We make this easy to do by putting them all in a single file. Install them
with:

```
$ pip install -r requirements.txt
```

Now, assuming your Mongo server is already running, load up one of our demo files. For this example, we use some
information about HBO's "Game of Thrones" TV series, sourced from Wikipedia.

```
$ python ./scripts/create_test_data.py scripts/game_of_thrones.json --no-ask
```

Lastly, we can start the Loom server:

```
$ python server.py --config example_config.conf
```

Now you should be good to go! Loom will be running and ready to accept connections from the InkWeaver fron-end.

Happy writing!
