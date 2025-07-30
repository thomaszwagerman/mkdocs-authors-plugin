import os
import yaml
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.config import config_options as c
from mkdocs.structure.files import File


log = get_plugin_logger(__name__)


class AuthorsPlugin(BasePlugin):
    """
    MkDocs plugin to generate an authors page from a YAML file.
    """

    config_scheme = (
        ("authors_file", c.Type(str, default=".authors.yml")),
        ("output_page", c.Type(str, default="authors.md")),
        ("page_params_key", c.Type(str, default="page_params")),
    )

    def on_pre_build(self, config):
        """
        Generates the authors page content from the YAML file before the build.
        """
        authors_file_path = os.path.join(
            config["docs_dir"], "..", self.config["authors_file"]
        )
        authors_data = []
        page_parameters = {}

        if not os.path.exists(authors_file_path):
            log.warning(
                f"Authors file not found at '{authors_file_path}'. No authors page will be generated."
            )
            self.authors_markdown_content = "No authors file found. Please create a '.authors.yml' file in your project root."
            return

        try:
            with open(authors_file_path, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)

            if isinstance(raw_data, dict):
                potential_page_params = raw_data.get(self.config["page_params_key"])
                if isinstance(potential_page_params, dict):
                    page_parameters = potential_page_params
                else:
                    log.warning(
                        f"'{self.config['page_params_key']}' in '{self.config['authors_file']}' is not a dictionary. Page parameters will be ignored."
                    )
                    page_parameters = {}

                authors_dict = raw_data.get("authors", {})

                if isinstance(authors_dict, dict):
                    authors_data = [
                        {"id": aid, **details} for aid, details in authors_dict.items()
                    ]
                else:
                    log.warning(
                        f"'{self.config['authors_file']}' does not contain an 'authors' key as a dictionary. No authors will be listed."
                    )
            else:
                log.warning(
                    f"'{self.config['authors_file']}' should contain a dictionary at the top level. No authors or page parameters will be loaded."
                )
        except yaml.YAMLError as e:
            log.error(f"Error parsing '{self.config['authors_file']}': {e}")
        except Exception as e:
            log.error(f"An unexpected error occurred while loading authors data: {e}")

        self._generate_markdown_content(authors_data, page_parameters)
        log.info(f"Authors page content generated for '{self.config['output_page']}'.")

    def _generate_markdown_content(self, authors_data, page_parameters):
        """Helper to generate the markdown string."""
        page_title = page_parameters.get("title", "Our Amazing Authors")
        page_description = page_parameters.get("description", "")
        avatar_size = page_parameters.get("avatar_size", 100)
        avatar_shape = page_parameters.get("avatar_shape", "square")
        avatar_align = page_parameters.get("avatar_align", "center")

        markdown_parts = [f"# {page_title}\n\n"]
        if page_description:
            markdown_parts.append(f"{page_description}\n\n")

        if not authors_data:
            markdown_parts.append(
                "No authors found or an error occurred while loading the authors data.\n"
            )
        else:
            for author in authors_data:
                markdown_parts.append(f"## {author.get('name', 'Unknown Author')}\n")

                avatar_html = self._get_avatar_html(
                    author, avatar_size, avatar_shape, avatar_align
                )
                if avatar_align not in [
                    "left",
                    "right",
                ]:  # Center-aligned avatar needs to be handled as a block
                    if avatar_html:
                        markdown_parts.append(
                            f'<p style="text-align: center;">{avatar_html}</p>\n'
                        )
                    avatar_html = ""  # Clear for other alignments

                # Add avatar for left/right float and then other details
                if avatar_html:
                    markdown_parts.append(avatar_html)

                if author.get("affiliation"):
                    markdown_parts.append(f"**Affiliation:** {author['affiliation']}\n")

                if author.get("description"):
                    markdown_parts.append(f"\n{author['description']}\n")

                if author.get("email"):
                    markdown_parts.append(
                        f"\n**Email:** [{author['email']}](mailto:{author['email']})\n"
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
                    markdown_parts.append(
                        "\n**Connect:** " + " | ".join(social_links) + "\n"
                    )

                if avatar_align in ["left", "right"]:
                    markdown_parts.append('<div style="clear: both;"></div>\n')

                markdown_parts.append("\n---\n\n")

        self.authors_markdown_content = "".join(markdown_parts)

    def _get_avatar_html(self, author, size, shape, align):
        """Generates the HTML for the author's avatar."""
        if not author.get("avatar"):
            return ""

        avatar_url = author["avatar"]
        author_name = author.get("name", "Avatar")

        style_attributes = f"width: {size}px; height: {size}px; object-fit: cover;"
        style_attributes += (
            " border-radius: 50%;" if shape == "circle" else " border-radius: 0;"
        )

        if align == "left":
            style_attributes += " float: left; margin-right: 15px; margin-bottom: 10px;"
        elif align == "right":
            style_attributes += " float: right; margin-left: 15px; margin-bottom: 10px;"
        elif align == "center":
            style_attributes += " display: block; margin: 0 auto 10px auto;"

        return f'<img src="{avatar_url}" alt="{author_name} Avatar" style="{style_attributes}">'

    def on_files(self, files, config):
        """
        Ensures the generated authors.md file is included in the MkDocs build.
        """
        output_page_name = self.config["output_page"]
        if not any(f.src_path == output_page_name for f in files):
            generated_file = File(
                path=output_page_name,
                src_dir=config["docs_dir"],
                dest_dir=config["site_dir"],
                use_directory_urls=config["use_directory_urls"],
            )
            files.append(generated_file)
            log.info(f"Added generated '{output_page_name}' to MkDocs files.")
        return files

    def on_page_read_source(self, page, config):
        """
        Intercepts the generated page and provides its content.
        """
        output_page_name = self.config["output_page"]
        if page.file.src_path == output_page_name:
            if hasattr(self, "authors_markdown_content"):
                return self.authors_markdown_content
            else:
                log.error(
                    "Authors page content not available when 'on_page_read_source' was called."
                )
                return "Error: Authors page content not available."
        return None
