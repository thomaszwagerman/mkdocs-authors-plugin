# Plugin Configuration

The `mkdocs-authors-plugin` offers a few configurable options that you can set in your main MkDocs project's `mkdocs.yml` file.

To configure the plugin, add it under the `plugins` section and provide the desired options:

```yaml
# mkdocs.yml
plugins:
  - search
  - authors_plugin:
      authors_file: custom_authors.yaml  # Optional: Default is '.authors.yml'
      output_page: team_members.md      # Optional: Default is 'authors.md'
```

### Options

* `authors_file` (default: `.authors.yml`)
    * Type: `string`
    * Description: Specifies the name of the YAML file that contains your authors' data. This file should be located in the root directory of your MkDocs documentation project (the same directory as your main `mkdocs.yml`).

* `output_page` (default: `authors.md`)
    * Type: `string`
    * Description: Defines the name of the Markdown file that the plugin will generate. This file will be placed in your `docs_dir` (e.g., `docs/authors.md`) and will contain the formatted author information. Ensure this page is referenced in your `nav` section in `mkdocs.yml`.
