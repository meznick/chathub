FROM python:3.11-slim

ARG PORT=8080

# Set environment variables.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory.
WORKDIR /code

# Install dependencies.
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt \
    --extra-index-url http://10.132.179.1:8228/simple/ --trusted-host 10.132.179.1

# Copy project.
COPY /*.py ./

# Expose the port the app runs on. Maybe set exposed port with param
EXPOSE $PORT

# define the default command to run when starting a container
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8888"]
