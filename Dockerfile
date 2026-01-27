FROM --platform=$TARGETPLATFORM python:3.13

## Port
# api
EXPOSE 8000
# metrics
EXPOSE 8100

WORKDIR /dingtalk_bot

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

ADD requirements.txt /dingtalk_bot/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY server_config/supervisord.conf /etc/supervisord.conf

ADD . /dingtalk_bot/

CMD supervisord