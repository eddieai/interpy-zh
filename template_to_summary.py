from pathlib import Path
import re


book_path = Path("./docs")


class Page:
    def __init__(self, title=None, nav_order=None, parent=None, has_children=False, path=None):
        self.title = title
        self.nav_order = nav_order
        self.parent = parent
        self.has_children = has_children
        self.children = []
        self.path = path


def read_markdown_front_matter(md_file_path):
    with open(md_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Extract the front matter
    front_matter_match = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not front_matter_match:
        return None

    front_matter = front_matter_match.group(1)

    # Parse the front matter
    attributes = {}
    for line in front_matter.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if key == "nav_order":
                attributes[key] = float(value)
            elif key == "has_children":
                attributes[key] = value.lower() == "true"
            else:
                attributes[key] = value

    if "title" not in attributes:
        attributes["title"] = (
            next((line.strip()for line in open(md_file_path, 'r')if line.lstrip().startswith('# ')),None,)[2:]
        )

    attributes["path"] = md_file_path

    return Page(**attributes)


def generate_summary(folder):

    def add_page_recursively(folder):
        readme_path = folder / "README.md"
        readme = read_markdown_front_matter(readme_path)

        for item in folder.glob("*"):
            if item.is_dir():
                readme.children.append(add_page_recursively(item))
            elif item.suffix == ".md" and item.stem != "README":
                readme.children.append(read_markdown_front_matter(item))

        readme.children.sort(key=lambda x: x.nav_order)

        return readme

    index = add_page_recursively(folder)

    summary = "# Summary\n"
    summary += f"\n### {index.title}"
    summary += f"\n* [{index.title}](./README.md)\n"

    for chapter in index.children:
        summary += f"\n### {chapter.title}"
        for page in chapter.children:
            summary += f"\n* [{page.title}]({page.path.relative_to(folder).as_posix()})"
        summary += "\n"

    return summary


print(generate_summary(book_path))
