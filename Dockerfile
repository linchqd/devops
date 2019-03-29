FROM 192.168.0.11/library/python3-uwsgi-nginx:base

LABEL maintainer="linchqd<13435600095@163.com>"

COPY . /home/docker/code/app/

RUN pip3 install -r /home/docker/code/app/requirements.txt \
	&& mv /home/docker/code/app/nginx-app.conf /etc/nginx/sites-available/default \
	&& mv /home/docker/code/app/supervisor-app.conf /etc/supervisor/conf.d/ \
	&& mv /home/docker/code/app/uwsgi.ini /home/docker/code/uwsgi.ini \
	&& mv /home/docker/code/app/uwsgi_params /home/docker/code/uwsgi_params \
	&& sed -i '39,43s/^/#/g' /home/docker/code/app/devops/settings.py \
	&& sed -i '22,27s/^/#/g' /home/docker/code/app/devops/urls.py \
	&& python3 /home/docker/code/app/manage.py migrate \
	&& sed -i '39,43s/^#//g' /home/docker/code/app/devops/settings.py \
	&& sed -i '22,27s/^#//g' /home/docker/code/app/devops/urls.py \
	&& python3 /home/docker/code/app/manage.py makemigrations dashboard accounts resources monitor work_order \
        && python3 /home/docker/code/app/manage.py migrate

CMD ["supervisord", "-n"]
