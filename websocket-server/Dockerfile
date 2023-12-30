FROM python:3.11-slim

ARG PORT=8080

# Set the working directory in the Docker image
WORKDIR /code

# Copy requirements.txt into the image
#COPY requirements.txt ./

# Install the dependencies present in requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application code into the Docker image
COPY . .

# Expose the port that your app runs on
EXPOSE $PORT

# Start the server
CMD [ "python", "server.py" ]
