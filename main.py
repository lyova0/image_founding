import asyncio
import random
import re
from pathlib import Path
from urllib.parse import quote

from playwright.async_api import async_playwright


TARGET_COUNT = 4000
RESULTS_PER_PAGE = 100

USED_FILE = Path("used_links.txt")
OUTPUT_FILE = Path("new_links.txt")

SEARCH_URL_TEMPLATE = (
    "https://www.ingimage.com/index.cfm?/search_EN"
    "&ucriteriaAll={query}"
    "&ucriteriaNot="
    "&uimagecolor_C=1&uimagecolor_BW=1"
    "&uimageOrient_P=1&uimageOrient_L=1&uimageOrient_S=1"
    "&uimagetype={imgtype}"
    "&umaxros=100"
    "&ustartpos={startpos}"
)


VECTOR_QUERIES = [
    "cute cartoon isolated white background",
    "groovy cartoon acter isolated",
    "funny cartoon mascot isolated",
    "retro cartoon acter isolated",
    "cartoon character isolated white",
    "cute cartoon girl isolated",
    "cute cartoon boy isolated",
    "cartoon woman isolated white",
    "cartoon man isolated white",
    "cartoon baby isolated white",
    "cartoon chef isolated",
    "cartoon doctor isolated",
    "cartoon superhero isolated",
    "cartoon student isolated",
    "cute cartoon cat isolated",
    "cute cartoon dog isolated",
    "cute cartoon bear isolated",
    "cute cartoon rabbit isolated",
    "cute cartoon owl isolated",
    "cartoon lion isolated",
    "cartoon fox isolated",
    "cartoon elephant isolated",
    "cartoon bird isolated",
    "cartoon fish isolated",
    "cartoon monkey isolated",
    "cartoon frog isolated",
    "cartoon dinosaur isolated",
    "cartoon penguin isolated",
    "cartoon horse isolated",
    "cartoon bee isolated",
    "cartoon hedgehog isolated",
    "cartoon tiger isolated",
    "cartoon giraffe isolated",
    "groovy coffee cup acter",
    "cartoon pizza isolated",
    "cartoon burger isolated",
    "cartoon ice cream isolated",
    "cartoon cake isolated",
    "cartoon donut isolated",
    "cartoon apple isolated",
    "cartoon watermelon isolated",
    "cartoon sushi isolated",
    "cartoon popcorn isolated",
    "cartoon robot isolated",
    "cartoon phone isolated",
    "cartoon guitar isolated",
    "cartoon car isolated",
    "cartoon rocket isolated",
    "cartoon gift isolated",
    "cartoon trophy isolated",
    "cartoon flower isolated",
    "cartoon camera isolated",
    "cartoon santa isolated",
    "cartoon pumpkin isolated",
    "cartoon snowman isolated",
]


PHOTO_ANIMAL_QUERIES = [
    "single cat sitting outdoors",
    "single dog portrait outdoor",
    "one bird perching branch",
    "single rabbit in grass",
    "one horse in field",
    "single butterfly on flower",
    "one squirrel on tree",
    "single fox in nature",
    "one deer in forest",
    "single owl on branch",
    "one eagle flying sky",
    "single duck on water",
    "one kitten close up",
    "single puppy portrait",
    "one parrot close up",
    "single turtle on ground",
    "one hedgehog in grass",
    "single frog on leaf",
    "one bee on flower",
    "single fish in water",
    "one cow in field",
    "single sheep in meadow",
    "one goat in field",
    "single pig portrait",
    "one chicken outdoor",
    "single hamster close up",
    "one gecko lizard close up",
    "single swan on water",
    "one flamingo portrait",
    "single peacock portrait",
]


