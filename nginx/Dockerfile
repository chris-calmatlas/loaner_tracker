FROM nginx:1.30.4-trixie
RUN rm /etc/nginx/conf.d/default.conf
COPY loaner_tracker.conf /etc/nginx/conf.d/loaner_tracker.conf

# Make a self signed cert
RUN mkdir -p /etc/nginx/ssl/ \
    && openssl req -x509 -subj "/C=US/ST=Denial/L=Nowhere/O=Dis" -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.cert

RUN mkdir -p /var/www/html
