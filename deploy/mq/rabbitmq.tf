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
  default = "dev"
}

variable "provider_password" {
  type = string
  default = "devpassword"
}

variable "rabbitmq_endpoint" {
  type = string
  default = "http://localhost:8081"
}

variable "target_vhost" {
  type = string
  default = "chathub_prod"
}

provider "rabbitmq" {
  endpoint = var.rabbitmq_endpoint
  username = var.provider_user
  password = var.provider_password
}

resource "rabbitmq_vhost" "chathub_prod" {
  name = var.target_vhost
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
  name  = "direct_main"
  vhost = rabbitmq_vhost.chathub_prod.name

  settings {
    type        = "direct"
    durable     = false
    auto_delete = false
  }
}

resource "rabbitmq_queue" "matchmaker" {
  name  = "matchmaker"
  vhost = rabbitmq_vhost.chathub_prod.name

  settings {
    durable     = false
    auto_delete = false
    arguments = {
      "x-queue-type" : "classic",
    }
  }
}

resource "rabbitmq_binding" "matchmaker" {
  source           = rabbitmq_exchange.direct_main.name
  vhost            = rabbitmq_vhost.chathub_prod.name
  destination      = rabbitmq_queue.matchmaker.name
  destination_type = "queue"
  routing_key      = "matchmaker"
}