PHOTO_OBJECT_QUERIES = [
    "apple isolated white background",
    "coffee cup isolated white background",
    "book isolated white background",
    "shoe isolated white background",
    "flower isolated white background",
    "camera isolated white background",
    "sunglasses isolated white background",
    "headphones isolated white background",
    "watch isolated white background",
    "laptop isolated white background",
    "smartphone isolated white background",
    "fruit isolated white background",
    "vegetable isolated white background",
    "toy isolated white background",
    "water bottle isolated white background",
    "backpack isolated white background",
    "hat isolated white background",
    "plant pot isolated white background",
    "candle isolated white background",
    "mug isolated white background",
    "ball isolated white background",
    "umbrella isolated white background",
    "guitar isolated white background",
    "key isolated white background",
    "pencil isolated white background",
    "scissors isolated white background",
    "clock isolated white background",
    "lamp isolated white background",
    "fork isolated white background",
    "spoon isolated white background",
]


PHOTO_PEOPLE_QUERIES = [
    "single woman smiling portrait outdoor",
    "single man portrait outdoor",
    "one child playing outdoor",
    "single chef portrait kitchen",
    "one doctor portrait",
    "single student portrait",
]


REQUIRED_VECTOR_KEYWORDS = [
    "cartoon", "groovy", "cute", "funny", "acter",
    "illustration", "vector", "clipart", "mascot",
    "character", "retro", "kawaii", "isolated", "chibi",
]


BAD_KEYWORDS_COMMON = [

    "set%2Dof", "set-of", "collection", "icons%2Dset", "icons-set",
    "sticker", "bundle", "%2Dpack", "-pack", "alphabet",
    "pattern", "seamless",

    "background", "poster", "concept", "scene%2D", "scene-",
    "banner", "wallpaper", "template", "panorama",

    "family%2D", "family-", "group%2D", "group-",
    "versus", "comic%2Dpage", "comic-page", "pop%2Dart", "pop-art",

    "infographic", "diagram", "icons%2D", "icons-",
    "map%2D", "map-",

    "performance", "festival", "concert", "%2Dband", "-band",
]


BAD_KEYWORDS_PHOTO = [
    "couple", "couples",
    "team%2D", "team-",
    "people%2D", "people-",
    "men%2D", "men-",
    "women%2D", "women-",
    "girls%2D", "girls-",
    "boys%2D", "boys-",
    "friends%2D", "friends-",
    "crowd", "audience",
    "gladiator",
    "warriors", "soldiers", "fighters",
    "meeting%2D", "meeting-",
    "party%2D", "party-",
    "wedding",
    "business%2Dpeople", "business-people",
    "multiethnic", "diverse%2Dgroup", "diverse-group",


    "bokeh",
    "blurred", "blurry",
    "silhouette",
    "aerial", "drone",
    "skyline",
    "cityscape",
    "landscape%2D", "landscape-",
    "panoramic",
    "abstract",
    "double%2Dexposure", "double-exposure",


    "collage",
    "before%2Dafter", "before-after",
    "step%2Dby%2Dstep", "step-by-step",
    "comparison",
]


