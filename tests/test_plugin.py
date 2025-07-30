# mkdocs-authors-plugin/tests/test_plugin.py
import unittest
import os
import tempfile
import shutil
from mkdocs.config import config_options as c
from mkdocs.config.base import Config
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

# Import the plugin class from your package
from mkdocs_authors_plugin.plugin import AuthorsPlugin


class TestAuthorsPlugin(unittest.TestCase):
    """
    Test suite for the AuthorsPlugin.

    This class contains unit tests to verify the functionality of the
    MkDocs AuthorsPlugin, including successful page generation, handling
    of missing or malformed YAML files, and correct file management
    within MkDocs' build process, and flexibility for page parameters.
    """

    def setUp(self):
        """
        Set up a temporary directory and mock MkDocs environment for each test.

        This method creates a temporary directory structure mimicking an MkDocs
        project (with 'docs' and 'site' directories) and initializes a mock
        MkDocs Config object. It also instantiates the AuthorsPlugin and
        loads its configuration.
        """
        self.tmp_dir = tempfile.mkdtemp()
        self.docs_dir = os.path.join(self.tmp_dir, "docs")
        os.makedirs(self.docs_dir)
        self.site_dir = os.path.join(self.tmp_dir, "site")
        os.makedirs(self.site_dir)

        # Mock MkDocs config
        self.config = Config(
            schema=(
                ("docs_dir", c.Dir(default="docs")),
                ("site_dir", c.Dir(default="site")),
                ("use_directory_urls", c.Type(bool, default=True)),
                (
                    "plugins",
                    c.ListOfItems(c.Type(str)),
                ),
            )
        )
        self.config.load_dict(
            {
                "docs_dir": self.docs_dir,
                "site_dir": self.site_dir,
                "plugins": ["authors_plugin"],
            }
        )
        self.config.validate()

        self.plugin = AuthorsPlugin()
        self.plugin.load_config(
            {
                "authors_file": ".authors.yml",
                "output_page": "authors.md",
                "page_params_key": "page_params",
            }
        )

    def tearDown(self):
        """
        Clean up the temporary directory after each test.

        This method removes the temporary directory and all its contents
        created during the test setup, ensuring a clean state for subsequent tests.
        """
        shutil.rmtree(self.tmp_dir)

    def _create_authors_yml(self, content):
        """
        Helper function to create the .authors.yml file with given content.

        Args:
            content (str): The YAML content to write to the .authors.yml file.

        Returns:
            str: The full path to the created .authors.yml file.
        """
        authors_yml_path = os.path.join(self.tmp_dir, ".authors.yml")
        with open(authors_yml_path, "w", encoding="utf-8") as f:
            f.write(content)
        return authors_yml_path

    def _get_generated_authors_md_content(self):
        """
        Helper function to simulate how MkDocs would get the content of
        the generated authors.md file by calling on_page_read_source.

        Returns:
            str or None: The content of the authors.md page if generated, otherwise None.
        """
        # Create a mock File object for authors.md
        authors_file = File(
            path="authors.md",
            src_dir=self.docs_dir,
            dest_dir=self.site_dir,
            use_directory_urls=self.config["use_directory_urls"],
        )
        # Create a mock Page object using the File
        authors_page = Page("authors", authors_file, self.config)

        # Call the plugin's on_page_read_source hook
        return self.plugin.on_page_read_source(authors_page, self.config)

    def test_authors_page_generation_success(self):
        """
        Test that the authors page is generated correctly with valid data.

        This test simulates a successful scenario where a well-formed
        .authors.yml file is provided, and verifies that the plugin
        generates the authors.md file with the expected Markdown content,
        including all specified author details and formatting.
        """
        yml_content = """
authors:
  author_one:
    name: Author One
    description: Owner
    avatar: headshot_one.png
    affiliation: British Antarctic Survey
    email: author.one@example.com
    github: authorone
    linkedin: author-one-profile
    twitter: author_one_dev
  author_two:
    name: Author Two
    description: Maintainer
    avatar: headshot_two.png
    affiliation: UK Centre for Ecology & Hydrology
        """
        self._create_authors_yml(yml_content)

        # Simulate on_pre_build hook to generate content
        self.plugin.on_pre_build(self.config)

        # Get the generated Markdown content via on_page_read_source simulation
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn("# Our Amazing Authors", generated_md)  # Default title
        self.assertIn("## Author One", generated_md)
        self.assertIn("**Affiliation:** British Antarctic Survey", generated_md)
        self.assertIn("Owner", generated_md)
        self.assertIn(
            "**Email:** [author.one@example.com](mailto:author.one@example.com)",
            generated_md,
        )
        self.assertIn("[GitHub](https://github.com/authorone)", generated_md)
        self.assertIn(
            "[LinkedIn](https://www.linkedin.com/in/author-one-profile)", generated_md
        )
        self.assertIn("[Twitter](https://twitter.com/author_one_dev)", generated_md)
        self.assertIn("## Author Two", generated_md)
        self.assertIn(
            "**Affiliation:** UK Centre for Ecology & Hydrology", generated_md
        )
        self.assertIn("Maintainer", generated_md)
        self.assertNotIn(
            "email", generated_md
        )  # Author Two has no email in this test data

    def test_authors_yml_not_found(self):
        """
        Test that no authors page content is generated if .authors.yml is missing.

        This test verifies the plugin's behavior when the specified
        .authors.yml file does not exist, ensuring that the generated content
        reflects this (e.g., an error message or empty content).
        """
        # Do not create .authors.yml
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn("No authors file found", generated_md)

    def test_authors_yml_empty(self):
        """
        Test handling of an empty .authors.yml file.

        This test ensures that if the .authors.yml file is empty, the plugin
        still provides content for the authors.md page but with a message indicating
        no authors were found.
        """
        self._create_authors_yml("")
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn(
            "No authors found or an error occurred while loading the authors data.",
            generated_md,
        )

    def test_authors_yml_malformed(self):
        """
        Test handling of a malformed .authors.yml file.

        This test verifies that if the .authors.yml file contains invalid YAML
        syntax, the plugin handles the error gracefully by providing content
        for the authors.md page with an appropriate error message.
        """
        self._create_authors_yml("not: valid: yaml")
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn(
            "No authors found or an error occurred while loading the authors data.",
            generated_md,
        )

    def test_authors_yml_wrong_top_level_key(self):
        """
        Test handling of .authors.yml with an incorrect top-level key.

        This test ensures that if the .authors.yml file has a top-level key
        other than 'authors', the plugin recognizes the incorrect format and
        generates the authors.md page content with a message indicating no valid
        authors data was found.
        """
        yml_content = """
contributors:
  author_one:
    name: Author One
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn(
            "No authors found or an error occurred while loading the authors data.",
            generated_md,
        )

    def test_authors_page_generation_with_custom_title(self):
        """
        Test that the authors page uses a custom title defined in .authors.yml.
        """
        yml_content = """
