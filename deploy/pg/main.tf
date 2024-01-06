terraform {
  required_providers {
    postgresql = {
      source = "cyrilgdn/postgresql"
      version = "1.21.0"
    }
  }
}

variable "postgres_user_password" {
  type = string
  default = "password"
}

variable "pg_host" {
  type = string
  default = "localhost"
}

variable "pg_port" {
  type = number
  default = 5432
}

variable "pg_dbname" {
  type = string
  default = "dev"
}

variable "dev_password" {
  type = string
  default = "devpassword"
}

provider "postgresql" {
  host            = var.pg_host
  port            = var.pg_port
  database        = var.pg_dbname
  username        = "postgres"
  password        = var.postgres_user_password
  sslmode         = "disable"
  connect_timeout = 15
}

# DEV
resource "postgresql_role" "dev_developer" {
  name     = "dev_developer"
  login    = true
  password = var.dev_password
  connection_limit = 3
}

resource "postgresql_role" "dev_service" {
  name     = "dev_service"
  login    = true
  password = var.dev_password
  connection_limit = 10
}

resource "postgresql_database" "chathub_dev" {
  name              = "chathub_dev"
  owner             = postgresql_role.dev_developer.name
  connection_limit  = -1
  allow_connections = true
}

resource "postgresql_grant" "read_write_services_dev" {
  database    = postgresql_database.chathub_dev.name
  object_type = "table"
  schema      = "public"
  privileges  = ["SELECT", "INSERT", "UPDATE"]
  role        = postgresql_role.dev_service.name
}

# PROD
# все то же самое что и на дев + (сделать бекап данных) отдельно
