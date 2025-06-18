#!/usr/bin/env python3
"""
Token Telemetry Script

This script tokenizes text content from files, directories, or repositories and counts tokens
using Hugging Face tokenizers library.

Usage:
    python tokenizer_script.py --file path/to/file.go
    python tokenizer_script.py --directory path/to/repo
    python tokenizer_script.py --repo https://github.com/celestiaorg/celestia-app.git
    python tokenizer_script.py --celestia-repos  # Process all predefined repos
    python tokenizer_script.py --text "Some text to tokenize"
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from transformers import GPT2TokenizerFast
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("Warning: transformers library not found.")

try:
    import git
    HAS_GIT = True
except ImportError:
    HAS_GIT = False
    print("Warning: GitPython not found. Repository cloning will not work.")

def load_repositories_from_file(file_path: str) -> List[str]:
    """
    Load repository URLs from a text file.
    
    Args:
        file_path: Path to the file containing repository URLs
        
    Returns:
        List of repository URLs
    """
    repos = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    repos.append(line)
    except FileNotFoundError:
        raise FileNotFoundError(f"Repository file not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading repository file {file_path}: {e}")
    
    return repos


def load_gpt2_tokenizer():
    """Load GPT-2 tokenizer if transformers is available."""
    if HAS_TRANSFORMERS:
        return GPT2TokenizerFast.from_pretrained('gpt2')
    else:
        # Fallback: create a simple BPE tokenizer
        tokenizer = Tokenizer(BPE(unk_token="<unk>"))
        tokenizer.pre_tokenizer = Whitespace()
        return tokenizer


def count_tokens_in_text(text: str, tokenizer) -> int:
    """Count tokens in the given text."""
    if HAS_TRANSFORMERS:
        # Using transformers tokenizer
        tokens = tokenizer.encode(text)
        return len(tokens)
    else:
        # Using basic tokenizer
        encoding = tokenizer.encode(text)
        return len(encoding.tokens)


def count_tokens_in_file(file_path: str, tokenizer) -> tuple[int, str]:
    """
    Count tokens in a file.
    
    Returns:
        tuple: (token_count, file_extension)
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check if it's a supported file type
    extension = path.suffix.lower()
    if extension not in ['.go', '.md', '.rs', '.sol']:
        return 0, extension  # Skip unsupported files silently
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        token_count = count_tokens_in_text(content, tokenizer)
        return token_count, extension
        
    except (UnicodeDecodeError, PermissionError):
        print(f"Warning: Could not read {file_path}. Skipping.")
        return 0, extension


