FROM python:latest
WORKDIR /bot
COPY requirements.txt /bot
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]

#docker build -t logoped_polina_bogdan_bot:v0.1 . && docker run -d -e API_TOKEN=6092736622:AAE-M9nWHVkY5_8qgWAkhOpCd0rB6g9YCak --name logoped_polina_bogdan_bot --restart=unless-stopped -v /home/mix/PycharmProjects/Koit.VPS/Logoped_Polina_Bogdan_bot:/bot logoped_polina_bogdan_bot:latest