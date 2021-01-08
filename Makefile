export PYTHONPATH := $(shell pwd)/fluentbit-server-py:$(PYTHONPATH)

client_build :
	docker build -t fluentc .

client_run_basic : client_build
	docker run --rm --name fluentclient -v $(shell pwd)/etc:/fluent/etc -e HOSTNAME=$(uname -n) --net host fluentc fluent-bit -c /fluent/etc/client.conf

client_run_auth : client_build
	docker run --rm --name fluentclient -v $(shell pwd)/etc:/fluent/etc -e HOSTNAME=$(uname -n) --net host fluentc fluent-bit -c /fluent/etc/client_auth.conf

client_run_ssl : client_build
	docker run --rm --name fluentclient -v $(shell pwd)/etc:/fluent/etc -e HOSTNAME=$(uname -n) --net host fluentc fluent-bit -c /fluent/etc/client_auth_ssl.conf

unittest:
	python3 -m unittest discover -s tests/ -p "*.py"

certificate:
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout etc/toto.com.key -out etc/toto.com.cert

server_build :
	docker build -t test_server -f dockerfile_server .

server_run : server_build
	docker run -it --rm -m 1024M  -v $(shell pwd)/etc:/root/etc/ -v $(shell pwd)/tests:/root/tests/ -v $(shell pwd)/fluentbit_server:/root/fluentbit_server/ --net host test_server python3 tests/server_auth_ssl.py

server_run_ssl:
	python3 tests/server_auth_ssl.py

server_run_auth:
	python3 tests/server_auth.py

server_run_basic:
	python3 tests/server_basic.py

build_pip:
	python3 setup.py sdist
	python3 setup.py bdist_wheel

clean_pip:
	rm -rf dist/ build/ fluentbit_server_py.egg-info/