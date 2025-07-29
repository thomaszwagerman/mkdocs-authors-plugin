# Authors YAML File Format

The `mkdocs-authors-plugin` expects your author data to be defined in a YAML file (by default, `.authors.yml`) located in the root of your MkDocs documentation project.

The YAML file must contain a top-level key named `authors`, which holds a dictionary of individual author entries. Each author entry is identified by a unique key (e.g., `author_one`, `alextbradley`), which the plugin uses as the author's `ID`.

Under each author ID, you can define various fields to describe the author. The plugin will render these fields on the generated authors page.

## Supported Fields

| Field         | Type     | Description                                                                                             | Example Value                                |
| :------------ | :------- | :------------------------------------------------------------------------------------------------------ | :------------------------------------------- |
| `name`        | `string` | **Required.** The full name of the author.                                                              | `Author One`                                 |
| `description` | `string` | A brief description or role of the author. This will be displayed as a blockquote.                      | `Lead Developer`                             |
| `avatar`      | `string` | A URL to the author's profile picture or avatar.                                                        | `https://placehold.co/100x100/aabbcc?text=A1` |
| `affiliation` | `string` | The organization or institution the author is affiliated with.                                          | `Tech Solutions Inc.`                        |
| `email`       | `string` | The author's email address. Will be rendered as a `mailto:` link.                                       | `author.one@example.com`                     |
| `github`      | `string` | The author's GitHub username. Will be rendered as a link to their GitHub profile.                       | `authorone`                                  |
| `linkedin`    | `string` | The author's LinkedIn profile ID (the part after `linkedin.com/in/`). Will be rendered as a link.      | `author-one-profile`                         |
| `twitter`     | `string` | The author's Twitter (X) handle. Will be rendered as a link to their Twitter profile.                   | `author_one_dev`                             |

## Example `.authors.yml`

```yaml
# .authors.yml
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
