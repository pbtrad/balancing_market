FROM python:3.11

WORKDIR /app

ENV TMPDIR=/app/tmp
RUN mkdir -p $TMPDIR

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["bash"]
