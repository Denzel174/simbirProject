FROM python:3.9-slim
WORKDIR /denproject
COPY . /denproject
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "main.py"]

