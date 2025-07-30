# Authors YAML File Format

The `mkdocs-authors-plugin` expects your author data to be defined in a YAML file (by default, `.authors.yml`) located in the root of your MkDocs documentation project.

The YAML can contain two top-level keys named `page_params` (optional) and `authors`.

## Page Data
The `page_params` key is an optional top-level dictionary that lets you configure characteristics
of the generated authors page itself, such as its main title and an introductory description.

## Author Data

The `authors` key is a required top-level dictionary which holds individual author entries.
Each author entry is identified by a unique key (e.g., `author_one`, `author_two`), which the plugin
uses as the author's ID.

| Field         | Type     | Description                                                          | Example Value                     |
| :------------ | :------- | :------------------------------------------------------------------- | :-------------------------------- |
| `title`       | `string` | The main title of the generated authors page. Defaults to `Our Amazing Authors`. | `Project Contributors`            |
| `description` | `string` | An introductory paragraph displayed directly under the main title.   | `Meet our team members.` |

Under each author ID, you can define various fields to describe the author.
The plugin will render these fields on the generated authors page.

| Field         | Type     | Description                                                                                             | Example Value                                |
| :------------ | :------- | :------------------------------------------------------------------------------------------------------ | :------------------------------------------- |
| `name`        | `string` | **Required.** The full name of the author.                                                              | `Author One`                                 |
| `description` | `string` | A brief description or role of the author. This will be displayed as a blockquote.                      | `Lead Developer`                             |
| `avatar`      | `string` | A URL to the author's profile picture or avatar.                                                        | `https://placehold.co/100x100/aabbcc?text=A1` |
| `affiliation` | `string` | The organization or institution the author is affiliated with.                                          | `British Antarctic Survey`                        |
| `email`       | `string` | The author's email address. Will be rendered as a `mailto:` link.                                       | `author.one@example.com`                     |
| `github`      | `string` | The author's GitHub username. Will be rendered as a link to their GitHub profile.                       | `authorone`                                  |
| `linkedin`    | `string` | The author's LinkedIn profile ID (the part after `linkedin.com/in/`). Will be rendered as a link.      | `author-one-profile`                         |
| `twitter`     | `string` | The author's Twitter (X) handle. Will be rendered as a link to their Twitter profile.                   | `author_one_dev`                             |

## Example `.authors.yml`

```yaml
# .authors.yml

# Optional: Define page-level parameters for the generated authors page
page_params:
  title: Our Project Team
  description: "Meet the people behind our project."


# Required: Define individual author data
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
    # You can omit any fields not applicable to an author
  author_three:
    name: Author Three
    description: Core Contributor
    avatar: headshot_three.png
    affiliation: University of Edinburgh
```
