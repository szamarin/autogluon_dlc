#################################################################################
# GLOBALS                                                                       #
#################################################################################

LOCAL_DATA_DIR = data
LOCAL_CODE_DIR = training_scripts
DOCKERFILE_DIR = containers
TARGET_DATA_DIR = /data
TARGET_CODE_DIR = /code
BASE_IMAGE_NAME = autogluon
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Build cpu image
build_train_cpu: 
	docker build -f $(DOCKERFILE_DIR)/training/Dockerfile.cpu  -t $(BASE_IMAGE_NAME)-cpu .

## Build gpu image
build_train_gpu: 
	docker build -f $(DOCKERFILE_DIR)/training/Dockerfile.gpu  -t $(BASE_IMAGE_NAME)-gpu .

## Build and push cpu
push_train_cpu: 
	./build_and_push.sh $(BASE_IMAGE_NAME)-cpu $(DOCKERFILE_DIR)/training/Dockerfile.cpu

## Build push gpu
push_train_gpu: 
	./build_and_push.sh $(BASE_IMAGE_NAME)-gpu $(DOCKERFILE_DIR)/training/Dockerfile.gpu

## Run interactive cpu
run_train_cpu: 
	docker container run -it --rm \
	-v ${PWD}/$(LOCAL_DATA_DIR):$(TARGET_DATA_DIR) \
	-v ${PWD}/$(LOCAL_CODE_DIR):$(TARGET_CODE_DIR) \
	autogluon-cpu bash

## Run interactive gpu
run_train_gpu: 
	docker container run -it --rm \
	-v ${PWD}/$(LOCAL_DATA_DIR):$(TARGET_DATA_DIR) \
	-v ${PWD}/$(LOCAL_CODE_DIR):$(TARGET_CODE_DIR) \
	autogluon-gpu bash

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
