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

provider "rabbitmq" {
  endpoint = var.rabbitmq_endpoint
  username = var.provider_user
  password = var.provider_password
}

resource "rabbitmq_vhost" "chathub" {
  name = "chathub"
}

resource "rabbitmq_user" "api_user" {
  name     = "api_service"
  password = var.api_user_password
  tags     = ["service"]
}

resource "rabbitmq_permissions" "permissions_prod" {
  user  = rabbitmq_user.api_user.name
  vhost = rabbitmq_vhost.chathub.name

  permissions {
    configure = "^$"
    write     = ".*"
    read      = ".*"
  }
}

resource "rabbitmq_exchange" "direct_main_prod" {
  name  = "direct_main_prod"
  vhost = rabbitmq_vhost.chathub.name

  settings {
    type        = "direct"
    durable     = false
    auto_delete = false
  }
}

resource "rabbitmq_exchange" "direct_main_dev" {
  name  = "direct_main_dev"
  vhost = rabbitmq_vhost.chathub.name

  settings {
    type        = "direct"
    durable     = false
    auto_delete = false
  }
}

resource "rabbitmq_queue" "matchmaker_prod" {
  name  = "matchmaker_prod"
  vhost = rabbitmq_vhost.chathub.name

  settings {
    durable     = false
    auto_delete = false
    arguments = {
      "x-queue-type" : "classic",
    }
  }
}

resource "rabbitmq_queue" "matchmaker_dev" {
  name  = "matchmaker_dev"
  vhost = rabbitmq_vhost.chathub.name

  settings {
    durable     = false
    auto_delete = false
    arguments = {
      "x-queue-type" : "classic",
    }
  }
}

resource "rabbitmq_binding" "matchmaker_prod" {
  source           = rabbitmq_exchange.direct_main_prod.name
  vhost            = rabbitmq_vhost.chathub.name
  destination      = rabbitmq_queue.matchmaker_prod.name
  destination_type = "queue"
  routing_key      = "matchmaker"
}

resource "rabbitmq_binding" "matchmaker_dev" {
  source           = rabbitmq_exchange.direct_main_dev.name
  vhost            = rabbitmq_vhost.chathub.name
  destination      = rabbitmq_queue.matchmaker_dev.name
  destination_type = "queue"
  routing_key      = "matchmaker"
}
