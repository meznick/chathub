default_config:
	rm config.json
	touch config.json
	@echo "{" >> config.json
	@echo '    "pg_host": "localhost",' >> config.json
	@echo '    "pg_port": 5432,' >> config.json
	@echo '    "pg_username": "dev_service",' >> config.json
	@echo '    "pg_password": "apipassword",' >> config.json
	@echo '    "redis_host": "localhost",' >> config.json
	@echo '    "redis_port": 6379,' >> config.json
	@echo '    "redis_username": "api_user",' >> config.json
	@echo '    "redis_password": "test",' >> config.json
	@echo '    "rmq_host": "localhost",' >> config.json
	@echo '    "rmq_port": 5672,' >> config.json
	@echo '    "rmq_username": "api_service",' >> config.json
	@echo '    "rmq_password": "apipassword",' >> config.json
	@echo "}" >> config.json
