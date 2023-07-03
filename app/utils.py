import wikipediaapi


def viki_data(response: str) -> dict:
    wiki_wiki = wikipediaapi.Wikipedia(
        language='ru', extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    page_py = wiki_wiki.page(response)
    data = {
        "t2": page_py.text.split('\n\n')
    }
    return data