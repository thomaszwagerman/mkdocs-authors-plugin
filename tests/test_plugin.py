# mkdocs-authors-plugin/tests/test_plugin.py
import unittest
import os
import tempfile
import shutil
from mkdocs.config import config_options as c
from mkdocs.config.base import Config
from mkdocs.structure.files import File, Files

# Import the plugin class from your package
from mkdocs_authors_plugin.plugin import AuthorsPlugin


class TestAuthorsPlugin(unittest.TestCase):

    def setUp(self):
        """
        Set up a temporary directory and mock MkDocs environment for each test.
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
            {"authors_file": ".authors.yml", "output_page": "authors.md"}
        )
        self.plugin.on_config(self.config)

    def tearDown(self):
        """
        Clean up the temporary directory after each test.
        """
        shutil.rmtree(self.tmp_dir)

    def _create_authors_yml(self, content):
        """Helper to create the .authors.yml file with given content."""
        authors_yml_path = os.path.join(self.tmp_dir, ".authors.yml")
        with open(authors_yml_path, "w", encoding="utf-8") as f:
            f.write(content)
        return authors_yml_path

    def _read_generated_authors_md(self):
        """Helper to read the content of the generated authors.md."""
        generated_path = os.path.join(self.docs_dir, "authors.md")
        if not os.path.exists(generated_path):
            return None
        with open(generated_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_authors_page_generation_success(self):
        """Test that the authors page is generated correctly with valid data."""
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

        # Simulate on_pre_build hook
        self.plugin.on_pre_build(self.config)

        # Read the generated Markdown file
        generated_md = self._read_generated_authors_md()
        self.assertIsNotNone(generated_md)
        self.assertIn("# Our Amazing Authors", generated_md)
        self.assertIn("## Author One", generated_md)
        self.assertIn("**ID:** `author_one`", generated_md)
        self.assertIn("**Affiliation:** British Antarctic Survey", generated_md)
        self.assertIn("> Owner", generated_md)
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
        self.assertIn("**ID:** `author_two`", generated_md)
        self.assertIn(
            "**Affiliation:** UK Centre for Ecology & Hydrology", generated_md
        )
        self.assertIn("> Maintainer", generated_md)
        self.assertNotIn(
            "email", generated_md
        )  # Author Two has no email in this test data

    def test_authors_yml_not_found(self):
        """Test that no authors page is generated if .authors.yml is missing."""
        # Do not create .authors.yml
        self.plugin.on_pre_build(self.config)
        generated_md = self._read_generated_authors_md()
        self.assertIsNone(generated_md)

    def test_authors_yml_empty(self):
        """Test handling of an empty .authors.yml file."""
        self._create_authors_yml("")
        self.plugin.on_pre_build(self.config)
        generated_md = self._read_generated_authors_md()
        self.assertIsNotNone(generated_md)
        self.assertIn(
            "No authors found or an error occurred while loading the authors data.",
            generated_md,
        )

    def test_authors_yml_malformed(self):
        """Test handling of a malformed .authors.yml file."""
        self._create_authors_yml("not: valid: yaml")
        self.plugin.on_pre_build(self.config)
        generated_md = self._read_generated_authors_md()
        self.assertIsNotNone(generated_md)
        self.assertIn(
            "No authors found or an error occurred while loading the authors data.",
            generated_md,
        )

    def test_authors_yml_wrong_top_level_key(self):
        """Test handling of .authors.yml with incorrect top-level key."""
        yml_content = """
contributors:
  author_one:
    name: Author One
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._read_generated_authors_md()
        self.assertIsNotNone(generated_md)
        self.assertIn(
            "No authors found or an error occurred while loading the authors data.",
            generated_md,
        )

    def test_on_files_adds_generated_page(self):
        """Test that on_files correctly adds the generated authors.md to MkDocs files."""
        yml_content = """
authors:
  author_one:
    name: Author One
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)  # Generate the file first

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
                break
        self.assertTrue(authors_md_found, "authors.md was not added to MkDocs files.")
        self.assertEqual(len(updated_files), 3)  # Should have 3 files now

    def test_on_files_does_not_duplicate_generated_page(self):
        """Test that on_files does not add a duplicate if authors.md is already present."""
        yml_content = """
authors:
  author_one:
    name: Author One
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)  # Generate the file first

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