def load_links(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def save_links(path: Path, links: set[str]) -> None:
    path.write_text("\n".join(sorted(links)), encoding="utf-8")


def normalize_url(url: str) -> str:
    url = url.split("#")[0]
    url = re.sub(r"[&?]CF(ID|TOKEN)=[^&]*", "", url)
    return url.rstrip("?&")


def is_image_page(url: str) -> bool:
    return "/imagedetails/" in url or "imgid=" in url


def is_good_vector_url(url: str) -> bool:
    url_lower = url.lower()
    if "imgid=" in url and "/imagedetails/" not in url:
        return True
    if not any(kw in url_lower for kw in REQUIRED_VECTOR_KEYWORDS):
        return False
    return not any(kw in url_lower for kw in BAD_KEYWORDS_COMMON)


def is_good_photo_url(url: str) -> bool:
    url_lower = url.lower()
    if "imgid=" in url and "/imagedetails/" not in url:
        return True
    bad_all = BAD_KEYWORDS_COMMON + BAD_KEYWORDS_PHOTO
    return not any(kw in url_lower for kw in bad_all)


async def collect_query(
    page,
    query: str,
    imgtype: str,
    label: str,
    is_good_fn,
    existing: set[str],
    found: set[str],
):
    print(f"\n{'='*55}")
    print(f"[{label}] '{query}' | найдено: {len(found)}/{TARGET_COUNT}")

    startpos = 1
    empty_pages = 0

    while len(found) < TARGET_COUNT:
        url = SEARCH_URL_TEMPLATE.format(
            query=quote(query),
            imgtype=imgtype,
            startpos=startpos,
        )

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(random.randint(2000, 3500))
        except Exception as e:
            print(f"  [ERROR] {e}")
            break

        hrefs = await page.eval_on_selector_all(
            "a[href*='imagedetails']",
            "els => els.map(a => a.href)"
        )

        added = 0
        skipped = 0

        for href in hrefs:
            clean = normalize_url(href)
            if not is_image_page(clean):
                continue
            if not is_good_fn(clean):
                skipped += 1
                continue
            if clean in existing or clean in found:
                continue
            found.add(clean)
            added += 1
            if len(found) >= TARGET_COUNT:
                break

        print(
            f"  startpos={startpos:4d} | "
            f"всего: {len(hrefs):3d} | "
            f"отброшено: {skipped:3d} | "
            f"+новых: {added:3d} | "
            f"итого: {len(found)}"
        )

        if len(hrefs) == 0:
            empty_pages += 1
            if empty_pages >= 2:
                print("  [СТОП] Страницы закончились")
                break
        else:
            empty_pages = 0

        if added > 0 and len(found) % 200 < added:
            save_links(OUTPUT_FILE, found)
            print(f"  [SAVE] Сохранено {len(found)} ссылок")

        next_btn = await page.query_selector(
            "a:has-text('Next Page'), button:has-text('Next Page')"
        )
        if not next_btn:
            print("  [СТОП] Последняя страница")
            break

        startpos += RESULTS_PER_PAGE
        await page.wait_for_timeout(random.randint(1500, 3000))

    save_links(OUTPUT_FILE, found)


async def main():
    used = load_links(USED_FILE)
    found = load_links(OUTPUT_FILE)

    print(f"[START] Использованных ссылок: {len(used)}")
    print(f"[START] Уже собрано:           {len(found)}")
    print(f"[ЦЕЛЬ]  Нужно:                 {TARGET_COUNT}")

    if len(found) >= TARGET_COUNT:
        print("[ГОТОВО] Цель уже достигнута!")
        return

    tasks = []
    for q in VECTOR_QUERIES:
        tasks.append((q, "vec", "ВЕКТОР", is_good_vector_url))
    for q in PHOTO_ANIMAL_QUERIES:
        tasks.append((q, "all", "ФОТО/ЖИВОТНЫЕ", is_good_photo_url))
    for q in PHOTO_OBJECT_QUERIES:
        tasks.append((q, "all", "ФОТО/ОБЪЕКТ", is_good_photo_url))
    for q in PHOTO_PEOPLE_QUERIES:
        tasks.append((q, "all", "ФОТО/ЛЮДИ", is_good_photo_url))

    random.shuffle(tasks)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=30,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )
        page = await context.new_page()

        for query, imgtype, label, is_good_fn in tasks:
            if len(found) >= TARGET_COUNT:
                break
            try:
                await collect_query(page, query, imgtype, label, is_good_fn, used, found)
            except Exception as e:
                print(f"[ERROR] '{query}': {e}")
                save_links(OUTPUT_FILE, found)

            pause = random.randint(2000, 5000)
            print(f"[PAUSE] {pause/1000:.1f}с ...")
            await page.wait_for_timeout(pause)

        await browser.close()

    save_links(OUTPUT_FILE, found)
    print(f"\n[ГОТОВО] Сохранено {len(found)} ссылок -> {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())