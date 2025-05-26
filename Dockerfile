# FROM python:3.8

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# RUN pip install --upgrade pip

# WORKDIR /code
# COPY requirements.txt ./
# RUN pip install -r requirements.txt
# COPY . .

# EXPOSE 8000
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Use the official Redis image as the base.
# Alpine is a lightweight Linux distribution, making the image smaller.
FROM redis:latest

# Expose the default Redis port.
# This informs Docker that the container listens on this port at runtime.
EXPOSE 6379

# The default command for this image is 'redis-server',
# so we don't explicitly need to specify CMD here unless we want to override it.
CMD ["redis-server"]