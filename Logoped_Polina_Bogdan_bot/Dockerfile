FROM python:3.11-slim-bookworm
ENV PIP_NO_CACHE_DIR=1
WORKDIR /bot
COPY requirements.txt /bot
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]

#docker build -t logoped_polina_bogdan_bot:v0.1 . && docker run -d -e API_TOKEN= --name logoped_polina_bogdan_bot --restart=unless-stopped -v ./:/bot logoped_polina_bogdan_bot:v0.1