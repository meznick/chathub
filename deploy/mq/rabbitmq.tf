terraform {
  required_providers {
    rabbitmq = {
      source = "cyrilgdn/rabbitmq"
      version = "1.8.0"
    }
  }
}

variable "api_user_password" {
  type = string
}

variable "provider_user" {
  type = string
  default = "myuser"
}

variable "provider_password" {
  type = string
  default = "mypassword"
}

variable "rabbitmq_endpoint" {
  type = string
  default = "http://localhost:8081"
}

provider "rabbitmq" {
  endpoint = var.rabbitmq_endpoint
  username = var.provider_user
  password = var.provider_password
}

resource "rabbitmq_vhost" "chathub_prod" {
  name = "chathub_prod"
}

resource "rabbitmq_user" "api_user" {
  name     = "api_service"
  password = var.api_user_password
  tags     = ["service"]
}

resource "rabbitmq_permissions" "permissions" {
  user  = rabbitmq_user.api_user.name
  vhost = rabbitmq_vhost.chathub_prod.name

  permissions {
    configure = "^$"
    write     = ".*"
    read      = ".*"
  }
}

resource "rabbitmq_exchange" "direct_main" {
  name  = "test"
  vhost = rabbitmq_vhost.chathub_prod.name

  settings {
    type        = "direct"
    durable     = false
    auto_delete = false
  }
}

resource "rabbitmq_queue" "matchmaker" {
  name  = "test"
  vhost = rabbitmq_vhost.chathub_prod.name

  settings {
    durable     = false
    auto_delete = false
    arguments = {
      "x-queue-type" : "classic",
    }
  }
}

resource "rabbitmq_binding" "test" {
  source           = rabbitmq_exchange.direct_main.name
  vhost            = rabbitmq_vhost.chathub_prod.name
  destination      = rabbitmq_queue.matchmaker.name
  destination_type = "queue"
  routing_key      = "matchmaker"
}
