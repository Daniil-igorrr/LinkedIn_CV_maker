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

AI-агент не должен использовать `Move-Item inbox\\*.txt`, `inbox/*`, `*.txt` или любые другие wildcard-операции для перемещения/удаления входных файлов.

**Запрещены любые ручные filesystem-операции над batch input/processed files**, включая `Move-Item`, `mv`, `cp`, `rm`, `Remove-Item`, `del`, `unlink` и эквиваленты.

Если `batch_controller.py complete` возвращает ошибку, агент обязан остановиться и сообщить точный текст ошибки. Он не должен удалять существующий destination, перемещать source вручную или иным способом обходить controller.

## Генерация CV

1. Поместите описание вакансии в `inbox/`.
2. Для одной вакансии агент может обработать только указанный файл.
3. Для batch используйте controller и workflow из `AGENTS.md` и `.agent/rules/workflow.md`.

## Google Calendar

Для календарных скриптов требуется Python 3.x и `credentials.json`, который находится в `.gitignore`.


## PDF Generation

For PROCEED jobs, generate the final PDFs with the repository-owned Python pipeline:

```bash
python scripts/generate_pdfs.py \
  --cv "output/<Company>_<Role>_CV.md" \
  --cover-letter "output/<Company>_<Role>_CoverLetter.md"
```

The dependencies are declared in `requirements.txt`. The generator renders A4 PDFs and verifies the actual page count with `pypdf`; it fails unless both documents are exactly one page.


### Local Python environment

Use a project virtual environment on Windows rather than installing PDF dependencies into the global Python installation:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The Antigravity PDF step should use `.venv\\Scripts\\python.exe scripts/generate_pdfs.py ...`. The WSL environment may use its own `.venv`; do not use `--break-system-packages`.

## Bulk Vacancy Import

Put multiple vacancies into:

`inbox/vacancies.txt`

You can separate vacancies using a numbered format:

```text
1) Business Development Representative
Company: Paydora
Location: Remote

Job description...

2) Account Executive
Company: Example Corp
Location: Madrid

Job description...
```

Or, for maximum reliability, use the explicit separator format:

```text
Business Development Representative
Company: Paydora

Job description...

---JOB---

Account Executive
Company: Example Corp

Job description...
```

Then run the parser to split them into individual jobs in the `inbox/` folder:

```bash
python scripts/vacancy_parser.py
```

Preview without creating files:

```bash
python scripts/vacancy_parser.py --dry-run
```

Once split, run `python scripts/batch_controller.py prepare` to process the jobs one by one.
