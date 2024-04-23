# Use an official Python runtime as a parent image
FROM mglue/content-similarity-base:v1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
#COPY ./data_3000/ /app/data_3000
#COPY ./data_today/ /app/data_today

# Install Python dependencies
#RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python project files into the container
#WORKDIR /app
COPY ./app/ /app

# Define the command to run your Python application
CMD ["python", "day.py"]
