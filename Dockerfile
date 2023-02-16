FROM nginx:1.23.3-alpine-slim

COPY ./ /usr/share/nginx/html

EXPOSE 80

# COPY ./ /usr/local/apache2/htdocs/