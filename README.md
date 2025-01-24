# PalMon

[![Tests](https://github.com/ardfard/PalMon/actions/workflows/test.yml/badge.svg)](https://github.com/ardfard/PalMon/actions/workflows/test.yml)
[![PalMon CI](https://github.com/ardfard/PalMon/actions/workflows/palmon.yml/badge.svg)](https://github.com/ardfard/PalMon/actions/workflows/palmon.yml)
[![codecov](https://codecov.io/gh/ardfard/PalMon/branch/main/graph/badge.svg)](https://codecov.io/gh/ardfard/PalMon)

PalMon is stealing Pokemon data (please don't sue)

## Features

- 🔄 Automatic Pokemon data scraping from PokeAPI
- 🚀 Fast and modern REST API
- 📊 Prometheus metrics integration
- 📝 OpenAPI documentation
- 🧪 Comprehensive test suite
- 🔧 Nix-based development environment

## Quick Start

You can easily run the project with the provided script. It has two modes:

1. with Nix
2. with Docker

### Running with Just Nix

You can run run-palmon.sh that will detect if you have Nix installed and use it. Or if you don't have Nix installed, it will install it for you. Please consider the warning below below before running the script.

⚠️ **WARNING** ⚠️

Running `run-palmon.sh` will:
- ☠☠ Install Nix package manager on your system ☠☠
- Modify your shell configuration
- Add Nix configuration files
Make sure you understand these changes before proceeding!

If you're okay with these changes: 

```
./run-palmon.sh
```

This will:
1. Install Nix if not present
2. Set up the development environment
3. Scrape Pokemon data
4. Start the API server
5. Run smoke tests

## Running with Docker

For those who don't want to deal with Nix, you can use the provided script to run the project in a Docker container.
This assumes you have Docker installed on your system. So if you don't have it, you can install it from [here](https://docs.docker.com/get-docker/).

```
./run-palmon-docker.sh
```

This will:
1. Build the Docker image
2. Run the container interactively
3. Execute `run-palmon.sh` inside the container

## Manual Setup

If you already have a Python environment and the `uv` package manager, you can manually set up and run the project:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ardfard/PalMon.git
   cd PalMon
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -e .
   ```

3. **Run the scraper**:
   ```bash
   python -m palmon.scraper.pokemon_scraper
   ```

4. **Start the API server**:
   ```bash
   python -m palmon.api.app
   ```

5. **Run smoke tests**:
   ```bash
   python -m palmon.tests.smoke_tests
   ```

## API Documentation

Once running, API documentation is available at:
- OpenAPI UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

- `GET /api/pokemon`: List all Pokemon with pagination
- `GET /api/pokemon/{id}`: Get specific Pokemon by ID
- `GET /metrics`: Prometheus metrics

## Development

### Running Tests

```
./run_tests.sh
```

The project uses GitHub Actions for:
- Running tests
- Code coverage reporting
- Smoke testing
- Dependency caching

## License

MIT

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request