# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /code

# Copy the dependencies file to the working directory
COPY ./requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache, which reduces the image size
# --upgrade: Ensures the latest versions of packages are installed
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application's code
COPY ./main.py .
COPY ./app ./app

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"]
