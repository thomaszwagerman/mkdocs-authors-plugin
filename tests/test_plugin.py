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
    """

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
            {"authors_file": ".authors.yml", "output_page": "authors.md", "page_params_key": "page_params"}
        )

    def tearDown(self):
        """
        Clean up the temporary directory after each test.
        """
        shutil.rmtree(self.tmp_dir)

    def _create_authors_yml(self, content):
        """
        Helper function to create the .authors.yml file with given content.
        """
        authors_yml_path = os.path.join(self.tmp_dir, ".authors.yml")
        with open(authors_yml_path, "w", encoding="utf-8") as f:
            f.write(content)
        return authors_yml_path

    def _get_generated_authors_md_content(self):
        """
        Helper function to simulate how MkDocs would get the content of
        the generated authors.md file by calling on_page_read_source.
        """
        authors_file = File(
            path="authors.md",
            src_dir=self.docs_dir,
            dest_dir=self.site_dir,
            use_directory_urls=self.config["use_directory_urls"],
        )
        authors_page = Page("authors", authors_file, self.config)
        return self.plugin.on_page_read_source(authors_page, self.config)

    def test_authors_page_generation_success(self):
        """
        Test that the authors page is generated correctly with valid data.
        Verifies default avatar size and shape (100px square, centered).
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

        self.plugin.on_pre_build(self.config)

        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn("# Our Amazing Authors", generated_md)
        self.assertIn("## Author One", generated_md)
        self.assertIn('<img src="headshot_one.png" alt="Author One Avatar"', generated_md)
        # Verify default avatar styles (100px square, centered)
        self.assertIn('style="width: 100px; height: 100px; object-fit: cover; border-radius: 0; display: block; margin: 0 auto 10px auto;"', generated_md)
        self.assertIn('<p style="text-align: center;">', generated_md) # Check for the wrapper paragraph
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
        self.assertIn('<img src="headshot_two.png" alt="Author Two Avatar"', generated_md)
        # Verify default avatar styles (100px square, centered)
        self.assertIn('style="width: 100px; height: 100px; object-fit: cover; border-radius: 0; display: block; margin: 0 auto 10px auto;"', generated_md)
        self.assertIn('<p style="text-align: center;">', generated_md) # Check for the wrapper paragraph
        self.assertIn("**Affiliation:** UK Centre for Ecology & Hydrology", generated_md)
        self.assertIn("Maintainer", generated_md)
        self.assertNotIn("email", generated_md)

    def test_authors_yml_not_found(self):
        """
        Test that no authors page content is generated if .authors.yml is missing.
        """
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn("No authors file found", generated_md)

    def test_authors_yml_empty(self):
        """
        Test handling of an empty .authors.yml file.
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
        lines = generated_md.splitlines()
        title_line_index = -1
        for i, line in enumerate(lines):
            if line.startswith("# No Desc Team"):
                title_line_index = i
                break
        self.assertGreaterEqual(title_line_index, 0)
        found_author_heading = False
        for i in range(title_line_index + 1, len(lines)):
            if lines[i].strip():
                if lines[i].startswith("## NoDesc Author"):
                    found_author_heading = True
                break
        self.assertTrue(found_author_heading, "Should directly follow title with author heading if no description")


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
        lines = generated_md.splitlines()
        title_line_index = -1
        for i, line in enumerate(lines):
            if line.startswith("# Our Amazing Authors"):
                title_line_index = i
                break
        self.assertGreaterEqual(title_line_index, 0)
        found_author_heading = False
        for i in range(title_line_index + 1, len(lines)):
            if lines[i].strip():
                if lines[i].startswith("## Default Title Author"):
                    found_author_heading = True
                break
        self.assertTrue(found_author_heading, "Should directly follow title with author heading if no description")


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
        self.assertIn("# Our Amazing Authors", generated_md)
        self.assertIn("## Alice", generated_md)
        self.assertNotIn("this is a string", generated_md)


    def test_avatar_custom_size_from_page_params(self):
        """
        Test that avatars are rendered with a custom size defined in page_params.
        """
        yml_content = """
page_params:
  avatar_size: 150
