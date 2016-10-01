.PHONY: install-plugin read-db run-miner

install-instrumentation-plugin:
	make -C fault_cardinality_classifier install-plugin

run-miner:
	make -C repository_mining run

read-db:
	make -C repository_mining read_db
	mv repository_mining/fixes.csv fixes.csv
