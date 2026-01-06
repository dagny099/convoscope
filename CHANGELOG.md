# Changelog

All notable changes to Convoscope will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Professional changelog following Keep a Changelog standards

---

## [2.0.0] - 2025-10-24

### Added
- **Model Comparison System**: Side-by-side evaluation of 2-4 provider/model pairs on the same prompt
- **Blind Scoring Interface**: Randomized A/B/C labels to reduce bias with 5-point evaluation rubric
  - Correctness, usefulness, clarity, safety, and overall quality metrics
- **Quick Winner Selection**: Radio button interface for fast preference indication
- **Results Viewer**: Filter comparison results by date, tags, and models with preview functionality
- **JSONL Logging**: Append-only log for all comparison results in `experiments/results.jsonl`
- **Metrics Tracking**: Latency (ms), token counts, and estimated costs per response
- **Prompt Caching**: Default cached demo prompt for fast first-run experience in `experiments/default_compare_cache.json`
- **Three-Tab Navigation**: Chat, Compare View, and Results with CSS-variable theming
- **Pricing Configuration**: Model pricing data in `experiments/pricing.yaml` for cost estimation
- **Baseline Prompts**: Systematic testing prompt sets in `experiments/prompts.yaml`
- Model comparison documentation in `docs/guides/model-comparison.md`

### Changed
- Navigation system from radio buttons to modern button-based interface
- Theme implementation using CSS variables for consistency across all views
- Screenshot automation to capture comparison workflow
- Visual tour documentation to feature new hero interface

### Fixed
- Date timezone bug in results logging
- Streamlit deprecation warnings for widget width parameters
- Gemini model configuration and `.env.example` template

---

## [1.2.0] - 2025-09-27

### Added
- Professional gradient header design with provider status chips
- Smart system prompt detection (automatic "Custom" labeling)
- Visual hierarchy improvements with organized sidebar sections
- Custom favicon for brand identity

### Changed
- Modernized sidebar design with preserved provider chip functionality
- Improved responsive design for better mobile compatibility
- Enhanced color theming with dark/light mode compatibility

### Fixed
- Temperature slider widget warning from improper session state usage
- Session state initialization error on first load
- Provider status chip update synchronization issue

---

## [1.1.0] - 2025-09-13

### Added
- Automated screenshot capture system in `scripts/capture-screenshots.py`
- Visual assets index documenting all project screenshots and diagrams
- Portfolio showcase documentation highlighting key features
- Visual documentation framework for professional presentation
- Enhanced README with visual tour section

### Changed
- Documentation structure with comprehensive visual asset organization
- Portfolio presentation with before/after metrics and journey narrative

---

## [1.0.0] - 2025-09-08

### Added
- **Multi-Provider LLM Integration**: OpenAI, Anthropic Claude, and Google Gemini support
- **Intelligent Fallback System**: Automatic provider switching on failures
- **Circuit Breaker Pattern**: Prevents cascade failures with exponential backoff
- **Health Monitoring**: Real-time provider availability checking
- **Comprehensive Testing**: 80+ automated tests (50+ unit, 20+ integration)
- **Playwright Integration Tests**: End-to-end UI workflow testing
- **MkDocs Documentation Site**: Professional documentation with Material theme
- **System Architecture Diagrams**: Mermaid diagrams for architecture and data flow in `diagrams/`
- **Technical Decision Records (TDRs)**: Documentation of architectural choices
- **Deployment Configuration**: Docker and Google Cloud Run deployment scripts
- **Conversation Management**: Save, load, and export functionality with auto-backup
- **Topic Summarization**: AI-generated conversation summaries
- **HTML Export**: Styled conversation exports with FontAwesome icons
- Modular architecture with service layer separation (`src/services/`, `src/utils/`)
- Atomic file operations for data persistence
- Data validation and integrity checks
- API documentation for all services
- Code quality tooling: `radon` complexity analysis, `cloc` metrics
- Comprehensive README with architecture overview and quick start guide

### Changed
- **Major Refactor**: Transformed 696-line monolith into modular architecture (42% code reduction)
- Project structure organized into `src/`, `tests/`, `docs/`, and `experiments/` directories
- Configuration management with environment variables and `.env` support
- Test organization into unit and integration test suites

### Removed
- Monolithic `run_chat.py` logic (replaced with modular services)
- `.venv` from version control (added to `.gitignore`)
- Unwanted JSON files and temporary artifacts

---

## [0.2.0] - 2025-01-13

### Added
- Accurate `requirements.txt` with pinned dependencies
- LLaMA-Index integration for enhanced LLM interactions
- Streamlit-specific requirements organization

### Changed
- Dependency management for better reproducibility
- Requirements organization for clearer dependency purposes

### Removed
- `.DS_Store` files from repository
- Redundant and outdated requirements files

---

## [0.1.0] - 2024-11-02

### Added
- Initial Streamlit-based chat application
- Basic OpenAI integration
- Simple conversation interface
- Foundational project structure

---

## Version History Summary

| Version | Date | Key Milestone |
|---------|------|---------------|
| 2.0.0 | 2025-10-24 | Model Comparison & Evaluation System |
| 1.2.0 | 2025-09-27 | UI/UX Modernization & Branding |
| 1.1.0 | 2025-09-13 | Visual Documentation & Portfolio Enhancement |
| 1.0.0 | 2025-09-08 | Production-Ready Multi-Provider Release |
| 0.2.0 | 2025-01-13 | Dependency Management & Configuration |
| 0.1.0 | 2024-11-02 | Initial Release |

---

## Migration Guides

### Upgrading to 2.0.0
- New tab navigation system replaces sidebar-only interface
- Experiments module requires `experiments/` directory with JSONL support
- New dependencies: `pandas`, `pyarrow` for results handling
- CSS variable theming may affect custom styles

### Upgrading to 1.0.0
- Breaking change: Modular architecture requires updated imports
- Environment variables now required for all providers (see `.env.example`)
- Conversation storage format updated (automatic migration on first load)
- Testing framework requires `pytest`, `playwright` installation

---

## Development Metrics

### Current State (v2.0.0)
- **Total Lines of Code**: ~2,000 (excluding tests and docs)
- **Test Coverage**: 95%+ across core services
- **Test Count**: 80+ automated tests
- **Documentation Pages**: 20+ comprehensive guides and API references
- **Maintainability**: Grade A (Radon complexity analysis)

### From Monolith to Modular
- **Before**: 696-line single file
- **After**: Modular architecture with clear separation of concerns
- **Code Reduction**: 42% through service abstraction and DRY principles
- **Uptime Improvement**: From single-provider to 99.9% with intelligent fallback

---

## Links

- [Documentation](https://docs.barbhs.com/convoscope)
- [GitHub Repository](https://github.com/dagny099/convoscope)
- [Issues](https://github.com/dagny099/convoscope/issues)
- [Pull Requests](https://github.com/dagny099/convoscope/pulls)

---

## Contributing

When contributing to Convoscope:
1. Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages
2. Update this CHANGELOG.md with your changes under `[Unreleased]`
3. Ensure all tests pass (`python run_tests.py all`)
4. Update relevant documentation in `docs/`
5. Add screenshots for UI changes to `docs/assets/screenshots/`

---

*This changelog is maintained following [Keep a Changelog](https://keepachangelog.com/) principles and [Semantic Versioning](https://semver.org/) standards.*
