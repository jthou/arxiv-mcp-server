# Use a Python base image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy all project files
COPY . .

# Install project dependencies using uv
RUN uv pip install --system --no-cache -e .

# Set the default entrypoint
ENTRYPOINT ["python", "-m", "arxiv_mcp_server"]