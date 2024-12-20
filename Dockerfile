
FROM python:3.12

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install flask

COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host", "0.0.0.0"]  
