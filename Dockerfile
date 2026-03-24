FROM python:3.11

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y ffmpeg ca-certificates

# Çalışma dizini
WORKDIR /app

# Requirements yükleme
COPY requirements.txt .
RUN pip install -r requirements.txt

# Kodları kopyala
COPY . .

# Başlat
CMD ["python", "main.py"]
