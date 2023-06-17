FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/root/.local/bin:$PATH"

# Install Make
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*


    # Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

RUN export PATH="/root/.local/bin:$PATH"


# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY . /app

# Installing dependencies
RUN make build
