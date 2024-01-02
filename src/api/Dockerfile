FROM python:3.11-slim

ARG PORT=8080

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
EXPOSE $PORT

# todo: переписать докерфайл, он теперь не работает из-за изменения структуры файлов
# define the default command to run when starting a container
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
