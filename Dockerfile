FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \ 
    build-essential \ 
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
CMD bash -lc 'streamlit run run_chat.py --server.port ${PORT:-8080} --server.address 0.0.0.0 --server.enableCORS false --server.headless true'
