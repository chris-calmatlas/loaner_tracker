FROM python:3.14.7-trixie
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x ./run_prod.sh
RUN chmod +x ./run_dev.sh
CMD [ "bash", "-c", "'/usr/src/app/run_prod.sh'" ]
