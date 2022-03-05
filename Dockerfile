FROM python:3.8

WORKDIR /app

ENV STREAMLIT_SERVER_PORT=80

COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 80
CMD ["streamlit", "run", "app.py"]
