# Token Telemetry System

A comprehensive token analysis system for CelestiaOrg repositories, designed to help AI agents understand codebase size, complexity, and structure for better context management and development assistance.

## 🎯 Purpose

This system automatically analyzes CelestiaOrg repositories and provides detailed token counts using the GPT-2 tokenizer. The results are published as a JSON API that AI agents can consume to make informed decisions about context window management, repository prioritization, and code analysis strategies.

## 🚀 Live API

**Endpoint:** `https://celestiaorg.github.io/tokenmetry/index.json`

The JSON includes comprehensive metadata, usage instructions, and detailed token analysis for all configured repositories.

## 📊 What's Analyzed

The system analyzes repositories configured in `repos.txt`. Current analysis results:
git 
<!-- TOKENMETRY_TABLE_START -->
| Repository | Total Files | Total Tokens | Go Files | Go Tokens | Markdown Files | Markdown Tokens | Rust Files | Rust Tokens | Solidity Files | Solidity Tokens |
|------------|-------------|--------------|----------|-----------|----------------|-----------------|------------|-------------|----------------|-----------------|
| celestia-core | 1198 | 3,303,547 | 716 | 2,568,944 | 482 | 734,603 | 0 | 0 | 0 | 0 |
| celestia-app | 458 | 1,058,291 | 367 | 750,026 | 91 | 308,265 | 0 | 0 | 0 | 0 |
| celestia-node | 478 | 746,843 | 457 | 702,863 | 21 | 43,980 | 0 | 0 | 0 | 0 |
| rsmt2d | 14 | 40,074 | 13 | 38,943 | 1 | 1,131 | 0 | 0 | 0 | 0 |
| optimism | 3241 | 8,648,780 | 2662 | 6,694,388 | 106 | 144,624 | 0 | 0 | 473 | 1,809,768 |
| nitro | 742 | 2,110,710 | 581 | 1,598,154 | 13 | 7,132 | 148 | 505,424 | 0 | 0 |
| nitro-contracts | 169 | 397,834 | 0 | 0 | 2 | 2,125 | 0 | 0 | 167 | 395,709 |
| nitro-das-celestia | 39 | 630,363 | 17 | 601,361 | 2 | 4,570 | 0 | 0 | 20 | 24,432 |
| docs | 86 | 219,221 | 0 | 0 | 86 | 219,221 | 0 | 0 | 0 | 0 |
| eq-service | 24 | 52,780 | 0 | 0 | 7 | 10,237 | 17 | 42,543 | 0 | 0 |
| CIPs | 54 | 130,427 | 0 | 0 | 54 | 130,427 | 0 | 0 | 0 | 0 |
| pda-proxy | 18 | 45,003 | 0 | 0 | 3 | 5,860 | 15 | 39,143 | 0 | 0 |
| hana | 29 | 25,388 | 0 | 0 | 7 | 315 | 22 | 25,073 | 0 | 0 |
| localestia | 12 | 26,735 | 0 | 0 | 2 | 1,605 | 10 | 25,130 | 0 | 0 |
| rollkit | 342 | 821,224 | 236 | 586,036 | 91 | 157,508 | 15 | 77,680 | 0 | 0 |
| zksync-era | 2390 | 7,075,867 | 0 | 0 | 281 | 708,163 | 2032 | 6,271,486 | 77 | 96,218 |
| dojo | 213 | 770,304 | 0 | 0 | 16 | 7,844 | 197 | 762,460 | 0 | 0 |
| weave | 127 | 352,078 | 123 | 350,618 | 4 | 1,460 | 0 | 0 | 0 | 0 |
| **TOTAL** | **9634** | **26,455,469** | **5172** | **13,891,333** | **1269** | **2,489,070** | **2456** | **7,748,939** | **737** | **2,326,127** |

**Last Updated:** 2025-09-23 06:02:06 UTC
<!-- TOKENMETRY_TABLE_END -->

**File Types:** `.go` (Go source code) and `.md` (Markdown documentation)

## 🔧 Components

### Core Files

- **`tokenizer.py`** - Main Python script for token analysis
- **`repos.txt`** - Configuration file listing repositories to analyze
- **`.github/workflows/tokenizer.yml`** - GitHub Actions workflow for automation
- **`pyproject.toml`** - Poetry dependency management

### Key Features

- **GPT-2 Tokenizer** - Consistent token counting across all content
- **Repository Cloning** - Shallow clones for efficient analysis
- **File-level Analysis** - Detailed breakdown of individual files
- **AI-Optimized Output** - Metadata and usage instructions for AI agents
- **Automated Deployment** - Daily updates and on-demand execution

## 🤖 AI Agent Usage

### Quick Start
```python
import requests

# Fetch token telemetry data
response = requests.get('https://celestiaorg.github.io/tokenmetry/index.json')
data = response.json()

# Get overall statistics
total_tokens = data['summary']['total_tokens']
total_repos = data['summary']['total_repositories']

# Discover available repositories
for repo in data['repositories']:
    name = repo['repository']['name']
    url = repo['repository']['url']
    tokens = repo['total_tokens']
    print(f"{name}: {tokens:,} tokens")
```

