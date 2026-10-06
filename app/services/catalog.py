from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogItem:
    name: str
    category: str
    platform: str
    estimated_price: float
    tags: tuple[str, ...]
    url: str


CATALOG = [
    CatalogItem("Compact 3-Seater Sofa", "furniture", "IKEA", 24999, ("modern", "living", "sofa"), "https://www.ikea.com/"),
    CatalogItem("LED Ceiling Light", "lighting", "Amazon", 1899, ("modern", "lighting", "bedroom"), "https://www.amazon.in/"),
    CatalogItem("Ceiling Fan", "lighting", "Amazon", 2999, ("utility", "fan", "living"), "https://www.amazon.in/"),
    CatalogItem("6-Seater Dining Table", "furniture", "IKEA", 15999, ("dining", "modern", "wood"), "https://www.ikea.com/"),
    CatalogItem("Textured Area Rug", "decor", "Amazon", 3499, ("rug", "modern", "decor"), "https://www.amazon.in/"),
    CatalogItem("Wall Art Set", "decor", "Flipkart", 1299, ("art", "wall", "decor"), "https://www.flipkart.com/"),
    CatalogItem("Warm Table Lamp", "lighting", "IKEA", 2299, ("lamp", "warm", "bedroom"), "https://www.ikea.com/"),
    CatalogItem("Vegetarian Catering Package", "catering", "Swiggy", 650, ("vegetarian", "birthday", "food"), "https://www.swiggy.com/"),
    CatalogItem("Party Catering Package", "catering", "Zomato", 750, ("mixed", "birthday", "food"), "https://www.zomato.com/"),
    CatalogItem("Simple Party Decoration", "decoration", "Amazon", 2999, ("birthday", "decor"), "https://www.amazon.in/"),
    CatalogItem("Event Hall Package", "venue", "OYO", 12000, ("event", "venue"), "https://www.oyorooms.com/"),
    CatalogItem("Fairy Light Set", "decoration", "Amazon", 899, ("lights", "party", "decor"), "https://www.amazon.in/"),
    CatalogItem("Minimal Necklace Set", "necklace", "Amazon", 2999, ("elegant", "minimal", "necklace"), "https://www.amazon.in/"),
    CatalogItem("Traditional Jhumka Set", "earrings", "Flipkart", 1499, ("traditional", "jhumka", "wedding"), "https://www.flipkart.com/"),
    CatalogItem("Gold-Tone Bangle Set", "bangles", "Amazon", 2199, ("gold-tone", "traditional"), "https://www.amazon.in/"),
    CatalogItem("Statement Earrings", "earrings", "Amazon", 3499, ("statement", "party", "elegant"), "https://www.amazon.in/"),
    CatalogItem("Pearl Pendant Set", "necklace", "Flipkart", 2699, ("pearl", "elegant"), "https://www.flipkart.com/"),
]


def catalog_for(planner: str) -> list[dict]:
    if planner == "home":
        categories = {"furniture", "lighting", "decor"}
    elif planner == "party":
        categories = {"catering", "decoration", "venue"}
    else:
        categories = {"necklace", "earrings", "bangles"}

    return [
        {
            "name": x.name,
            "category": x.category,
            "platform": x.platform,
            "estimated_price": x.estimated_price,
            "tags": list(x.tags),
            "url": x.url,
        }
        for x in CATALOG
        if x.category in categories
    ]
