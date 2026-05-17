# 🚀 Ingram Image Link Collector

A high-performance Python scraper built with Playwright for collecting thousands of unique image detail links from [Ingram Image](https://www.ingimage.com?utm_source=chatgpt.com).

The script automatically searches across vector illustrations, photos of animals, objects, and people, filters out low-quality or irrelevant results, removes duplicates, and saves only clean image detail URLs.

---

## ✨ Features

* 🔍 Collects up to **4,000 unique image links**
* 🎨 Supports both **vector illustrations** and **photos**
* 🧠 Smart filtering to exclude:

  * Sets and bundles
  * Backgrounds and templates
  * Groups of people
  * Blurry or abstract photos
* ♻️ Avoids duplicates using `used_links.txt`
* 💾 Auto-saves progress every 200 new links
* 🎲 Randomized query order to improve diversity
* 🕵️ Human-like delays to reduce detection risk
* 📂 Resumable collection process

---

## 📁 Project Structure

```text
project/
├── scraper.py          # Main script
├── used_links.txt      # Previously processed links
├── new_links.txt       # Newly collected links
└── README.md
```

---

## ⚙️ Requirements

* Python 3.10+
* [Playwright](https://playwright.dev/python/?utm_source=chatgpt.com)

Install dependencies:

```bash
pip install playwright
playwright install
```

---

## 🚀 Usage

Run the script:

```bash
python scraper.py
```

The scraper will:

1. Load previously used links.
2. Resume from existing results.
3. Visit Ingram Image search pages.
4. Extract image detail URLs.
5. Apply quality filters.
6. Save unique links to `new_links.txt`.

---

## 🧠 Search Categories

### Vector Queries

Searches for cartoon and mascot illustrations such as:

* Cute cartoon characters
* Animals
* Food items
* Seasonal objects
* Retro and groovy illustrations

### Photo Queries

#### Animals

Cats, dogs, birds, foxes, deer, butterflies, and more.

#### Objects

Books, cameras, laptops, flowers, mugs, guitars, etc.

#### People

Portraits of men, women, children, doctors, chefs, and students.

---

## 🔍 Filtering Logic

### Vector Images Must Include

At least one of these keywords:

* cartoon
* vector
* illustration
* mascot
* cute
* retro
* kawaii
* chibi

### Automatically Excluded

* Collections and icon sets
* Stickers and bundles
* Backgrounds and templates
* Patterns
* Group scenes

### Photo-Specific Exclusions

* Couples or crowds
* Meetings and parties
* Blurry or bokeh shots
* Landscapes and panoramas
* Collages

---

## 📄 Output Files

### `used_links.txt`

Contains URLs that have already been processed.

### `new_links.txt`

Stores all newly collected image detail URLs.

---

## ⚙️ Configuration

Edit these constants in the script:

```python
TARGET_COUNT = 4000
RESULTS_PER_PAGE = 100
```

### File Paths

```python
USED_FILE = Path("used_links.txt")
OUTPUT_FILE = Path("new_links.txt")
```

---

## 🔄 Auto-Save Behavior

The scraper automatically saves progress:

* Every 200 new links
* After each query
* On errors
* At completion

This ensures minimal data loss if the process is interrupted.

---

## 🧩 Core Functions

### `load_links(path)`

Loads URLs from a text file into a Python set.

### `save_links(path, links)`

Writes sorted URLs to disk.

### `normalize_url(url)`

Removes tracking parameters and fragments.

### `is_good_vector_url(url)`

Validates vector image links.

### `is_good_photo_url(url)`

Validates photo image links.

### `collect_query(...)`

Processes a single search query across all result pages.

### `main()`

Coordinates the full scraping workflow.

---

## 🌐 Search URL Format

```text
https://www.ingimage.com/index.cfm?/search_EN
```

Parameters include:

* `ucriteriaAll` — search keywords
* `uimagetype` — vector or all
* `umaxros=100` — results per page
* `ustartpos` — pagination offset

---

## 🛡️ Anti-Detection Measures

The script uses several techniques to appear more like a normal user:

* Real browser (not headless)
* Custom user agent
* Random delays
* Shuffled query order
* Automation flag suppression

---

## 📈 Example Console Output

```text
[START] Использованных ссылок: 1230
[START] Уже собрано:           840
[ЦЕЛЬ]  Нужно:                 4000

=======================================================
[ВЕКТОР] 'cute cartoon cat isolated' | найдено: 840/4000
startpos=1    | всего: 100 | отброшено: 42 | +новых: 58 | итого: 898
[SAVE] Сохранено 898 ссылок
```

---

## 🔧 Customization Ideas

You can easily adapt the scraper to:

* Collect more than 4,000 links
* Add your own search queries
* Export metadata instead of URLs
* Download images automatically
* Run in parallel with multiple browsers

---

## ⚠️ Notes

* The scraper targets public search results.
* Site structure changes may require selector updates.
* Respect website terms of service and rate limits.

---

## 📜 License

This project is released under the MIT License.

---

## 👤 Author

Created for scalable image dataset collection and automated asset pipelines. 