### Context Management Strategies

1. **Repository Prioritization**
   ```python
   # Sort repositories by size for context planning
   repos_by_size = sorted(data['repositories'], 
                         key=lambda x: x['total_tokens'])
   ```

2. **File Analysis**
   ```python
   # Find largest files that might need chunking
   for repo in data['repositories']:
       large_files = [f for f in repo['files'] if f['tokens'] > 5000]
   ```

3. **Language Breakdown**
   ```python
   # Understand code vs documentation ratio
   go_tokens = data['summary']['by_extension']['.go']['tokens']
   md_tokens = data['summary']['by_extension']['.md']['tokens']
   ```

## 🛠️ Local Development

### Prerequisites

- Python 3.9+
- Poetry
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/celestiaorg/tokenmetry.git
cd tokenmetry

# Install dependencies
poetry install

# Run analysis on all configured repositories
poetry run python tokenizer.py --celestia-repos --output results.json

# Analyze a single repository
poetry run python tokenizer.py --repo https://github.com/celestiaorg/celestia-app.git

# Analyze a local directory
poetry run python tokenizer.py --directory /path/to/repo

# Analyze a single file
poetry run python tokenizer.py --file example.go
```

### Command Line Options

```
usage: tokenizer.py [-h] (--file FILE | --directory DIRECTORY | --repo REPO | --celestia-repos | --text TEXT)
                    [--repo-file REPO_FILE] [--output OUTPUT] [--verbose]

options:
  --file, -f           Path to file to tokenize
  --directory, -d      Path to directory to process
  --repo, -r           Repository URL to clone and process
  --celestia-repos     Process all repositories from repos.txt
  --text, -t           Text string to tokenize
  --repo-file          Path to repository list file (default: repos.txt)
  --output, -o         Output JSON file path
  --verbose, -v        Show detailed file-by-file results
```

## 📝 Configuration

### Adding Repositories

Edit `repos.txt` to add or remove repositories:

```
# CelestiaOrg Repository List
# One repository URL per line
# Lines starting with # are comments

https://github.com/celestiaorg/celestia-core
https://github.com/celestiaorg/celestia-app
https://github.com/celestiaorg/celestia-node
https://github.com/celestiaorg/docs
```

Changes to `repos.txt` automatically trigger workflow runs.

### GitHub Pages Setup

1. Go to repository **Settings** → **Pages**
2. Set **Source** to **"GitHub Actions"**
3. The workflow will handle deployment automatically

## 🔄 Automation

### Workflow Triggers

- **📅 Scheduled:** Daily at 6 AM UTC
- **👆 Manual:** Via GitHub Actions UI ("Run workflow" button)
- **🔧 Automatic:** On changes to:
  - `tokenizer.py`
  - `.github/workflows/tokenizer.yml`
  - `repos.txt`

### Manual Execution

1. Go to **Actions** tab in GitHub
2. Select **"Token Telemetry"** workflow
3. Click **"Run workflow"**
4. Select branch and click **"Run workflow"**

## 📊 Output Format

### JSON Structure

```json
{
  "metadata": {
    "generated_at": "2025-06-17T14:00:00Z",
    "purpose": "Token analysis for AI context management",
    "usage_instructions": { /* AI guidance */ },
    "data_structure": { /* Format explanation */ }
  },
  "summary": {
    "total_repositories": 4,
    "total_files": 2123,
    "total_tokens": 4917390,
    "by_extension": {
      ".go": { "files": 1553, "tokens": 3904304 },
      ".md": { "files": 570, "tokens": 1013086 }
    }
  },
  "repositories": [
    {
      "directory": "celestia-core",
      "repository": {
        "name": "celestia-core",
        "url": "https://github.com/celestiaorg/celestia-core"
      },
      "total_files": 1179,
      "total_tokens": 3202991,
      "by_extension": { /* breakdown by file type */ },
      "files": [ /* individual file analysis */ ]
    }
  ]
}
```

## 🔍 Monitoring

### Workflow Status

Check workflow runs in the **Actions** tab to monitor:
- Execution success/failure
- Processing time
- Token count changes over time

### Error Handling

The system includes robust error handling:
- Repository cloning failures are logged but don't stop other repositories
- File encoding issues are skipped with warnings
- Network timeouts are retried automatically

## 🤝 Contributing

### Adding New File Types

Edit `tokenizer.py` to support additional file extensions:

```python
# In count_tokens_in_file function
if extension not in ['.go', '.md', '.rs', '.py']:  # Add new extensions
    return 0, extension
```

---

**Last Updated:** Auto-generated daily at 6 AM UTC  
**API Endpoint:** https://celestiaorg.github.io/tokenmetry/index.json
