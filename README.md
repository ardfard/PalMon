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