ARG PYTHON=3.11
ARG TERRAFORM=latest

FROM amazon/aws-lambda-python:${PYTHON} AS lock
RUN pip install pipenv
RUN pipenv lock 2>&1
COPY Pipfile* /var/task/
RUN pipenv requirements > requirements-lock.txt
RUN pipenv requirements --dev > requirements-dev-lock.txt

FROM amazon/aws-lambda-python:${PYTHON} AS zip
RUN yum install -y git zip
COPY src .
COPY --from=lock /var/task/ .
RUN mkdir dist
RUN pip install -r requirements-lock.txt -t .
RUN find . -name __pycache__ | xargs rm -rf
RUN zip -9r dist/sync.zip .
COPY src/alarm.py .
RUN zip -9r dist/alarm.zip alarm.py

FROM hashicorp/terraform:${TERRAFORM} AS plan
WORKDIR /var/task/
COPY *.tf /var/task/

ARG AWS_ACCESS_KEY_ID
ARG AWS_DEFAULT_REGION=us-east-1
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_ROLE_ARN
ARG AWS_SESSION_TOKEN

ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV AWS_ROLE_ARN=${AWS_ROLE_ARN}
ENV AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN}

RUN terraform init
RUN terraform fmt

COPY --from=zip /var/task/dist/ /var/task/dist/

ARG TF_VAR_VERSION
ENV TF_VAR_VERSION=${TF_VAR_VERSION}

RUN echo "Target Role ARN is: '${AWS_ROLE_ARN}'"

RUN terraform plan -var="AWS_ROLE_ARN=${AWS_ROLE_ARN}" -out=tfplan

CMD ["apply", "tfplan"]