authors:
  author_one:
    name: Sized Author
    avatar: path/to/avatar.png
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        # Expected style for default alignment (center) but custom size
        self.assertIn('style="width: 150px; height: 150px; object-fit: cover; border-radius: 0; display: block; margin: 0 auto 10px auto;"', generated_md)

    def test_avatar_custom_shape_circle_from_page_params(self):
        """
        Test that avatars are rendered as circles when 'circle' shape is specified in page_params.
        """
        yml_content = """
page_params:
  avatar_shape: circle
authors:
  author_one:
    name: Circular Author
    avatar: path/to/avatar.png
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        # Expected style for default alignment (center) but custom shape
        self.assertIn('style="width: 100px; height: 100px; object-fit: cover; border-radius: 50%; display: block; margin: 0 auto 10px auto;"', generated_md)


    def test_avatar_custom_shape_square_from_page_params(self):
        """
        Test that avatars are rendered as squares when 'square' shape is specified in page_params.
        (even though it's default, explicitly test it)
        """
        yml_content = """
page_params:
  avatar_shape: square
authors:
  author_one:
    name: Square Author
    avatar: path/to/avatar.png
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        # Expected style for default alignment (center) and default shape
        self.assertIn('style="width: 100px; height: 100px; object-fit: cover; border-radius: 0; display: block; margin: 0 auto 10px auto;"', generated_md)


    def test_avatar_defaults_when_page_params_missing(self):
        """
        Test that avatars use default size, shape, and alignment when page_params are missing or incomplete.
        """
        yml_content = """
authors:
  author_one:
    name: Default Avatar Author
    avatar: path/to/avatar.png
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        # Expected default style (100px square, centered)
        self.assertIn('style="width: 100px; height: 100px; object-fit: cover; border-radius: 0; display: block; margin: 0 auto 10px auto;"', generated_md)
        self.assertIn('<p style="text-align: center;">', generated_md)


    def test_avatar_alignment_left(self):
        """
        Test avatar aligns left and text wraps around it.
        """
        yml_content = """
page_params:
  avatar_align: left
authors:
  author_one:
    name: Left Aligned Author
    avatar: path/to/left_avatar.png
    affiliation: Left Corp
    description: This is a long description that should wrap around the left-aligned avatar. It provides details about the author's work and contributions to the project.
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn('style="width: 100px; height: 100px; object-fit: cover; border-radius: 0; float: left; margin-right: 15px; margin-bottom: 10px;"', generated_md)
        self.assertNotIn('<p style="text-align: center;">', generated_md) # Should not be wrapped in a center paragraph
        self.assertIn('<div style="clear: both;"></div>', generated_md) # Ensure clear is present


    def test_avatar_alignment_right(self):
        """
        Test avatar aligns right and text wraps around it.
        """
        yml_content = """
page_params:
  avatar_align: right
authors:
  author_one:
    name: Right Aligned Author
    avatar: path/to/right_avatar.png
    affiliation: Right Corp
    description: This is a description that should wrap around the right-aligned avatar. It details the author's role.
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)
        generated_md = self._get_generated_authors_md_content()
        self.assertIsNotNone(generated_md)
        self.assertIn('style="width: 100px; height: 100px; object-fit: cover; border-radius: 0; float: right; margin-left: 15px; margin-bottom: 10px;"', generated_md)
        self.assertNotIn('<p style="text-align: center;">', generated_md) # Should not be wrapped in a center paragraph
        self.assertIn('<div style="clear: both;"></div>', generated_md) # Ensure clear is present


    def test_on_files_adds_generated_page(self):
        """
        Test that on_files correctly adds the generated authors.md to MkDocs files.
        """
        yml_content = """
authors:
  author_one:
    name: Author One
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)

        initial_files = Files(
            [
                File("index.md", self.docs_dir, self.site_dir, True),
                File("about.md", self.docs_dir, self.site_dir, True),
            ]
        )

        updated_files = self.plugin.on_files(initial_files, self.config)

        authors_md_found = False
        for f in updated_files:
            if f.src_path == "authors.md":
                authors_md_found = True
                self.assertEqual(f.abs_src_path, os.path.join(self.docs_dir, "authors.md"))
                break
        self.assertTrue(authors_md_found, "authors.md was not added to MkDocs files.")
        self.assertEqual(len(updated_files), 3)

    def test_on_files_does_not_duplicate_generated_page(self):
        """
        Test that on_files does not add a duplicate if authors.md is already present.
        """
        yml_content = """
authors:
  author_one:
    name: Author One
        """
        self._create_authors_yml(yml_content)
        self.plugin.on_pre_build(self.config)

        initial_files = Files(
            [
                File("index.md", self.docs_dir, self.site_dir, True),
                File("about.md", self.docs_dir, self.site_dir, True),
                File("authors.md", self.docs_dir, self.site_dir, True),
            ]
        )

        updated_files = self.plugin.on_files(initial_files, self.config)
        self.assertEqual(len(updated_files), 3)


if __name__ == "__main__":
    unittest.main()