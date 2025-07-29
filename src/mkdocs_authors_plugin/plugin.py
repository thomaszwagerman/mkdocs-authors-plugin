# mkdocs-authors-plugin/mkdocs_authors_plugin/plugin.py
import os
import yaml
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options as c
from mkdocs.structure.files import File


class AuthorsPlugin(BasePlugin):
    """
    MkDocs plugin to generate an authors page from a YAML file.
    """

    # Define configuration options for the plugin
    config_scheme = (
        ("authors_file", c.Type(str, default=".authors.yml")),
        ("output_page", c.Type(str, default="authors.md")),
    )

    def on_pre_build(self, config):
        """
        The 'on_pre_build' event is called once, before the documentation is built.
        This is where we'll generate our authors page content.
        """
        # Get the path to the authors YAML file, assumes in root of the project (ie one up from docs)
        authors_file_path = os.path.join(
            config["docs_dir"], "..", self.config["authors_file"]
        )

        # Get the path where the output Markdown page should be created
        output_page_path = os.path.join(config["docs_dir"], self.config["output_page"])

        authors_data = []
        if os.path.exists(authors_file_path):
            with open(authors_file_path, "r", encoding="utf-8") as f:
                try:
                    raw_data = yaml.safe_load(f)

                    if (
                        isinstance(raw_data, dict)
                        and "authors" in raw_data
                        and isinstance(raw_data["authors"], dict)
                    ):
                        for author_id, details in raw_data["authors"].items():
                            # Add the ID (key from the YAML) into the author's details dictionary
                            details["id"] = author_id
                            authors_data.append(details)
                    else:
                        print(
                            f"Warning: {self.config['authors_file']} should contain a dictionary with an 'authors' key at the top level."
                        )
                        authors_data = (
                            []
                        )  # Ensure it's an empty list if format is incorrect

                except yaml.YAMLError as e:
                    print(f"Error parsing {self.config['authors_file']}: {e}")
                    authors_data = []
        else:
            print(
                f"Warning: Authors file not found at {authors_file_path}. No authors page will be generated."
            )
            return  # Exit if the authors file doesn't exist

        # Generate Markdown content for the authors page
        markdown_content = "# Our Amazing Authors\n\n"
        if not authors_data:
            markdown_content += "No authors found or an error occurred while loading the authors data.\n"
        else:
            for author in authors_data:
                markdown_content += f"## {author.get('name', 'Unknown Author')}\n"

                if author.get("id"):
                    markdown_content += f"**ID:** `{author['id']}`\n"

                if author.get("affiliation"):
                    markdown_content += f"**Affiliation:** {author['affiliation']}\n"

                if author.get("description"):
                    markdown_content += f"\n> {author['description']}\n"

                if author.get("avatar"):
                    markdown_content += f"\n![{author.get('name', 'Avatar')} Avatar]({author['avatar']})\n"

                if author.get("email"):
                    markdown_content += (
                        f"**Email:** [{author['email']}](mailto:{author['email']})\n"
                    )

                social_links = []
                if author.get("github"):
                    social_links.append(
                        f"[GitHub](https://github.com/{author['github']})"
                    )
                if author.get("linkedin"):
                    social_links.append(
                        f"[LinkedIn](https://www.linkedin.com/in/{author['linkedin']})"
                    )
                if author.get("twitter"):
                    social_links.append(
                        f"[Twitter](https://twitter.com/{author['twitter']})"
                    )

                if social_links:
                    markdown_content += (
                        "\n**Connect:** " + " | ".join(social_links) + "\n"
                    )

                markdown_content += "\n---\n\n"  # Separator for each author

        # Write the generated Markdown content to the output file
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_page_path), exist_ok=True)
        with open(output_page_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"Authors page generated at: {output_page_path}")

    def on_files(self, files, config):
        """
        The 'on_files' event is called after the files are gathered.
        We need to ensure our generated authors.md file is included in the build.
        """
        # Get the path where the output Markdown page was created
        output_page_name = self.config["output_page"]
        output_page_src_path = os.path.join(config["docs_dir"], output_page_name)

        # Check if the file already exists in the files collection to avoid duplicates
        # This is important if authors.md was already listed in mkdocs.yml nav
        if not any(f.src_path == output_page_name for f in files):
            # Create a new File object for our generated page
            # The 'src_path' should be relative to docs_dir
            generated_file = File(
                path=output_page_name,
                src_dir=config["docs_dir"],
                dest_dir=config["site_dir"],
                use_directory_urls=config["use_directory_urls"],
            )
            files.append(generated_file)
            print(f"Added generated '{output_page_name}' to MkDocs files.")
        return files