page_params:
  title: Project Contributors
authors:
  author_one:
    name: Custom Author
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn("# Project Contributors", generated_md)
        self.assertIn("## Custom Author", generated_md)
        self.assertNotIn("# Our Amazing Authors", generated_md)

    def test_authors_page_generation_with_custom_description(self):
        """
        Test that the authors page includes a custom description defined in .authors.yml.
        """
        yml_content = """
page_params:
  title: Our Team
  description: This is a test description for the authors page.
authors:
  author_one:
    name: Desc Author
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn("# Our Team", generated_md)
        self.assertIn("This is a test description for the authors page.", generated_md)
        self.assertIn("## Desc Author", generated_md)

    def test_authors_page_generation_without_description(self):
        """
        Test that the authors page does not include a description if not defined.
        """
        yml_content = """
page_params:
  title: No Desc Team
authors:
  author_one:
    name: NoDesc Author
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn("# No Desc Team", generated_md)
        self.assertIn("## NoDesc Author", generated_md)
        # Check that no empty line or unexpected content is added for description
        lines = generated_md.splitlines()
        title_line_index = -1
        for i, line in enumerate(lines):
            if line.startswith("# No Desc Team"):
                title_line_index = i
                break
        self.assertGreaterEqual(title_line_index, 0)
        found_author_heading = False
        for i in range(title_line_index + 1, len(lines)):
            if lines[i].strip():  # Find the next non-empty line
                if lines[i].startswith("## NoDesc Author"):
                    found_author_heading = True
                break
        self.assertTrue(
            found_author_heading,
            "Should directly follow title with author heading if no description",
        )

    def test_authors_page_generation_with_default_title_if_not_specified(self):
        """
        Test that the authors page uses the default title if 'page_params' or 'title' is missing.
        """
        yml_content = """
authors:
  author_one:
    name: Default Title Author
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn("# Our Amazing Authors", generated_md)
        self.assertIn("## Default Title Author", generated_md)
        # Ensure no accidental empty description is added if page_params is missing
        lines = generated_md.splitlines()
        title_line_index = -1
        for i, line in enumerate(lines):
            if line.startswith("# Our Amazing Authors"):
                title_line_index = i
                break
        self.assertGreaterEqual(title_line_index, 0)
        found_author_heading = False
        for i in range(title_line_index + 1, len(lines)):
            if lines[i].strip():  # Find the next non-empty line
                if lines[i].startswith("## Default Title Author"):
                    found_author_heading = True
                break
        self.assertTrue(
            found_author_heading,
            "Should directly follow title with author heading if no description",
        )

    def test_authors_yml_page_params_not_a_dict(self):
        """
        Test handling of .authors.yml where 'page_params' is not a dictionary.
        """
        yml_content = """
