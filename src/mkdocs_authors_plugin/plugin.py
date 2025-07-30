import os
import yaml
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.config import config_options as c
from mkdocs.structure.files import File
from mkdocs.structure.pages import Page


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
        The 'on_pre_build' event is called once, before the documentation is built.
        This is where we'll generate our authors page content.
        """
        authors_file_path = os.path.join(
            config["docs_dir"], "..", self.config["authors_file"]
        )

        authors_data = []
        page_parameters = {}

        if os.path.exists(authors_file_path):
            with open(authors_file_path, "r", encoding="utf-8") as f:
                try:
                    raw_data = yaml.safe_load(f)

                    if isinstance(raw_data, dict):
                        if self.config["page_params_key"] in raw_data and isinstance(
                            raw_data[self.config["page_params_key"]], dict
                        ):
                            page_parameters = raw_data[self.config["page_params_key"]]

                        if "authors" in raw_data and isinstance(
                            raw_data["authors"], dict
                        ):
                            for author_id, details in raw_data["authors"].items():
                                details["id"] = author_id
                                authors_data.append(details)
                        else:
                            log.warning(
                                f"'{self.config['authors_file']}' does not contain an 'authors' key at the top level, or it's not a dictionary. No authors will be listed."
                            )
                            authors_data = []
                    else:
                        log.warning(
                            f"'{self.config['authors_file']}' should contain a dictionary at the top level. No authors or page parameters will be loaded."
                        )
                        authors_data = []
                        page_parameters = {}

                except yaml.YAMLError as e:
                    log.error(f"Error parsing '{self.config['authors_file']}': {e}")
                    authors_data = []
                    page_parameters = {}
        else:
            log.warning(
                f"Authors file not found at '{authors_file_path}'. No authors page will be generated."
            )
            self.authors_markdown_content = "No authors file found. Please create a '.authors.yml' file in your project root."
            return

        page_title = page_parameters.get("title", "Our Amazing Authors")
        page_description = page_parameters.get("description")

        # Get avatar styling from page_parameters, with defaults
        avatar_size = page_parameters.get(
            "avatar_size", 100
        )  # Default if not specified in page_params
        avatar_shape = page_parameters.get(
            "avatar_shape", "square"
        )  # Default if not specified in page_params

        markdown_content = f"# {page_title}\n\n"
        if page_description:
            markdown_content += f"{page_description}\n\n"

        if not authors_data:
            markdown_content += "No authors found or an error occurred while loading the authors data.\n"
        else:
            for author in authors_data:
                markdown_content += f"## {author.get('name', 'Unknown Author')}\n"

                if author.get("avatar"):
                    avatar_url = author["avatar"]
                    author_name = author.get("name", "Avatar")

                    style_attributes = f"width: {avatar_size}px; height: {avatar_size}px; object-fit: cover;"
                    if avatar_shape == "circle":
                        style_attributes += " border-radius: 50%;"
                    else:  # Default or 'square'
                        style_attributes += " border-radius: 0;"

                    style_attributes += " display: block; margin: 0 auto;"

                    markdown_content += f'\n<p style="text-align: center;"><img src="{avatar_url}" alt="{author_name} Avatar" style="{style_attributes}"></p>\n'

                if author.get("affiliation"):
                    markdown_content += f"**Affiliation:** {author['affiliation']}\n"

                if author.get("description"):
                    markdown_content += f"\n {author['description']}\n"

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

                markdown_content += "\n---\n\n"

        self.authors_markdown_content = markdown_content
        log.info(f"Authors page content generated for '{self.config['output_page']}'.")

    def on_files(self, files, config):
        """
        The 'on_files' event is called after the files are gathered.
        We need to ensure our generated authors.md file is included in the build.
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
        The 'on_page_read_source' event is called when MkDocs reads the source
        for a page. We'll intercept our generated page and provide its content.
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
