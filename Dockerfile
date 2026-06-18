FROM python:3.11-slim

RUN useradd -m -u 1000 appuser							  
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 


RUN mkdir -p /apps/datacom/app/

RUN chown -R appuser:appuser /apps/datacom/app/

USER appuser

EXPOSE 8001

CMD ["streamlit", "run", "ui.py", "--server.port", "8001", "--server.address", "0.0.0.0"]