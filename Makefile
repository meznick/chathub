default_config:
	rm config.json
	touch config.json
	@echo "{" >> config.json
	@echo '    "pg_host": "",' >> config.json
	@echo '    "pg_port": 5432,' >> config.json
	@echo '    "pg_username": "",' >> config.json
	@echo '    "pg_password": "",' >> config.json
	@echo '    "redis_host": "",' >> config.json
	@echo '    "redis_port": 6379,' >> config.json
	@echo '    "redis_username": "",' >> config.json
	@echo '    "redis_password": "",' >> config.json
	@echo '    "rmq_host": "",' >> config.json
	@echo '    "rmq_port": 5672,' >> config.json
	@echo '    "rmq_username": "",' >> config.json
	@echo '    "rmq_password": "",' >> config.json
	@echo '    "api_host": ""' >> config.json
	@echo '    "api_port": ""' >> config.json
	@echo '    "websocket_host": ""' >> config.json
	@echo "}" >> config.json
