# Guardian Documentation

Welcome to Guardian - AI-Powered Penetration Testing CLI Tool

## User Guides

### Getting Started
- [README.md](../README.md) - Korean overview (primary)
- [README_EN.md](../README_EN.md) - English overview
- [QUICKSTART.md](../QUICKSTART.md) - Installation and basic usage
- [QUICKSTART_KO.md](QUICKSTART_KO.md) - 한국어 빠른 시작 가이드

### Core Documentation
- [USAGE.md](USAGE.md) - Detailed command reference (coming soon)
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration guide (coming soon)

## Compliance Pack (2026-02-12)
- [2026-02-12_docs-1.md](2026-02-12_docs-1.md) - 범위/ROE/위험분석
- [2026-02-12_docs-2.md](2026-02-12_docs-2.md) - OWASP LLM Top 10 통제 매트릭스
- [2026-02-12_docs-3.md](2026-02-12_docs-3.md) - 테스트 실행/증거/보고

## Developer Guides

### Tool Development
- [TOOLS_DEVELOPMENT_GUIDE.md](TOOLS_DEVELOPMENT_GUIDE.md) - Creating custom tools
- [tools/README.md](../tools/README.md) - Available tools overview

### Workflow Development
- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Creating custom workflows
- [workflows/](../workflows/) - Example workflow files

### Architecture
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture (coming soon)
- [AI_AGENTS.md](AI_AGENTS.md) - Agent system design (coming soon)

## API Reference

### Agents
- **Planner Agent** - Strategic decision making
- **Tool Agent** - Tool selection and execution
- **Analyst Agent** - Result interpretation
- **Reporter Agent** - Report generation

### Tools
9 integrated pentesting tools:
- Network: Nmap
- Web: httpx, WhatWeb, Wafw00f, Nikto
- Subdomain: Subfinder
- Vulnerability: Nuclei
- SSL: TestSSL
- Content: Gobuster

## Contributing

Contributions welcome! 

1. Fork the repository
2. Create feature branch
3. Follow development guides
4. Submit pull request

## Support

- Issues: GitHub Issues
- Documentation: This directory
- Examples: `workflows/` and `examples/` (coming soon)

## License

MIT License - See LICENSE file
