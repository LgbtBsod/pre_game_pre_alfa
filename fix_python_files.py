import os
import re
import ast
import tokenize
import io
from collections import defaultdict
from typing import List, Tuple

def fix_indentation(content):
    """Заменяет табы на 4 пробела и нормализует отступы."""
    lines = content.splitlines()
    fixed_lines = []
    
    for line in lines:
        fixed_line = line.replace('\t', '    ')
        stripped = fixed_line.lstrip()
        if stripped:
            indent = len(fixed_line) - len(stripped)
            if indent % 4 != 0:
                new_indent = (indent // 4) * 4
                fixed_line = ' ' * new_indent + stripped
        fixed_lines.append(fixed_line)
    
    return '\n'.join(fixed_lines)

def fix_try_except(content):
    """Исправляет голые except и пустые блоки."""
    lines = content.splitlines()
    fixed_lines = []
    i = 0
    n = len(lines)
    
    while i < n:
        line = lines[i]
        stripped = line.strip()
        
        if stripped.startswith('try:'):
            # Найдем блок try
            try_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            i += 1
            
            # Собираем весь блок try
            try_block = []
            while i < n:
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= try_indent and next_line.strip() != '':
                    break
                try_block.append(next_line)
                i += 1
            
            # Обрабатываем блок except
            if i < n and lines[i].strip().startswith('except'):
                except_line = lines[i]
                except_stripped = except_line.strip()
                except_indent = len(except_line) - len(except_line.lstrip())
                
                if except_stripped == 'except:':
                    fixed_lines.append(' ' * except_indent + 'except Exception:')
                else:
                    fixed_lines.append(except_line)
                i += 1
                
                # Собираем блок except
                except_block = []
                while i < n:
                    next_line = lines[i]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= except_indent and next_line.strip() != '':
                        break
                    except_block.append(next_line)
                    i += 1
                
                # Проверяем, пуст ли блок except
                non_empty = [l for l in except_block if l.strip() and not l.strip().startswith('#')]
                if not non_empty:
                    fixed_lines.append(' ' * (except_indent + 4) + 'pass')
                else:
                    fixed_lines.extend(except_block)
            else:
                fixed_lines.extend(try_block)
        else:
            fixed_lines.append(line)
            i += 1
    
    return '\n'.join(fixed_lines)

def fix_empty_blocks(content):
    """Удаляет пустые блоки и добавляет pass где необходимо."""
    lines = content.splitlines()
    fixed_lines = []
    i = 0
    n = len(lines)
    
    while i < n:
        line = lines[i]
        stripped = line.strip()
        
        # Обработка блоков, требующих содержимого
        block_keywords = ['if', 'elif', 'else:', 'for', 'while', 'with', 'def', 'class']
        if any(stripped.startswith(keyword) for keyword in block_keywords):
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            i += 1
            
            # Собираем содержимое блока
            block_content = []
            while i < n:
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= indent and next_line.strip() != '':
                    break
                block_content.append(next_line)
                i += 1
            
            # Проверяем, пуст ли блок
            non_empty = [l for l in block_content if l.strip() and not l.strip().startswith('#')]
            if not non_empty:
                fixed_lines.append(' ' * (indent + 4) + 'pass')
            else:
                fixed_lines.extend(block_content)
        else:
            fixed_lines.append(line)
            i += 1
    
    return '\n'.join(fixed_lines)

def fix_redundant_else(content):
    """Удаляет лишние блоки else в try-except."""
    lines = content.splitlines()
    fixed_lines = []
    i = 0
    n = len(lines)
    
    while i < n:
        line = lines[i]
        stripped = line.strip()
        
        if stripped == 'else:':
            indent = len(line) - len(line.lstrip())
            # Проверяем предыдущие строки на наличие except
            has_except = False
            for j in range(i-1, max(i-10, -1), -1):
                prev_line = lines[j]
                prev_indent = len(prev_line) - len(prev_line.lstrip())
                if prev_indent < indent and 'except' in prev_line:
                    has_except = True
                    break
            
            if has_except:
                # Собираем содержимое блока else
                j = i + 1
                block_content = []
                while j < n:
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent and next_line.strip() != '':
                        break
                    block_content.append(next_line)
                    j += 1
                
                # Проверяем, пуст ли блок else
                non_empty = [l for l in block_content if l.strip() and not l.strip().startswith('#')]
                if not non_empty:
                    i = j  # Пропускаем блок else
                    continue
                else:
                    fixed_lines.append(line)
                    fixed_lines.extend(block_content)
                    i = j
                    continue
            else:
                fixed_lines.append(line)
                i += 1
        else:
            fixed_lines.append(line)
            i += 1
    
    return '\n'.join(fixed_lines)

def fix_imports(content):
    """Сортирует импорты и группирует по типам."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return content

    imports = defaultdict(list)
    import_nodes = []
    last_import_line = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if hasattr(node, 'lineno') and node.lineno > last_import_line:
                import_nodes.append(node)
                last_import_line = node.lineno

    for node in import_nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports['standard'].append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports['third_party'].append(f"from {module} import {alias.name}")

    sorted_imports = []
    for category in ['standard', 'third_party']:
        if imports[category]:
            sorted_imports.extend(sorted(set(imports[category])))
            sorted_imports.append('')

    if not import_nodes:
        return content

    lines = content.splitlines()
    start_line = min(node.lineno for node in import_nodes) - 1
    end_line = max(node.end_lineno for node in import_nodes if hasattr(node, 'end_lineno')) - 1

    new_content = (
        '\n'.join(lines[:start_line]) + '\n' +
        '\n'.join(sorted_imports) +
        '\n'.join(lines[end_line + 1:])
    )
    
    return new_content

def fix_syntax_errors(content):
    """Исправляет распространенные синтаксические ошибки."""
    # Исправляем опечатки в ключевых словах
    replacements = {
        r'imp or t': 'import',
        r'logg in g': 'logging',
        r' in sert': 'insert',
        r' in g': 'ing',
        r' in ': 'in ',
        r'f or mat': 'format',
        r'f or ': 'for ',
        r' and ': 'and ',
        r' is ': 'is ',
        r'pr in t': 'print',
        r'==': '=',
        r'= =': '==',
        r': =': ':=',
        r'=:': '=',
        r' % ': '%',
        r' %': '%',
        r'% ': '%',
    }
    
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)
    
    # Добавление двоеточий после управляющих конструкций
    content = re.sub(r'(if|elif|else|for|while|with|def|class)\s*(\([^)]*\))?\s*$(?=\s*[^#\s])', r'\1\2:', content, flags=re.MULTILINE)
    
    # Удаление лишних запятых в вызовах функций
    content = re.sub(r',(\s*[\]\}])', r'\1', content)
    
    return content

def validate_python_syntax(content):
    """Проверяет, является ли содержимое валидным Python-кодом."""
    try:
        ast.parse(content)
        return True
    except SyntaxError:
        return False

def create_backup(filepath):
    """Создает резервную копию файла."""
    backup_path = filepath + '.bak'
    try:
        with open(filepath, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        return True
    except Exception:
        return False

def process_file(filepath):
    """Обрабатывает один Python-файл."""
    # Проверяем, не является ли файл самим скриптом
    if os.path.abspath(filepath) == os.path.abspath(__file__):
        print(f"Пропуск самого себя: {filepath}")
        return
        
    # Создаем резервную копию
    if not create_backup(filepath):
        print(f"Не удалось создать резервную копию: {filepath}")
        return
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка чтения файла {filepath}: {e}")
        return

    original_content = content

    # Проверяем исходный синтаксис
    original_valid = validate_python_syntax(content)
    
    # Последовательное применение исправлений
    content = fix_indentation(content)
    content = fix_syntax_errors(content)
    content = fix_try_except(content)
    content = fix_empty_blocks(content)
    content = fix_redundant_else(content)
    content = fix_imports(content)

    # Проверяем итоговый синтаксис
    final_valid = validate_python_syntax(content)
    
    if not final_valid and original_valid:
        print(f"Исправления сломали синтаксис: {filepath}. Восстанавливаем из резервной копии.")
        # Восстанавливаем из резервной копии
        try:
            with open(filepath + '.bak', 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(backup_content)
        except Exception as e:
            print(f"Ошибка восстановления из резервной копии: {filepath}: {e}")
        return

    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Исправлен: {filepath}")
        except Exception as e:
            print(f"Ошибка записи в файл {filepath}: {e}")
    else:
        print(f"Без изменений: {filepath}")
        
    # Удаляем резервную копию, если она больше не нужна
    try:
        if os.path.exists(filepath + '.bak'):
            os.remove(filepath + '.bak')
    except Exception:
        pass

def main():
    """Основная функция для обхода директорий."""
    current_dir = os.getcwd()
    for root, _, files in os.walk(current_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                process_file(filepath)

if __name__ == '__main__':
    main()