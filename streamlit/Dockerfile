# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY ./requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application's code
COPY ./app.py .

# Expose port 8501 for the Streamlit app
EXPOSE 8501

# Command to run the Streamlit application
# --server.port=8501 specifies the port
# --server.address=0.0.0.0 makes the app accessible from outside the container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
