# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal collection of Agent skills for Claude Code - a plugin-based architecture where each skill is a self-contained module that extends Claude's capabilities.

### Plugin Configuration
- `.claude-plugin/marketplace.json`: Defines plugin metadata and registers all skills
- Each skill is a separate directory with its own implementation

### Current Skills
- **pdf-toc-extractor**: Extracts hierarchical bookmarks/outlines from PDF documents
- **deepin-mail**: Interacts with deepin-mail via D-Bus for email operations on Deepin OS

## Development Commands

### Testing a Skill
```bash
# Validate Python syntax in skill scripts
python pdf-toc-extractor/scripts/test_syntax.py

# Test PDF TOC extraction directly
python pdf-toc-extractor/scripts/extract_toc.py <pdf_file> --json

# Test deepin-mail D-Bus operations
python deepin-mail/scripts/dbus_client.py accounts
python deepin-mail/scripts/dbus_client.py mails --folder INBOX --limit 10
```

### Skill Dependencies
Each skill manages its own dependencies:
- `pdf-toc-extractor/scripts/requirements.txt`: PyPDF2, pdfplumber, pandas
- `deepin-mail`: Uses only standard library (subprocess for gdbus calls)

## Architecture

### Skill Organization Pattern
Each skill directory contains:
- **SKILL.md**: Skill definition with frontmatter (name, description, compatibility) and detailed usage documentation
- **scripts/**: Executable code implementing the skill functionality
- **references/**: (optional) API documentation and guides loaded into Claude's context
- **assets/**: (optional) Templates or resources for output

### Plugin Configuration (`.claude-plugin/marketplace.json`)
```json
{
  "name": "myagentskills",
  "plugins": [
    {
      "name": "skill-name",
      "description": "Skill description",
      "source": "./",
      "strict": false,
      "skills": ["./skill-directory"]
    }
  ]
}
```
- `strict: false` allows dynamic skill loading
- Skills are referenced by path relative to plugin root

### Skill Implementation Patterns

**pdf-toc-extractor**: Multi-module Python script
- `extract_toc.py`: Main entry point with CLI
- `toc_page_analyzer.py`: TOC page detection logic
- `toc_pattern_matcher.py`: Pattern matching for TOC formats
- Uses PyPDF2 for bookmark extraction, falls back to page analysis

**deepin-mail**: D-Bus client wrapper
- `dbus_client.py`: DeepinMailDBusClient class wrapping gdbus calls
- JSON-based communication protocol
- Includes CLI for manual testing

## Adding New Skills

1. Create a new skill directory at the root level (e.g., `skill-name/`)
2. Create `SKILL.md` with frontmatter:
   ```yaml
   ---
   name: skill-name
   description: One-line description of when to use this skill
   compatibility: Prerequisites (OS, tools, APIs)
   ---
   ```
3. Add `scripts/` directory with implementation code
4. (Optional) Add `references/` for documentation to load into context
5. Update `.claude-plugin/marketplace.json` to register the new skill

## Notes for Development
- Skills are self-contained - no cross-skill dependencies
- Scripts should be executable directly for testing
- SKILL.md frontmatter is critical for skill discovery and triggering
- Reference files are loaded into Claude's context during skill execution
