"""
Скрипт для эмуляции нажатия мыши в определённое место на экране (Windows)

Использование:
    python mouse_click.py --x 100 --y 200
    python mouse_click.py --x 100 --y 200 --button left
    python mouse_click.py --x 100 --y 200 --button right --double
    python mouse_click.py --x 100 --y 200 --interval 5  # Клик каждые 5 секунд
    python mouse_click.py --x 100 --y 200 --interval 2 --count 10  # 10 кликов с интервалом 2 секунды
"""

import argparse 
import time
import sys

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


def click_with_pyautogui(x, y, button='left', double=False, delay=0.1, silent=False):
    """
    Эмуляция клика мыши с использованием pyautogui
    
    Args:
        x: Координата X
        y: Координата Y
        button: Кнопка мыши ('left', 'right', 'middle')
        double: Двойной клик
        delay: Задержка между кликами (для двойного клика)
        silent: Не выводить сообщение о клике
    """
    if not PYAUTOGUI_AVAILABLE:
        raise ImportError("pyautogui не установлена. Установите: pip install pyautogui")
    
    # Перемещаем курсор
    pyautogui.moveTo(x, y, duration=0.1)
    
    if double:
        pyautogui.doubleClick(x, y, button=button, interval=delay)
    else:
        pyautogui.click(x, y, button=button)
    
    if not silent:
        print(f"Клик выполнен в координатах ({x}, {y}) кнопкой {button}")


def click_with_win32api(x, y, button='left', double=False, delay=0.1, silent=False):
    """
    Эмуляция клика мыши с использованием win32api (более низкоуровневый метод)
    
    Args:
        x: Координата X
        y: Координата Y
        button: Кнопка мыши ('left', 'right', 'middle')
        double: Двойной клик
        delay: Задержка между кликами (для двойного клика)
        silent: Не выводить сообщение о клике
    """
    if not WIN32_AVAILABLE:
        raise ImportError("pywin32 не установлена. Установите: pip install pywin32")
    
    # Маппинг кнопок мыши
    button_map = {
        'left': (win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_LEFTUP),
        'right': (win32con.MOUSEEVENTF_RIGHTDOWN, win32con.MOUSEEVENTF_RIGHTUP),
        'middle': (win32con.MOUSEEVENTF_MIDDLEDOWN, win32con.MOUSEEVENTF_MIDDLEUP)
    }
    
    if button not in button_map:
        raise ValueError(f"Неизвестная кнопка: {button}. Используйте: left, right, middle")
    
    down_event, up_event = button_map[button]
    
    # Устанавливаем позицию курсора
    win32api.SetCursorPos((x, y))
    
    # Выполняем клик(и)
    if double:
        # Первый клик
        win32api.mouse_event(down_event, x, y, 0, 0)
        win32api.mouse_event(up_event, x, y, 0, 0)
        time.sleep(delay)
        # Второй клик
        win32api.mouse_event(down_event, x, y, 0, 0)
        win32api.mouse_event(up_event, x, y, 0, 0)
    else:
        win32api.mouse_event(down_event, x, y, 0, 0)
        win32api.mouse_event(up_event, x, y, 0, 0)
    
    if not silent:
        print(f"Клик выполнен в координатах ({x}, {y}) кнопкой {button}")


def get_current_mouse_position():
    """Получить текущую позицию курсора мыши"""
    if PYAUTOGUI_AVAILABLE:
        x, y = pyautogui.position()
        print(f"Текущая позиция курсора: ({x}, {y})")
        return x, y
    elif WIN32_AVAILABLE:
        x, y = win32api.GetCursorPos()
        print(f"Текущая позиция курсора: ({x}, {y})")
        return x, y
    else:
        print("Не установлены необходимые библиотеки для получения позиции курсора")
        return None, None


