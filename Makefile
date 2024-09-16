# Define variables for directories
DOCS_DIR = docs
SOURCE_DIR = src
TEST_DIR = tests

# Default target: Generate HTML documentation with pdoc, ensuring PYTHONPATH is set correctly (Windows compatible)
docs:
	@echo "Generating documentation with pdoc..."
	@set PYTHONPATH=C:/Users/molak/strategy-research;C:/Users/molak/AppData/Local/pypoetry/Cache/virtualenvs/strategy-research-dv98sU_e-py3.9/lib/python3.9/site-packages && poetry run pdoc --output-dir $(DOCS_DIR) $(SOURCE_DIR)
	@echo "Documentation generated in $(DOCS_DIR)/"

# Target to clean the docs directory
clean-docs:
	@echo "Cleaning up documentation directory..."
	@rm -rf $(DOCS_DIR)
	@echo "Documentation cleaned up."

# Target to run tests, ensuring pytest runs within the Poetry environment (Windows compatible)
test:
	@echo "Running tests..."
	@set PYTHONPATH=C:/Users/molak/strategy-research;C:/Users/molak/AppData/Local/pypoetry/Cache/virtualenvs/strategy-research-dv98sU_e-py3.9/lib/python3.9/site-packages && poetry run pytest $(TEST_DIR)
	@echo "Tests completed."

# Define phony targets to avoid conflicts with file names
.PHONY: docs clean-docs test