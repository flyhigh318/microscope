FROM python:3.8.6-alpine
LABEL maintainer="rongwen.tang"
RUN  addgroup micro \
     && adduser -D -h /microscope micro -G micro  \
     && su - micro -c "mkdir -p /microscope/monitor" 
COPY --chown=micro:micro requirements.txt .
RUN  apk add -U tzdata \
     && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
     && apk add --no-cache mariadb-dev build-base \
     && pip install -r requirements.txt \
     && rm -rf /var/cache/apk* 
USER  micro
WORKDIR /microscope/monitor
COPY --chown=micro:micro . .
EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
