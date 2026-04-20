# Рекорды России по плаванию

Автообновляемое зеркало таблицы рекордов с [russwimming.ru/records/russia/](https://russwimming.ru/records/russia/).  
Каждый день GitHub Actions парсит источник и, если что-то изменилось, коммитит обновлённые данные и пересобирает сайт.

**Сайт:** [russwimming-records.borozodov.ru](https://russwimming-records.borozodov.ru)

---

## Скачать данные

| Формат | Ссылка |
|--------|--------|
| JSON   | [records.json](https://russwimming-records.borozodov.ru/records.json) |
| CSV    | [records.csv](https://russwimming-records.borozodov.ru/records.csv) |
| Excel  | [records.xlsx](https://russwimming-records.borozodov.ru/records.xlsx) |
| Markdown | [records.md](https://russwimming-records.borozodov.ru/records.md) |
| TXT    | [records.txt](https://russwimming-records.borozodov.ru/records.txt) |

Файлы обновляются автоматически вместе с сайтом.  
История изменений рекордов — в коммитах файла [`data/russia.json`](data/russia.json).

---

## Фичи сайта

- вкладки: Женщины 50м / 25м, Мужчины 50м / 25м, Смешанные, плюс «Все»
- фильтры: пол, длина бассейна, стиль, личное / эстафета
- сортировка по любой колонке
- тёмная тема с авто-переключением
- печать / сохранение в PDF
- бейдж «новое» для рекордов моложе года

---

## Структура репозитория

```
scripts/fetch.py     # скрапер → data/russia.json
scripts/build.py     # data/russia.json → public/*
static/              # source CSS/JS
data/russia.json     # нормализованные данные (source of truth)
public/              # готовый сайт (деплоится через GitHub Pages)
.github/workflows/   # cron + авто-коммит
```

---

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch.py && python scripts/build.py
python -m http.server --directory public 8080
# открыть http://localhost:8080
```

---

## Формат данных

`data/russia.json` / `records.json`:

```jsonc
{
  "source_url": "https://russwimming.ru/records/russia/",
  "fetched_at": "2026-04-20T06:00:00Z",
  "total_records": 90,
  "categories": [
    {
      "id": "women-lcm",
      "title": "Женщины, бассейн 50 м",
      "records": [
        {
          "discipline": "вольный стиль 50 м",
          "athlete": "Каменева Мария",
          "result": "24.20",
          "result_seconds": 24.20,
          "location": "Казань",
          "date": "2021-04-09"
        }
      ]
    }
  ]
}
```

---

## Лицензия

Скрипты — MIT. Данные принадлежат Всероссийской федерации плавания; сайт — зеркало с атрибуцией источника.
