DBT ?= dbt
STATE_DIR ?= data/prod_state
CI_FLAGS = --target ci --select state:modified+ --defer --state $(STATE_DIR)

.PHONY: prod ci

# Build everything into prod, then save the manifest for CI to compare against.
prod:
	$(DBT) build --target prod
	mkdir -p $(STATE_DIR)
	cp target/manifest.json $(STATE_DIR)/manifest.json

# Build only modified models (and their children) into an isolated schema,
# deferring to prod for everything else.
ci:
	$(DBT) build $(CI_FLAGS) --empty
	$(DBT) build $(CI_FLAGS)
