#!/usr/bin/env bash

set -euo pipefail

# Function to display usage
usage() {
  echo "Usage: $(basename "$0") [-h] <message>"
  echo "Options:"
  echo "  -h, --help    Display this help message"
  exit 1
}

# Function to run alembic commands
run_alembic() {
  local message="$1"

  # Generate migration
  alembic revision --autogenerate -m "$message"

  # Upgrade to the latest revision
  alembic upgrade head

  # Add changes to git
  git add "${SCRIPT_DIR}/../migrations/versions"
}

# Parse command-line options
parse_options() {
  while [[ $# -gt 0 ]]; do
    case $1 in
      -h|--help)
        usage
        ;;
      *)
        MESSAGE="$1"
        ;;
    esac
    shift
  done

  # If no message provided
  if [ -z "$MESSAGE" ]; then
    echo "Error: Please provide a message for the migration."
    usage
  fi
}

# Main function
main() {
  # Default values
  MESSAGE=""

  # Parse command-line options
  parse_options "$@"

  # Obtain the directory of the script
  SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

  # Run alembic commands
  run_alembic "$MESSAGE"
}

# Execute main function
main "$@"
