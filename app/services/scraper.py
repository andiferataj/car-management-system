from bs4 import BeautifulSoup
from typing import List, Dict

def parse_car_listings(html: str) -> List[Dict]:
    """Parse simple car listing HTML and return list of dicts.

    This is a small utility that extracts elements with a `.listing` class
    and reads `data-*` attributes or child text. It's resilient to missing
    fields and intended as a template for real scrapers.
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for item in soup.select(".listing"):
        title = item.select_one(".title")
        price = item.select_one(".price")
        vin = item.get("data-vin") or (item.select_one(".vin") and item.select_one(".vin").text.strip())
        color = item.select_one(".color")
        results.append({
            "title": title.text.strip() if title else None,
            "price": float(price.text.replace("$", "")) if (price and price.text.strip().replace('.', '', 1).replace(',', '').lstrip('$').isdigit()) else None,
            "vin": vin,
            "color": color.text.strip() if color else None,
        })
    return results
