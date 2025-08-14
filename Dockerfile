FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and wkhtmltopdf
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        curl \
        wget \
        gnupg \
        xfonts-base \
        xfonts-75dpi \
        libfontconfig1 \
        wkhtmltopdf && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Google Cloud SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
      | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
      | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && apt-get install -y google-cloud-sdk && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY main.py .

EXPOSE 8080
CMD ["python3", "main.py"]
