FROM python:3.9-slim

COPY . /app

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the app and all necessary files
COPY . .

# Expose the required port
EXPOSE 5009

# Run the application
CMD ["python", "app.py"]

