# Define variables for directories
DOCS_DIR = docs
SOURCE_DIR = src
TEST_DIR = tests

# Default target: Generate HTML documentation with pdoc
docs:
	@echo "Generating documentation with pdoc..."
	@pdoc --output-dir $(DOCS_DIR) $(SOURCE_DIR)
	@echo "Documentation generated in $(DOCS_DIR)/"

# Target to clean the docs directory
clean-docs:
	@echo "Cleaning up documentation directory..."
	@rm -rf $(DOCS_DIR)
	@echo "Documentation cleaned up."

# Target to run tests (ensure the test directory is specified)
test:
	@echo "Running tests..."
	@pytest $(TEST_DIR)
	@echo "Tests completed."

# Define phony targets to avoid conflicts with file names
.PHONY: docs clean-docs test
