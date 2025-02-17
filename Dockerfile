FROM python:3.13

WORKDIR /dingtalk_bot

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple


ADD requirements.txt /dingtalk_bot/requirements.txt

RUN pip install -r requirements.txt

ADD . /dingtalk_bot/

CMD bash -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"