def click_repeat(x, y, interval, method='pyautogui', button='left', count=None):
    """
    Выполнить повторяющиеся клики с заданным интервалом
    
    Args:
        x: Координата X
        y: Координата Y
        interval: Интервал между кликами в секундах
        method: Метод эмуляции ('pyautogui' или 'win32api')
        button: Кнопка мыши ('left', 'right', 'middle')
        count: Количество кликов (None = бесконечно)
    """
    print(f"Начало автоматических кликов в позицию ({x}, {y})")
    print(f"Интервал: {interval} секунд")
    if count:
        print(f"Количество кликов: {count}")
    else:
        print("Количество кликов: бесконечно (нажмите Ctrl+C для остановки)")
    print("Нажмите Ctrl+C для остановки\n")
    
    click_count = 0
    
    try:
        while True:
            # Выполняем клик
            if method == 'pyautogui':
                click_with_pyautogui(x, y, button=button, silent=False)
            elif method == 'win32api':
                click_with_win32api(x, y, button=button, silent=False)
            
            click_count += 1
            
            # Проверяем, достигнуто ли нужное количество кликов
            if count and click_count >= count:
                print(f"\nВыполнено {click_count} кликов. Остановка.")
                break
            
            # Ждём перед следующим кликом
            if count is None or click_count < count:
                print(f"Следующий клик через {interval} секунд... (выполнено: {click_count})")
                time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n\nОстановлено пользователем. Выполнено кликов: {click_count}")
        sys.exit(0)
    except Exception as e:
        print(f"\nОшибка при выполнении клика: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Эмуляция нажатия мыши в определённое место на экране (Windows)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python mouse_click.py --x 100 --y 200
  python mouse_click.py --x 100 --y 200 --button right
  python mouse_click.py --x 100 --y 200 --double
  python mouse_click.py --get-position  # Получить текущую позицию курсора
  python mouse_click.py --x 100 --y 200 --interval 5  # Клик каждые 5 секунд
  python mouse_click.py --x 100 --y 200 --interval 2 --count 10  # 10 кликов с интервалом 2 секунды
        """
    )
    
    parser.add_argument('--x', type=int, help='Координата X')
    parser.add_argument('--y', type=int, help='Координата Y')
    parser.add_argument('--button', type=str, default='left', 
                       choices=['left', 'right', 'middle'],
                       help='Кнопка мыши (по умолчанию: left)')
    parser.add_argument('--double', action='store_true',
                       help='Выполнить двойной клик')
    parser.add_argument('--method', type=str, default='auto',
                       choices=['auto', 'pyautogui', 'win32api'],
                       help='Метод эмуляции (по умолчанию: auto)')
    parser.add_argument('--delay', type=float, default=0.1,
                       help='Задержка между кликами для двойного клика (секунды)')
    parser.add_argument('--interval', type=float, default=None,
                       help='Интервал между повторяющимися кликами в секундах (для автоматического режима)')
    parser.add_argument('--count', type=int, default=None,
                       help='Количество кликов при использовании --interval (по умолчанию: бесконечно)')
    parser.add_argument('--get-position', action='store_true',
                       help='Получить текущую позицию курсора мыши')
    
    try:
        args = parser.parse_args()
    except SystemExit:
        # argparse вызывает sys.exit() при ошибке или --help
        return
    
    # Если запрошена текущая позиция
    if args.get_position:
        get_current_mouse_position()
        return
    
    # Проверка обязательных параметров
    if args.x is None or args.y is None:
        parser.print_help()
        print("\nОшибка: Необходимо указать координаты --x и --y")
        sys.exit(1)
    
    # Выбор метода
    method = args.method
    if method == 'auto':
        if PYAUTOGUI_AVAILABLE:
            method = 'pyautogui'
        elif WIN32_AVAILABLE:
            method = 'win32api'
        else:
            print("Ошибка: Не установлены необходимые библиотеки!")
            print("Установите одну из библиотек:")
            print("  pip install pyautogui")
            print("  или")
            print("  pip install pywin32")
            sys.exit(1)
    
    # Проверка режима работы
    if args.interval is not None:
        # Режим повторяющихся кликов
        if args.interval <= 0:
            print("Ошибка: Интервал должен быть больше 0")
            sys.exit(1)
        
        if args.count is not None and args.count <= 0:
            print("Ошибка: Количество кликов должно быть больше 0")
            sys.exit(1)
        
        if args.double:
            print("Предупреждение: Режим повторяющихся кликов не поддерживает двойной клик. Используется одинарный клик.")
        
        click_repeat(args.x, args.y, args.interval, method, args.button, args.count)
    else:
        # Одиночный клик
        try:
            if method == 'pyautogui':
                click_with_pyautogui(args.x, args.y, args.button, args.double, args.delay)
            elif method == 'win32api':
                click_with_win32api(args.x, args.y, args.button, args.double, args.delay)
        except Exception as e:
            print(f"Ошибка при выполнении клика: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
