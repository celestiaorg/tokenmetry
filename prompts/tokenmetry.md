# Prompt for AI IDE Agents: Interacting with CelestiaOrg Tokenmetry Data

You have access to tokenization data for CelestiaOrg GitHub repositories. This data is structured to provide both high-level summaries and detailed breakdowns. Here's how to use it:

## 1. Start with the Meta-Index File

The primary entry point is the meta-index file:

-   **URL:** `https://celestiaorg.github.io/tokenmetry/index.json`

This `index.json` file is relatively small and contains:
    -   `metadata`: Information about the data generation, version, format, and detailed usage instructions (including this guide).
    -   `summary`: Aggregated statistics across all processed repositories (e.g., `total_tokens_across_all_repos`, `by_extension_across_all_repos`).
    -   `repositories`: An array where each element is a summary for a specific repository. Each repository summary includes:
        -   `name`: Repository name (e.g., "celestia-app").
        -   `url`: GitHub URL of the repository.
        -   `total_files`: Total number of tokenized files in this repository.
        -   `total_tokens`: Total tokens in this repository.
        -   `by_extension`: A summary of file counts and token counts per language (e.g., `.go`, `.md`, `.rs`, `.sol`) for this repository.
        -   `data_file`: A relative path to a JSON file containing detailed tokenization data for *only this repository* (e.g., `repository_data/celestia-app.json`).
        -   `data_file_full_url`: The full, direct URL to the detailed JSON data file for this repository (e.g., `https://celestiaorg.github.io/tokenmetry/repository_data/celestia-app.json`). **This is the recommended field to use for direct access.**
        -   `error`: Null or an error message if processing failed for this repository.

**Always fetch and parse this `index.json` (meta-index) first.**

## 2. Accessing Detailed Repository Data

To get the detailed file-by-file breakdown for a specific repository:

1.  In the `index.json` (meta-index), find the desired repository within the `repositories` array.
2.  Use the value of its `data_file_full_url` field. This provides the direct URL to the detailed data.
    (Alternatively, you can construct the URL using the `data_file` relative path: `https://celestiaorg.github.io/tokenmetry/` + `data_file_path`)
3.  Fetch and parse this individual repository JSON file using the full URL.

## 3. Structure of Individual Repository JSON Files

Each individual repository JSON file (e.g., `repository_data/celestia-core.json`) contains:

-   `repository`: An object with `name` and `url`.
-   `directory`: The name of the repository (used as the base for file paths).
-   `total_files`: Total tokenized files in this repository.
-   `total_tokens`: Total tokens in this repository.
-   `by_extension`: Detailed breakdown by file type (e.g., `.go`, `.md`) with file counts and token counts for each extension in this repository.
-   `files`: An array where each element represents a tokenized file:
    -   `path`: Relative path of the file within the repository.
    -   `extension`: File extension (e.g., ".go").
    -   `tokens`: Number of tokens in this file.
-   `error`: Null or an error message if processing this specific repository had issues.

## 4. Example Queries / Tasks

Here are some examples of how you can use this data:

**Using `index.json` (Meta-Index):**

*   "What is the total token count for all analyzed CelestiaOrg repositories?"
    *   *Action:* Read `summary.total_tokens_across_all_repos` from `index.json`.
*   "List all repositories that have been analyzed and their individual total token counts."
    *   *Action:* Iterate through the `repositories` array in `index.json`. For each entry, display `name` and `total_tokens`.
*   "Which repository has the most Solidity (`.sol`) tokens?"
    *   *Action:* Iterate through `repositories` in `index.json`. For each, check `by_extension['.sol']['tokens']`. Find the maximum.
*   "What is the overall breakdown of tokens by language (Go, Markdown, Rust, Solidity) across all projects?"
    *   *Action:* Inspect `summary.by_extension_across_all_repos` from `index.json`.
*   "Get the direct URL for the detailed token data of the 'celestia-node' repository."
    *   *Action:* In `index.json`, find the entry for 'celestia-node' in the `repositories` array. Retrieve the value of `data_file_full_url`.

**Using Individual Repository JSON Files (after finding them via `index.json` and using `data_file_full_url`):**

*   "What are the 5 largest Go files by token count in the 'celestia-app' repository?"
    1.  *Action:* In `index.json`, find the entry for 'celestia-app' and get its `data_file_full_url`.
    2.  *Action:* Fetch the detailed JSON for 'celestia-app' using this URL.
    3.  *Action:* In the detailed JSON, filter the `files` array for `extension == ".go"`, sort by `tokens` descending, and take the top 5.
*   "How many Markdown files are in the 'docs' repository?"
    1.  *Action:* In `index.json`, find 'docs', get its `data_file_full_url`.
    2.  *Action:* Fetch its detailed JSON.
    3.  *Action:* Look at `by_extension['.md']['files']` in the detailed JSON (or this info is also available directly in the `repositories` array of `index.json`).
*   "Provide a list of all Rust files and their token counts in the 'nitro' repository."
    1.  *Action:* Find 'nitro' in `index.json`, get `data_file_full_url`.
    2.  *Action:* Fetch detailed JSON for 'nitro'.
    3.  *Action:* Filter `files` array for `extension == ".rs"` and list `path` and `tokens`.

## 5. Important Considerations
## 5. Important Considerations

*   **Start with `index.json`:** This file is small and gives you the necessary overview and pointers, including direct full URLs to detailed data.
*   **Selective Fetching:** Only fetch detailed repository JSON files when you need that level of detail for a specific repository. This saves processing time and context window space.
*   **Error Handling:** Check the `error` field in both the meta-index repository entries and the detailed repository JSON files.

This structured approach allows for efficient and targeted access to the tokenmetry data.
