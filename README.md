# LinkedIn CV Maker & BDR Application Assistant

Ассистент на базе ИИ для подготовки адаптированных CV и cover letters для SDR / BDR / Lead Generation позиций на основе описаний вакансий.

## Структура проекта

- `AGENTS.md` — правила AI-агента.
- `master-profile.md` — единственный источник фактов о кандидате.
- `inbox/` — входящие вакансии.
- `output/` — сгенерированные материалы и append-only execution log.
- `templates/` — шаблоны.
- `scripts/batch_controller.py` — детерминированный контроллер batch state.

## Batch Mode

Для нескольких вакансий **не передавайте управление batch state самому LLM**. Используйте controller:

```bash
python scripts/batch_controller.py prepare
python scripts/batch_controller.py current
```

Контроллер фиксирует максимум 5 файлов в `.batch/manifest.json`, сохраняет SHA-256 правил и исходных файлов и выдаёт ровно один CURRENT JOB.

После обработки текущей вакансии агент создаёт временный execution record:

```text
.batch/records/<job>.record.md
```

Затем:

```bash
python scripts/batch_controller.py complete "<CURRENT_JOB>" ".batch/records/<job>.record.md"
```

Controller сам:
- проверяет неизменность правил и входного файла;
- добавляет запись в `output/execution_log.md`;
- перемещает только конкретный текущий файл в `inbox/processed/`;
- переводит следующий job в `in_progress`;
- закрывает batch после последнего job.

### Важное ограничение

AI-агент не должен использовать `Move-Item inbox\\*.txt`, `inbox/*`, `*.txt` или любые другие wildcard-операции для перемещения/удаления входных файлов. Он также не должен напрямую изменять `output/execution_log.md`.

## Генерация CV

1. Поместите описание вакансии в `inbox/`.
2. Для одной вакансии агент может обработать только указанный файл.
3. Для batch используйте controller и workflow из `AGENTS.md` и `.agent/rules/workflow.md`.

## Google Calendar

Для календарных скриптов требуется Python 3.x и `credentials.json`, который находится в `.gitignore`.
