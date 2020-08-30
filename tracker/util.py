from bs4 import BeautifulSoup


def soup(markup: str):
    return BeautifulSoup(markup, 'lxml')


def find_html_nodes(markup: str, selector: str):
    return soup(markup).select(selector)


def extract_price(node) -> str:
    price_string = ''
    if 'value' in node and node['value']:
        price_string = node['value']
    else:
        price_string = node.get_text()

    return price_string


def parse_price(x: str, decimal_separator: str) -> float:
    valid_chars = {
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        decimal_separator,
    }
    trimmed = ''.join(c for c in x if c in valid_chars)
    return float(trimmed.replace(decimal_separator, '.'))
