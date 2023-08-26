FROM python:3.10.0

COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

COPY get_issue_body.py /get_issue_body.py

CMD ["python", "/get_issue_body.py"]
