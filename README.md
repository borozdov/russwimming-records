# Рекорды России по плаванию

Статический сайт с актуальной таблицей рекордов России по плаванию.
Раз в сутки GitHub Actions дёргает страницу
[russwimming.ru/records/russia/](https://russwimming.ru/records/russia/),
парсит её, и если что-то изменилось — коммитит нормализованный JSON
и перестроенный сайт. Cloudflare Pages автоматически выкатывает новый деплой.

История коммитов в `data/russia.json` = хронология изменений рекордов.

## Фичи сайта

- вкладки: Женщины 50м / 25м, Мужчины 50м / 25м, Смешанные, плюс «Все»;
- поиск (`/` — быстрый фокус);
- фильтры: пол, длина бассейна, стиль, личное / эстафета;
- сортировка по любой колонке;
- тёмная тема с авто-переключением;
- печать / сохранение в PDF;
- скачивание в **JSON / CSV / XLSX / Markdown / TXT**;
- бейдж «новое» для рекордов моложе года.

## Структура репозитория

```
scripts/fetch.py     # скрапер → data/russia.json
scripts/build.py     # data/russia.json → public/*
static/              # source CSS/JS (копируется в public/assets/)
data/russia.json     # normalized records (source of truth, diff-friendly)
public/              # готовый сайт (то, что деплоит Cloudflare Pages)
.github/workflows/   # cron + авто-коммит + issue при поломке
```

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch.py && python scripts/build.py
python -m http.server --directory public 8080
# открыть http://localhost:8080
```

`fetch.py` идемпотентен: если рекорды не изменились, `data/russia.json` не
трогается (поле `fetched_at` тоже сохраняется), поэтому пустых коммитов не
будет.

## Деплой на Cloudflare Pages

1. Запушьте репозиторий на GitHub (публичный).
2. В Cloudflare Dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Connect to Git**, выберите репозиторий.
3. Настройки билда:
   - **Framework preset:** None
   - **Build command:** *(оставить пустым)*
   - **Build output directory:** `public`
   - **Root directory:** *(оставить пустым)*
4. Сохраните. Первый деплой запустится с того, что уже лежит в `public/` в
   ветке `main`. Далее каждый пуш (включая авто-коммиты от Actions)
   триггерит пересборку.

> Никакого Python-билда в Cloudflare не требуется: сайт уже статический,
> Cloudflare просто раздаёт `public/`. Это делает деплой максимально
> стабильным и не зависящим от provider build env.

## GitHub Actions

`.github/workflows/update.yml`:

- **cron:** `30 6 * * *` (UTC), то есть ≈09:30 MSK каждый день.
- **manual run:** вкладка Actions → «Update records» → «Run workflow».
- Делает `git diff data/russia.json`, и только при изменениях пересобирает
  сайт и делает коммит. Пустых коммитов не бывает.
- Если парсер падает (сайт-источник сменил разметку) — заводит / обновляет
  issue с меткой `parser-broken`.

Права, нужные боту, уже прописаны в workflow (`contents: write`).

## Формат данных

`data/russia.json` / `public/records.json`:

```jsonc
{
  "source_url": "https://russwimming.ru/records/russia/",
  "fetched_at": "2026-04-19T06:30:00Z",
  "total_records": 90,
  "categories": [
    {
      "id": "women-lcm",
      "title": "Женщины, бассейн 50 м",
      "sex": "women",
      "pool": "lcm",
      "records": [
        {
          "discipline": "вольный стиль 50 м",
          "relay": false,
          "relay_count": null,
          "leg_distance_m": null,
          "total_distance_m": 50,
          "distance_m": 50,
          "stroke_id": "freestyle",
          "is_25m_pool": false,
          "athlete": "Каменева Мария",
          "roster": null,
          "result": "24.20",
          "result_seconds": 24.20,
          "location": "Казань",
          "date": "2021-04-09",
          "date_original": "09.04.2021"
        }
      ]
    }
  ]
}
```

Поля `*_seconds` и `date` (ISO) удобны для сортировки/фильтрации в коде;
`result` и `date_original` — в исходном виде для человеко-читаемого
отображения.

## Лицензия

Скрипты — MIT. Данные принадлежат Всероссийской федерации плавания; сайт —
зеркало с чёткой атрибуцией источника.
