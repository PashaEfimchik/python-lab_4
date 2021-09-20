FROM python:3.8.6
COPY . /lab_4
WORKDIR /lab_4
RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]