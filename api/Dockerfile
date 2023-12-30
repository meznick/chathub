FROM python:3.11-slim

# Set environment variables.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory.
WORKDIR /code

# Install dependencies.
COPY server/requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project.
COPY server/api.py /code/api.py

# Expose the port the app runs on. Maybe set exposed port with param
EXPOSE 8000

# define the default command to run when starting a container
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
