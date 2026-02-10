FROM python:3.11-slim

WORKDIR /nexus

# RUN apt-get update && \
#     apt-get install -y gcc libpq-dev curl && \
#     rm -rf /var/lib/apt/lists/*


COPY requirements.txt /nexus/
RUN pip install -r requirements.txt

COPY . /nexus/ 

# RUN python3 manage.py collectstatic --noinput

EXPOSE 8000


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

#RUNNING GUNICORN