# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/
# Use an official Python runtime as a parent image
FROM mglue/content-similarity-base:v1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
#COPY requirements.txt .

# Install Python dependencies
#RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python project files into the container
COPY . /app

# Define the command to run your Python application
CMD ["python", "all-time.py"]
