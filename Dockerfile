# Use the official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (git) and clean up unnecessary files
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --upgrade pip && \
    pip install fellow-aiden streamlit openai

# Clone the GitHub repository containing brew_studio.py
RUN git clone https://github.com/9b/fellow-aiden.git /app/fellow-aiden

# Change directory to the cloned repo
WORKDIR /app/fellow-aiden/brew_studio

# Use environment variable for port (set via Docker Compose or .env)
CMD sh -c "streamlit run brew_studio.py --server.port=$(echo $PORT) --server.address=0.0.0.0"