page_params: "this is a string"
authors:
  author_one:
    name: Alice
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn(
            "# Our Amazing Authors", generated_md
        )  # Should fall back to default title
        self.assertIn("## Alice", generated_md)
        # Also ensure no description is added from a malformed page_params
        self.assertNotIn("this is a string", generated_md)

    def test_on_files_adds_generated_page(self):
        """
        Test that on_files correctly adds the generated authors.md to MkDocs files.

        This test simulates the 'on_files' hook, verifying that after the
        authors.md file is conceptually "generated" (its content prepared),
        it is correctly added to the list of files that MkDocs processes,
        ensuring it appears in the final build.
        """
        yml_content = """
authors:
  author_one:
    name: Author One
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)  # Prepare the content

        initial_files = Files(
            [
                File("index.md", self.docs_dir, self.site_dir, True),
                File("about.md", self.docs_dir, self.site_dir, True),
            ]
        )

        updated_files = self.plugin.on_files(initial_files, self.config)

        # Check if authors.md is now in the files list
        authors_md_found = False
        for f in updated_files:
            if f.src_path == "authors.md":
                authors_md_found = True
                self.assertEqual(
                    f.abs_src_path, os.path.join(self.docs_dir, "authors.md")
                )
                break
        self.assertTrue(authors_md_found, "authors.md was not added to MkDocs files.")
        self.assertEqual(len(updated_files), 3)  # Should have 3 files now

    def test_on_files_does_not_duplicate_generated_page(self):
        """
        Test that on_files does not add a duplicate if authors.md is already present.

        This test ensures that if an 'authors.md' file is already present
        in the MkDocs file list (e.g., if it was manually added to `nav`
        before generation), the 'on_files' hook does not add a duplicate
        entry.
        """
        yml_content = """
authors:
  author_one:
    name: Author One
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)  # Prepare the content

        # Simulate authors.md already being in the initial files list
        initial_files = Files(
            [
                File("index.md", self.docs_dir, self.site_dir, True),
                File("about.md", self.docs_dir, self.site_dir, True),
                File("authors.md", self.docs_dir, self.site_dir, True),  # Already here
            ]
        )

        updated_files = self.plugin.on_files(initial_files, self.config)

        # Check that it's still 3 files, not 4
        self.assertEqual(len(updated_files), 3)


if __name__ == "__main__":
    unittest.main()
