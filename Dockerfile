# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

COPY . /app

# Copy the requirements file into the container
# COPY req.txt .

# Install the required Python packages
RUN pip install -r req.txt

# Copy the entire application into the container
COPY . /app

# Expose port 5000 for the Flask application
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "run.py"]
