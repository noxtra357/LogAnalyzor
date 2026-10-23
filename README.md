# Log Analyzer

A command-line utility that reads a log file and prints a short summary: how many lines were processed, how they are split across log levels, which IP addresses appear most often, and which errors came last. The report can be saved as JSON. It uses only the Python standard library, so there is nothing to install.

> The prompts and report text are in Russian. Their meaning is explained below.

## Features

- Counts lines by level: `INFO`, `WARNING`, `ERROR`, `DEBUG`, `CRITICAL`
- Top 5 most frequent IP addresses
- Last 10 entries of level `ERROR` and `CRITICAL`
- Reads the file line by line, so large logs are not loaded into memory all at once
- Saves the report to `log_report.json`
- If the file doesn't exist, creates a sample log so you can try the tool right away

## Requirements

- Python 3.6 or newer
- Nothing else

## Running

Pass the file path as an argument:

```bash
python log_analyzer.py /var/log/app.log
```

Or run without arguments and the script will ask for the path:

```bash
python log_analyzer.py
```

The prompt reads "Введите путь к файлу логов (по умолчанию app.log)", i.e. "Enter the path to the log file (default: app.log)". Pressing Enter uses `app.log` from the current folder.

If your script has a different name, use that instead.

After the report, the script asks "Сохранить результат в JSON? (y/n)" (Save the result to JSON?). The answers `y`, `yes`, `да`, and `д` save the report to `log_report.json` in the current folder. Any other answer exits without saving.

## Supported log formats

A line can be in any format as long as it contains an uppercase level word and, if you want IP stats, an IPv4 address. For example:

```
2026-06-06 10:05:42 [ERROR] Database connection failed for IP 10.0.0.5.
```

Dates and times are not parsed, so their format doesn't matter.

## Example output

On the built-in sample log:

```
--------------------------------------------------
ОТЧЕТ ПО АНАЛИЗУ ЛОГОВ
--------------------------------------------------
Файл: app.log
Всего строк обработано: 6

Распределение по уровням:
  INFO    : 2
  WARNING : 1
  ERROR   : 2
  CRITICAL: 1

Топ IP-адресов:
  192.168.1.10   : 3 запросов
  10.0.0.5       : 1 запросов
  10.0.0.8       : 1 запросов

Последние ошибки (до 10 записей):
  [!] 2026-06-06 10:05:42 [ERROR] Database connection failed for IP 10.0.0.5.
  [!] 2026-06-06 10:07:22 [CRITICAL] Memory limit exceeded on server 10.0.0.8.
  [!] 2026-06-06 10:10:05 [ERROR] Failed to fetch data from IP 192.168.1.10.
--------------------------------------------------
```

The headings, in order: log analysis report, file, total lines processed, distribution by level, top IP addresses (with a "requests" label), last errors (up to 10 entries).

## JSON report format

```json
{
    "file_name": "app.log",
    "total_lines": 6,
    "log_levels": {
        "INFO": 2,
        "WARNING": 1,
        "ERROR": 2,
        "CRITICAL": 1
    },
    "top_ip_addresses": {
        "192.168.1.10": 3,
        "10.0.0.5": 1,
        "10.0.0.8": 1
    },
    "recent_errors": [
        "2026-06-06 10:05:42 [ERROR] Database connection failed for IP 10.0.0.5.",
        "2026-06-06 10:07:22 [CRITICAL] Memory limit exceeded on server 10.0.0.8.",
        "2026-06-06 10:10:05 [ERROR] Failed to fetch data from IP 192.168.1.10."
    ]
}
```

## Things to know

- **A missing file gets created.** If the given file doesn't exist, the script writes sample data to that path and analyzes it. With a typo in the path, you get a report on made-up data plus a stray file that you'll need to delete.
- **Only the first match per line counts.** One level and one IP address are counted per line, even if there are several.
- **The "requests" label in the report is loose.** What is actually counted is the number of lines in which the IP address appears.
- **Levels are matched in uppercase only**, and only from the list above. Entries with `FATAL`, `TRACE`, or lowercase `info` won't show up in the statistics.
- **IP addresses are not validated.** Anything of the form `number.number.number.number` matches, including `999.1.1.1` or a version number like `1.2.3.4`. IPv6 is not supported.
- **UTF-8 only.** A file in another encoding can't be read, and the script prints an error message.
- **`log_report.json` is overwritten without warning.**
- **The script is interactive.** The JSON question is always asked, even when the path is passed as an argument, so it isn't suitable for cron or other unattended runs without changes.

## Customizing

Everything is changed directly in the code:

- Set of levels: the `level_pattern` regular expression in `parse_log_file()`
- Number of IPs in the top list: `ip_addresses.most_common(5)`
- Number of recent errors: `errors_list[-10:]`
- Default file: `'app.log'` in `main()`
- Sample data: the `SAMPLE_LOG_CONTENT` constant

## Code structure

- `ensure_log_file_exists()`: creates a sample log if the file is missing
- `parse_log_file()`: reads the file and collects statistics
- `print_report()`: prints the report to the console
- `save_to_json()`: saves the report as JSON
- `main()`: argument handling and user prompts
