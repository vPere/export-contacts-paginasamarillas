# 📒 Páginas Amarillas Contact Extractor

A simple **Flask web app** that extracts company names and phone numbers from [Páginas Amarillas](https://www.paginasamarillas.es/), displays them in a table, and exports them as an **Excel file**.  

---

## 🚀 Features
- Search by **sector** and **province**.  
- Extracts company **name** and **phone number** from multiple pages.  
- Displays results in a browser table.  
- Exports to **Excel (.xlsx)**.  
- Secure file downloads.  

---

## ⚙️ Installation

Install dependencies:

pip install flask pandas requests openpyxl

---

## ▶️ Usage

Run the Flask app:

```
python app.py
```

Open in your browser:

```
http://127.0.0.1:5000
```

Fill in:

* **Sector** (e.g., `inmobiliarias`)
* **Província** (e.g., `valencia`)
* **Núm. de pàgines**

Click **Cerca** to scrape.

Results will appear in a table, with an option to **download Excel**.

---

## 📄 Example

* Sector: `inmobiliarias`
* Província: `valencia`
* Pàgines: `2`

Output file:

```
exports/telefonos_inmobiliarias_valencia.xlsx
```

---

## ⚠️ Notes

* Educational purposes only.
* Scraping depends on the target site’s **ToS**.
* If Páginas Amarillas changes its structure, the scraper may need updates.

```
```
