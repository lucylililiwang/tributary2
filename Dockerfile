FROM python:3.11
COPY ./requirements.txt .
RUN pip install -r requirements.txt
CMD ["gunicorn", "entrypoint:app"]
COPY ./entrypoint.py .