FROM python:3.11-slim-bookworm
ENV PIP_NO_CACHE_DIR=1
WORKDIR /bot
COPY requirements.txt /bot
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]

#docker build -t logoped_polina_bogdan_bot:v0.1 . && docker run -d -e API_TOKEN= --name logoped_polina_bogdan_bot --restart=unless-stopped -v ./:/bot logoped_polina_bogdan_bot:v0.1



        location /grafana/ {
            proxy_pass http://grafana/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Переписываем пути и редиректы в HTML и заголовках
            sub_filter_once off;
            sub_filter_types *;
            sub_filter 'href="/' 'href="/grafana/';
            sub_filter 'src="/' 'src="/grafana/';
            sub_filter 'action="/' 'action="/grafana/';
            sub_filter 'content="/' 'content="/grafana/';
            sub_filter 'url("/' 'url("/grafana/';
            sub_filter 'window.location="/' 'window.location="/grafana/';
            sub_filter 'location="/' 'location="/grafana/';
            sub_filter 'refresh:0;url=/' 'refresh:0;url=/grafana/';

            # Переписываем заголовки редиректа
            proxy_redirect default;
            proxy_redirect / /grafana/;

            # Обработка веб-сокетов
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }