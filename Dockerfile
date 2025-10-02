# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Expose the port your application listens on (if it's a web app)
# Replace 8000 with the actual port your application uses
EXPOSE 8000

# Define the command to run your application
# Replace 'python app.py' with the command to start your application
CMD ["python", "main.py"]