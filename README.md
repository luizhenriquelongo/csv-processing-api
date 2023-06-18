# CSV Processing API

This api receives a CSV file of the following format as its input,
processes it and generates the output CSV file. The goal here is to generate the output file with the `Total Number of Plays for Date` for each song and date combination.

# Contents

- [Made With](#made-with)
- [Architecture](#architecture-overview)
- [Installation](#installation)
- [Usage](#usage)
- [Findings & Decisions](#findings--decisions)
- [Tests](#tests)
- [TODOs](#todos)


## Made With
- Python
- Flask
- Pandas
- Polars
- Celery
- MongoDB
- RabbitMQ

## Architecture Overview

The goal of this architecture is to be able to process csv files asynchronously noticing that the uploaded and the result files
may be larger than the available memory in the server.

_**Important:** Did not spend much time on configuration of componentes other than the flask application and the celery worker, all other components are just a "plug and play" docker-compose version with basic to none security at all. This is not intended to be production ready (despite the python code) environment._

### Components
- **Flask API**: The actual web server.
- **Local Storage**: The storage inside the web server.
- **MongoDB**: The database that holds all the information about all tasks created so far.
- **RabbitMQ**: The message broker used to enable the async comunication between celery and flask.
- **Celery Worker**: The worker that will process the files asynchronously.
- **Celery Beat**: Will schedule a task for every 30 seconds to clean up the files in the local storage.

### Sequence Diagram of the relevant endpoint
![sequence_diagram.png](docs/sequence_diagram.png)

**NOTE:** The process of saving/appending each group data to a group file,
and appending the results from each group file to the result file are made using multithreading,
so they are not strictly a for loop which processes one item at a time.

## Installation
### Requirements
- [Docker](https://docs.docker.com/get-docker/)
- [docker-compose](https://docs.docker.com/compose/install/)
- `.env`: The application relly on a few environment variables (you could find in `.env.example`).
Make a copy of this file making sure that the file name is `.env` and change it as needed. _It will
work if you use the values in the `.env.example` file but is not recomended._

### Command
Go to the project folder directory and run:
```bash
docker-compose up --build
```

## Usage
After all containers are up and running, you can access the endpoints documentation in the following url:
> http://127.0.0.1:5002/api/v1/docs/swagger


## Findings & Decisions
Processing larger datasets can be challenging and understanding the frameworks that "solve" this problem can be even more.
My first approach would be to stream open the file using python's built-in `csv` module, but this could be overwhelming since
this would lead to a lot of python code to manipulate the data, generating chunks of lines and so on.

By searching for a framework that could also address this problem, you will find `pandas`, `polars`, `Dask`
, `DuckDB`, `Vaex`, etc. I tried a few of these to came up with this solution.

My first try was `pandas`, but I run into the `pandas` main issue fairly quick, which is the memory.
`pandas` need to have the whole dataframe in the memory to process it
(of course you can open the file in chunks and then do the processing with chunks,
but since I had to calculate all the times played for each song/date combination,
this would require a different approach), and also `pandas` is single threaded, meaning that it
cannot leverage multiple cores in a machine or cluster.

`Dask` was my second try since it has the ability to work in a distributed environment and use the
_lazy_ approach to dataframes where all the computing are done lazily, only when the results are
actually required. This allows the framework to create a computing graph with the tasks that it
needs to perform and optimize those graphs to have a better performance. The problem with `dask`
is that it was built on top of `pandas`, even though it is considerably faster than `pandas`
(due to its distributed approach and the "try" to use multiple threads since a `dask` dataframe
is made of multiple smalled `pandas` dataframes, so the framework tries to do some multi-threading.)
One of the requirements of this project is that the **input** and the **output** files may be
larger than memory, the problem wasn't the input file, because `dask` do not load the entire
file in the memory at once (like `pandas`) due to its lazy evaluation. The problem started when
trying to save the results to a new `.csv` file, `dask` will need to `compute()` to execute the
computation graphs and gather the results. By calling `compute()` the result dataframe will be loaded
entirely into memory and that may raise Out Of Memory error. `dask` actually have a solution for this,
it involves distributed computing relying on multiple machines running in a cluster (Too much for us right now).

My last resort was `polars`. Yes, it is indeed "blazing fast" like the docs says. `polars` was built
from the ground up using `Rust` so it's multithreaded by default and also apply lazy evaluation on
the dataset. So it also will create computational graphs first, optimize as much as possible the graphs
and only evaluate the results once required. `Polars` could solve the problem with just about less than
10 lines of code **IF** we were not working with `.csv` files. `polars` has a method that can save the results
to `parquet` or `Feather` formats in the disk even if the results are larger than the memory, those methods
relly on streaming the results to a file and I tested it with 10+Gb files on containers limited
to 1Gb of memory, never run into any issue. Since the requirement is that the end user will have access
to a `.csv` file, could not use that approach.

Here is the final decision, the same old thing talked for a long time to everyone:
> "Split the big problem into smaller and more manageble problems"

This is what I came up with:
1. **Open the `.csv` file in chunks using `pandas`:** by doing that, we do not have to care about the
total file size. `polars` have a similar API called `read_csv_batched()` but in my tests, `pandas` did a better job on chunking files since the `polars` method is not lazy evaluated.
2. **Convert each `pandas` chunk dataframe into `polars` dataframe:** As mentioned before, `polars` is significantly faster than `pandas` on processing data, so we will use that in our favour.
3. **Partitioning the chunk:** `polars` has a `partition_by` method were it can group data into
partitions, so we partitioned the chunk using the song name, each partition will contain the only one song and the other information of that song like "Date" and "Number of Plays".
4. **Save/Append each partition data:** With the partitions containing only information about one song each,
now we can save it into a new `.csv` file, or append to an existing file related to that song (a variable containing the `seen_groups` is initialized in the beggining of this process to control wheter the file for the group already exists)
5. **Create a result file empty and add the headers `Song,Date,Total Number of Plays for Date`**.
6. **Process all the smaller files**: All the smaller file would be saved into a directory named after the `task_id`,
by going into that directory, we process each file by loading it lazily with `polars`, doing the grouping
by "Song" and "Date", and summing the "Number Of Plays". With that we will have a dataframe with just one row
for each song/date combination, so we can append it to the result file.

With this approach we won't have problem regarding the file sizes and memory. The bottleneck here is the
smaller temporary files for the songs, if those files are larger than memory, we would have a problem. To improve that capacity,
we could partition the chunks not only by song, but by song/date combination, which would result in even smaller
files. The problem with this is the overhead of having a very large number of files that needs to be opened and appended.(I tested this as well
, and it has a massive impact in the overall performance, it does the job, but for the file, it went
from 53 seconds to 376 seconds of processing time).

For even worst cases, I think solution like `dask` or `spark` would be better due to the whole clustering thing.
We are not talking here about processing thousands of huge files in only one computer,
that would be insane.


## Tests
The main application container and the celery worker are set to work with only 1Gb of RAM, so you can try it with files larger than this to check if everything is running fine.

Inside the `tests/` folder you will find a `script.py` file, use this module to create large csv files to be processed by the application. The output file will live in `/tests/static/`.
So with this you can create larger `.csv` files to load test the application.

## TODOs

- Testing, testing, testing: I have wroted just a small amount of tests due to time constraints.
- Improve API documentation.
- Improve components configuration (e.g. mongo, rabbitmq, celery)
