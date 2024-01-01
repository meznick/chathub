# start from the official RabbitMQ image
FROM rabbitmq:3.12-management

# set the RabbitMQ service to listen on 5672, 15672 is for management
EXPOSE 5672 15672

# set default user and password
ENV RABBITMQ_DEFAULT_USER=dev
ENV RABBITMQ_DEFAULT_PASS=devpassword

# set default virtual host
ENV RABBITMQ_DEFAULT_VHOST=dev
