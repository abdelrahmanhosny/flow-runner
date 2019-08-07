FROM centos:centos6

# Add OpenROAD flow tools
USER root
RUN yum install -y git tcl tk libjpeg libgomp libXext libSM libXft libffi cairo gettext
RUN yum install -y install centos-release-scl
RUN yum install -y rh-python36 gcc
ENV PATH=/opt/rh/rh-python36/root/usr/bin:$PATH

# OpenROAD env
ENV OPENROAD=/openroad/OpenROAD-$VERSION
ENV OPENROADOS=Linux-x86_64
ENV PATH=$OPENROAD/bin:$OPENROAD/bin/Linux-x86_64:$OPENROAD/pdn/scripts:$PATH
ENV LD_LIBRARY_PATH=$OPENROAD/lib:$OPENROAD/lib/Linux-x86_64:$LD_LIBRARY_PATH
ENV MANPATH=$OPENROAD/share/man:$MANPATH
ENV TCLLIBPATH=$OPENROAD/pdn/scripts:$TCLLIBPATH

# Install python dependencies
RUN pip3 install --upgrade pip && \
    pip3 install matplotlib

COPY deployment/requirements.deploy.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt

COPY deployment/celery/flow /flow/
COPY deployment/celery/alpha-release /tools/alpha-release/openroad
COPY src /src/
COPY deployment/celery/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /src

RUN mkdir /openroad-sandbox && chmod 777 /openroad-sandbox

ENV DJANGO_SETTINGS_MODULE=flow.settings
ENV UWSGI_WSGI_FILE=/src/flow/wsgi.py UWSGI_HTTP=:8000 UWSGI_MASTER=1 UWSGI_WORKERS=2 UWSGI_THREADS=8 UWSGI_UID=1000 UWSGI_GID=2000 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy
ENV OPENROAD /openroad

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]