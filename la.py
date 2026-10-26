from collections import Counter
import json
import os
import re
import sys


SAMPLE_LOG_CONTENT = """2026-06-06 10:00:01 [INFO] User 192.168.1.10 logged in successfully.
2026-06-06 10:01:15 [WARNING] Low disk space on partition /var.
2026-06-06 10:05:42 [ERROR] Database connection failed for IP 10.0.0.5.
2026-06-06 10:06:00 [INFO] Reconnecting to database from IP 192.168.1.10...
2026-06-06 10:07:22 [CRITICAL] Memory limit exceeded on server 10.0.0.8.
2026-06-06 10:10:05 [ERROR] Failed to fetch data from IP 192.168.1.10.
"""


def ensure_log_file_exists(file_path):
  """Проверяет существование файла и создает тестовый, если он отсутствует."""
  if not os.path.exists(file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
      f.write(SAMPLE_LOG_CONTENT)
    print(
        f'[INFO] Файл "{file_path}" не найден. Создан тестовый лог-файл для'
        ' проверки.\n'
    )


def parse_log_file(file_path):
  """Считывает лог-файл и собирает ключевую статистику."""
  ensure_log_file_exists(file_path)

  level_pattern = re.compile(r'\b(INFO|WARNING|ERROR|DEBUG|CRITICAL)\b')
  ip_pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

  total_lines = 0
  log_levels = Counter()
  ip_addresses = Counter()
  errors_list = []

  print(f'Обработка файла: {file_path}...')

  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      for line in f:
        total_lines += 1
        line_clean = line.strip()

        
        level_match = level_pattern.search(line_clean)
        if level_match:
          level = level_match.group(1)
          log_levels[level] += 1

          if level in ('ERROR', 'CRITICAL'):
            errors_list.append(line_clean)

        # Поиск IP-адреса
        ip_match = ip_pattern.search(line_clean)
        if ip_match:
          ip = ip_match.group(0)
          ip_addresses[ip] += 1

  except Exception as e:
    print(f'[ERROR] Не удалось прочитать файл: {e}')
    return None

  return {
      'file_name': os.path.basename(file_path),
      'total_lines': total_lines,
      'log_levels': dict(log_levels),
      'top_ip_addresses': dict(ip_addresses.most_common(5)),
      'recent_errors': errors_list[-10:],
  }


def print_report(report):
  """Форматирует и выводит отчет в консоль."""
  if not report:
    return

  divider = '-' * 50

  print('\n' + divider)
  print('ОТЧЕТ ПО АНАЛИЗУ ЛОГОВ')
  print(divider)
  print(f"Файл: {report['file_name']}")
  print(f"Всего строк обработано: {report['total_lines']}")

  print('\nРаспределение по уровням:')
  if report['log_levels']:
    for level, count in report['log_levels'].items():
      print(f'  {level:<8}: {count}')
  else:
    print('  Уровни логов не найдены.')

  print('\nТоп IP-адресов:')
  if report['top_ip_addresses']:
    for ip, count in report['top_ip_addresses'].items():
      print(f'  {ip:<15}: {count} запросов')
  else:
    print('  IP-адреса не найдены.')

  print('\nПоследние ошибки (до 10 записей):')
  if report['recent_errors']:
    for err in report['recent_errors']:
      print(f'  [!] {err}')
  else:
    print('  Ошибки не обнаружены.')

  print(divider + '\n')


def save_to_json(report, output_file='log_report.json'):
  """Сохраняет итоговый отчет в JSON."""
  try:
    with open(output_file, 'w', encoding='utf-8') as f:
      json.dump(report, f, ensure_ascii=False, indent=4)
    print(f'[УСПЕХ] Отчет сохранен в файл: {output_file}')
  except Exception as e:
    print(f'[ОШИБКА] Не удалось сохранить отчет: {e}')


def main():
  if len(sys.argv) > 1:
    log_path = sys.argv[1]
  else:
    user_input = input(
        'Введите путь к файлу логов (по умолчанию app.log): '
    ).strip()
    log_path = user_input if user_input else 'app.log'

  report_data = parse_log_file(log_path)

  if report_data:
    print_report(report_data)

    save_choice = (
        input('Сохранить результат в JSON? (y/n): ').strip().lower()
    )
    if save_choice in ('y', 'yes', 'да', 'д'):
      save_to_json(report_data)


if __name__ == '__main__':
  main()
