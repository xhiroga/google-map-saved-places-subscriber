FROM mcr.microsoft.com/playwright:v1.17.1-focal

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install

COPY src ./src

CMD ["python", "src/main.py"]
