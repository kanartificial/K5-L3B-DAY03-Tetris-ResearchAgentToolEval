---
name: save_note
track: core
kind: action
provider: local_json_folder
requires_env: []
inputs: [title, content, source_url, confirmed]
outputs: [status, note_id, error, message]
side_effect: local_file_write
requires_confirmation: true
---
# save_note

Saves a research finding and its source URL as a UTF-8 JSON file under
`starter_v0/notes/<note_id>.json`. No external API or additional dependency is used.
The directory is created on the first save. Each call creates a new note; it does
not overwrite or deduplicate existing notes. The tool generates the ID and path;
the model cannot choose a file path.

## When to use

Use when the user explicitly asks to save a research finding locally. Obtain any
missing title, content, or source URL with `clarify`; never invent a source URL.
Only set `confirmed=true` after explicit user confirmation of the save. If the
intent to save is unclear, ask with `clarify(response_type="yes_no")` first.
Do not use for web search, retrieving saved notes, formatting a digest, or sending
to Telegram. The tool stores supplied content; it does not fetch or verify the URL.

## Inputs and results

- `title`, `content`, `source_url`: non-empty strings; outer whitespace is stripped.
- `confirmed`: boolean, default `false`. Without confirmation, returns
  `status="needs_confirmation"` without creating a directory or file.
- Success: `{tool: "save_note", status: "saved", note_id: "<generated ID>"}`.
  The JSON file contains `note_id`, `title`, `content`, and `source_url`.
- Invalid input or a storage failure returns `{tool, error, message}` using the
  shared error convention. A failed save must not be reported as successful.

Saved notes persist on the local filesystem and are not encrypted. Avoid storing
secrets or sensitive personal data. Back up or remove notes separately as needed.

## Example

```python
from tools import TOOL_FUNCTIONS

# Only after the user explicitly confirms the save:
result = TOOL_FUNCTIONS["save_note"](
    title="Research finding",
    content="The paper reports a 12% improvement.",
    source_url="https://example.org/paper",
    confirmed=True,
)
```

Verified with a temporary storage directory: UTF-8 content and source are
persisted unchanged apart from outer whitespace; repeated saves use independent
IDs; unconfirmed or invalid calls do not write notes; storage failures return an
error dict. The tool contract suite passes. This does not establish model routing
accuracy; measure that separately with an eval case.

## Unit tests

```bash
python -m pytest tests/test_tools_todo.py -k save_note -v
```