def process_directory(directory_path: str, tokenizer) -> Dict:
    """
    Process all .go and .md files in a directory.
    
    Returns:
        dict: Results with file counts and token counts by extension
    """
    path = Path(directory_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")
    
    results = {
        'directory': str(path),
        'total_files': 0,
        'total_tokens': 0,
        'by_extension': {
            '.go': {'files': 0, 'tokens': 0},
            '.md': {'files': 0, 'tokens': 0},
            '.rs': {'files': 0, 'tokens': 0},
            '.sol': {'files': 0, 'tokens': 0}
        },
        'files': []
    }
    
    # Find all .go, .md, .rs, and .sol files
    for pattern in ['**/*.go', '**/*.md', '**/*.rs', '**/*.sol']:
        for file_path in path.glob(pattern):
            if file_path.is_file():
                token_count, extension = count_tokens_in_file(str(file_path), tokenizer)
                
                if token_count > 0:  # Only count successfully processed files
                    results['total_files'] += 1
                    results['total_tokens'] += token_count
                    
                    if extension in results['by_extension']:
                        results['by_extension'][extension]['files'] += 1
                        results['by_extension'][extension]['tokens'] += token_count
                    
                    # Store individual file info
                    relative_path = file_path.relative_to(path)
                    results['files'].append({
                        'path': str(relative_path),
                        'extension': extension,
                        'tokens': token_count
                    })
    
    return results


def clone_repository(repo_url: str, temp_dir: Path) -> Path:
    """
    Clone a repository to a temporary directory.
    
    Returns:
        Path: Path to the cloned repository
    """
    if not HAS_GIT:
        raise RuntimeError("GitPython is required for repository cloning. Install with: poetry add gitpython")
    
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    repo_path = temp_dir / repo_name
    
    print(f"Cloning {repo_url}...")
    try:
        git.Repo.clone_from(repo_url, repo_path, depth=1)  # Shallow clone for speed
        return repo_path
    except git.exc.GitCommandError as e:
        print(f"Error cloning {repo_url}: {e}")
        raise


def process_repository(repo_url: str, tokenizer) -> Dict:
    """
    Clone and process a single repository.
    
    Returns:
        dict: Processing results for the repository
    """
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        try:
            repo_path = clone_repository(repo_url, temp_path)
            results = process_directory(str(repo_path), tokenizer)
            
            # Replace the temporary directory path with just the repo name
            results['directory'] = repo_name
            
            # Add repository metadata
            results['repository'] = {
                'name': repo_name,
                'url': repo_url
            }
            
            return results
            
        except Exception as e:
            print(f"✗ Failed to process {repo_name}: {e}")
            return {
                'repository': {'name': repo_name, 'url': repo_url},
                'error': str(e),
                'total_files': 0,
                'total_tokens': 0
            }


def process_multiple_repositories(repo_urls: List[str], tokenizer, output_base_path: Path) -> Dict:
    """
    Process multiple repositories, saving individual repo data and returning meta-index data.
    
    Args:
        repo_urls: List of repository URLs.
        tokenizer: The tokenizer instance.
        output_base_path: The base path where 'meta_index.json' and 'repository_data/' will be stored.
        
    Returns:
        dict: Data for the meta_index.json file.
    """
    repository_data_dir = output_base_path / "repository_data"
    repository_data_dir.mkdir(parents=True, exist_ok=True)

    meta_index_data = {
        'summary': {
            'total_repositories_configured': len(repo_urls),
            'successful_repositories_processed': 0,
            'total_files_across_all_repos': 0,
            'total_tokens_across_all_repos': 0,
            'by_extension_across_all_repos': {
                '.go': {'files': 0, 'tokens': 0},
                '.md': {'files': 0, 'tokens': 0},
                '.rs': {'files': 0, 'tokens': 0},
                '.sol': {'files': 0, 'tokens': 0}
            }
        },
        'repositories': [] # List of summaries for each repo, pointing to their individual files
    }
    
    for repo_url in repo_urls:
        print(f"\nProcessing {repo_url}...")
        # repo_results contains detailed file list for this specific repo
        repo_results = process_repository(repo_url, tokenizer) 
        
        repo_name = repo_results.get('repository', {}).get('name', 'unknown_repo')
        individual_repo_filename = f"{repo_name}.json"
        individual_repo_filepath = repository_data_dir / individual_repo_filename
        
        if 'error' not in repo_results:
            # Save detailed data for this specific repository
            try:
                with open(individual_repo_filepath, 'w') as f:
                    json.dump(repo_results, f, indent=2)
                print(f"  Detailed data saved to: {individual_repo_filepath}")
            except Exception as e:
                print(f"  Error saving detailed data for {repo_name}: {e}")
                # Continue processing other repos, but mark this one as having an issue with saving
                repo_results['error'] = repo_results.get('error', '') + f"; Failed to save individual JSON: {e}"

        # Prepare summary for this repo to be included in meta_index.json
        repo_summary_for_meta = {
            'name': repo_name,
            'url': repo_url,
            'data_file': f"repository_data/{individual_repo_filename}", # Relative path for GitHub Pages
            'total_files': repo_results.get('total_files', 0),
            'total_tokens': repo_results.get('total_tokens', 0),
            'by_extension': repo_results.get('by_extension', {}),
            'error': repo_results.get('error', None)
        }
        meta_index_data['repositories'].append(repo_summary_for_meta)
        
        # Update overall summary in meta_index_data if processing was successful (error field is not present or empty)
        if not repo_summary_for_meta['error']:
            meta_index_data['summary']['successful_repositories_processed'] += 1
            meta_index_data['summary']['total_files_across_all_repos'] += repo_summary_for_meta['total_files']
            meta_index_data['summary']['total_tokens_across_all_repos'] += repo_summary_for_meta['total_tokens']
            
            for ext, data in repo_summary_for_meta['by_extension'].items():
                if ext in meta_index_data['summary']['by_extension_across_all_repos']:
                    meta_index_data['summary']['by_extension_across_all_repos'][ext]['files'] += data.get('files', 0)
                    meta_index_data['summary']['by_extension_across_all_repos'][ext]['tokens'] += data.get('tokens', 0)
            
            print(f"✓ {repo_name}: {repo_summary_for_meta['total_files']} files, {repo_summary_for_meta['total_tokens']} tokens")
        else:
            print(f"✗ {repo_name}: Processing encountered an error: {repo_summary_for_meta['error']}")
            
    return meta_index_data


def main():
    parser = argparse.ArgumentParser(description='Count tokens in text, files, directories, or repositories')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', help='Path to file to tokenize')
    group.add_argument('--directory', '-d', help='Path to directory to process')
    group.add_argument('--repo', '-r', help='Repository URL to clone and process')
    group.add_argument('--celestia-repos', action='store_true', help='Process all CelestiaOrg repositories from repos.txt')
    group.add_argument('--text', '-t', help='Text string to tokenize')
    
    parser.add_argument('--repo-file', default='repos.txt', help='Path to file containing repository URLs (default: repos.txt)')
    parser.add_argument('--output', '-o', help='Output JSON file path (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed file-by-file results')
    
    args = parser.parse_args()
    
    print("Loading tokenizer...")
    tokenizer = load_gpt2_tokenizer()
    
    if args.file:
        try:
            token_count, extension = count_tokens_in_file(args.file, tokenizer)
            print(f"File: {args.file}")
            print(f"Extension: {extension}")
            print(f"Token count: {token_count}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.directory:
        try:
            results = process_directory(args.directory, tokenizer)
            print(f"\nDirectory: {results['directory']}")
            print(f"Total files: {results['total_files']}")
            print(f"Total tokens: {results['total_tokens']:,}")
            print(f"Go files: {results['by_extension']['.go']['files']} files, {results['by_extension']['.go']['tokens']:,} tokens")
            print(f"Markdown files: {results['by_extension']['.md']['files']} files, {results['by_extension']['.md']['tokens']:,} tokens")
            print(f"Rust files: {results['by_extension']['.rs']['files']} files, {results['by_extension']['.rs']['tokens']:,} tokens")
            print(f"Solidity files: {results['by_extension']['.sol']['files']} files, {results['by_extension']['.sol']['tokens']:,} tokens")
            
            if args.verbose:
                print("\nFile details:")
                for file_info in results['files']:
                    print(f"  {file_info['path']}: {file_info['tokens']} tokens")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\nDetailed results saved to: {args.output}")
                
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.repo:
        try:
            results = process_repository(args.repo, tokenizer)
            if 'error' in results:
                print(f"Failed to process repository: {results['error']}")
                sys.exit(1)
            
            print(f"\nRepository: {results['repository']['name']}")
            print(f"URL: {results['repository']['url']}")
            print(f"Total files: {results['total_files']}")
            print(f"Total tokens: {results['total_tokens']:,}")
            print(f"Go files: {results['by_extension']['.go']['files']} files, {results['by_extension']['.go']['tokens']:,} tokens")
            print(f"Markdown files: {results['by_extension']['.md']['files']} files, {results['by_extension']['.md']['tokens']:,} tokens")
            print(f"Rust files: {results['by_extension']['.rs']['files']} files, {results['by_extension']['.rs']['tokens']:,} tokens")
            print(f"Solidity files: {results['by_extension']['.sol']['files']} files, {results['by_extension']['.sol']['tokens']:,} tokens")
            
            if args.verbose:
                print("\nFile details:")
                for file_info in results['files']:
                    print(f"  {file_info['path']}: {file_info['tokens']} tokens")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\nDetailed results saved to: {args.output}")
                
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.celestia_repos:
        try:
            # Load repositories from file
            repo_urls = load_repositories_from_file(args.repo_file)
            print(f"Loaded {len(repo_urls)} repositories from {args.repo_file}")

            if not args.output:
                print("Error: --output path is required when using --celestia-repos for meta_index.json.")
                sys.exit(1)
            
            output_meta_index_path = Path(args.output)
            # The script will create a 'repository_data' subdirectory within the parent of the --output file.
            # E.g., if --output is _site/meta_index.json, individual files go into _site/repository_data/
            output_base_dir = output_meta_index_path.parent
            output_base_dir.mkdir(parents=True, exist_ok=True)

            meta_index_content = process_multiple_repositories(repo_urls, tokenizer, output_base_dir)
            
            try:
                with open(output_meta_index_path, 'w') as f:
                    json.dump(meta_index_content, f, indent=2)
                print(f"\nMeta-index saved to: {output_meta_index_path}")
            except Exception as e:
                print(f"Error saving meta-index to {output_meta_index_path}: {e}")
                sys.exit(1)

            print("\n" + "=" * 60)
            print("CELESTIA REPOSITORIES META-INDEX SUMMARY")
            print("=" * 60)
            summary = meta_index_content['summary']
            print(f"Repositories configured: {summary['total_repositories_configured']}")
            print(f"Repositories successfully processed: {summary['successful_repositories_processed']}")
            print(f"Total files across all processed repos: {summary['total_files_across_all_repos']:,}")
            print(f"Total tokens across all processed repos: {summary['total_tokens_across_all_repos']:,}")
            
            for ext_name, data in summary['by_extension_across_all_repos'].items():
                 print(f"{ext_name.replace('.', '').capitalize()} files: {data['files']:,} files, {data['tokens']:,} tokens")

            if args.verbose:
                print("\nIndividual Repository Summaries (from meta-index):")
                for repo_summary in meta_index_content['repositories']:
                    status = "OK" if not repo_summary.get('error') else f"ERROR ({repo_summary['error']})"
                    print(f"  - {repo_summary['name']}: {repo_summary['total_tokens']:,} tokens in {repo_summary['total_files']} files. Status: {status}. Data: {repo_summary['data_file']}")
            
            return 0 if summary['successful_repositories_processed'] > 0 else 1
                
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.text:
        token_count = count_tokens_in_text(args.text, tokenizer)
        print(f"Text: {args.text[:50]}{'...' if len(args.text) > 50 else ''}")
        print(f"Token count: {token_count}")


if __name__ == "__main__":
    main()
