FROM python:3.12-slim-bookworm

# Install make and other dependencies
RUN apt-get update && apt-get install -y \
    make \
    curl \
    && apt-get clean

# Install Poetry
ENV POETRY_VERSION=1.8.3
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock* /app/

# Install project dependencies
RUN make install

# Copy the rest of the application code
COPY . /app

# Command to run your application (customize as needed)
CMD ["make", "start"]
