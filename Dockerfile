# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which your Python app runs (replace 8000 with your app's port if needed)
EXPOSE 5000

# Define the command to run your Python app (replace "app.py" with your app's main file)
CMD ["python", "app.py"]