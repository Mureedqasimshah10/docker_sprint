FROM thoom/pyresttest

WORKDIR /app

COPY ./mytests /app

ENTRYPOINT ["pyresttest"]

CMD ["https://oxqssmq643.execute-api.us-east-1.amazonaws.com", "api_test.yml"]

