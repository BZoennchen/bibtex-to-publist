import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

def format_authors(authors_string):
    authors = authors_string.split(" and ")
    formatted_authors = []
    for author in authors:
        if "," in author:  # Format is "Last, First"
            last, first = author.split(",", 1)
            first_initials = " ".join([f"{name.strip()[0]}." for name in first.strip().split()])
            formatted_authors.append(f"{last.strip()}, {first_initials}")
        else:  # Format is "First Last"
            names = author.split()
            last = names[-1]
            first_initials = " ".join([f"{name[0]}." for name in names[:-1]])
            formatted_authors.append(f"{last}, {first_initials}")
    return ", ".join(formatted_authors)

def extract_url(entry):
    doi = entry.get("doi", "")
    if doi:
        return f"https://doi.org/{doi}"
    return entry.get("url", "")

# APA citation formatting
def format_apa(entry):
    authors = format_authors(entry.get("author", ""))
    year = entry.get("year", "n.d.")
    title = entry.get("title", "").strip("{}").replace('--', '-')
    journal = entry.get("journal", "")
    booktitle = entry.get("booktitle", "").replace('--', '-')
    volume = entry.get("volume", "")
    number = entry.get("number", "")
    pages = entry.get("pages", "").replace('--', '-')
    doi = entry.get("doi", "")
    publisher = entry.get("publisher", "")

    url = extract_url(entry)

    if url:
        title_html = f'<span class="entry-title"><a href="{url}">{title}</a></span>'
    else:
        title_html = f'<span class="entry-title">{title}</span>'

    citation = f'<span class="entry-authors">{authors}</span><span class="entry-year"> ({year})</span><br>{title_html}<br>'
    if journal:
        citation += f" <em>{journal}</em>"
    if not journal and booktitle:
        citation += f' <em>{booktitle}</em>'
    if volume:
        citation += f", <em>{volume}</em>"
    if number:
        citation += f"({number})"
    if pages and (journal or booktitle):
        citation += f", {pages}"
    if publisher:
        if booktitle or volume or journal:
            citation += ', '
        citation += f"{publisher}"
    if doi:
        citation += f'<br>https://doi.org/{doi}'
    return citation

def format_bibtex_sting(entry, filters=[]):
    bibtex_string = f"@{entry['ENTRYTYPE']}"
    bibtex_string += "{"
    bibtex_string += f'{entry['ID']}'
    for key, value in entry.items():
        if key not in ["ENTRYTYPE", "ID"] and key not in filters:
          bibtex_string += f",\n{key} = {{{value}}}"
    bibtex_string += '\n}'
    return bibtex_string
    #return f"@{entry['ENTRYTYPE']}{{{entry['ID']},\n" + ",\n".join([f"{key} = {{{value}}}" for key, value in entry.items() if key not in ["ENTRYTYPE", "ID"]]) + "\n}"

def extract_keywords(entry):
    keywords = entry.get("keywords", "").split(',')
    return keywords

def sort_entries(entries):
    def sort_key(entry):
        year = entry.get("year", "0")
        # Extract the last name of the first author
        first_author = entry.get("author", "").split(" and ")[0]
        last_name = first_author.split(",")[0] if "," in first_author else first_author.split(" ")[-1]
        return (-int(year), last_name.lower())  # Sort by year (descending) and last name (ascending)

    return sorted(entries, key=sort_key)

def generate_publication_list(bibtex_file, output_html_file, keywords = None):
    # Read the BibTeX file
    with open(bibtex_file, 'r', encoding='utf-8') as bibtex_file:
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(bibtex_file, parser=parser)

    sorted_entries = sort_entries(bib_database.entries)
    # Generate HTML
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Publication List</title>
    <link rel="stylesheet" href="style.css">
    <script type="text/javascript" src="script.js"></script>
</head>
<body>
    <h1>Publication List</h1>
"""

    # Add each publication
    for entry in sorted_entries:
        if keywords == None or any([keyword in extract_keywords(entry) for keyword in keywords]):
          apa_citation = format_apa(entry)
          bibtex_code = format_bibtex_sting(entry, filters=['file', 'keywords'])
          html_content += f"""
    <div class="publications">
        <p class="entry">{apa_citation}</p>
        <button class="copy-button" onclick="copyToClipboard('{entry['ID']}')">Copy BibTeX</button>
        <pre id="{entry['ID']}">{bibtex_code}</pre>
    </div>
"""

    # Add JavaScript for copying BibTeX
    html_content += """
</body>
</html>
"""

    # Write the HTML file
    with open(output_html_file, 'w', encoding='utf-8') as output_file:
        output_file.write(html_content)

    print(f"Publication list has been generated: {output_html_file}")


# Example usage
generate_publication_list('literature-muc-dai.bib', 'publication_list.html', keywords=['muc.dai'])
