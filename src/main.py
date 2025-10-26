import argparse
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Точка входа приложения."""
    parser = argparse.ArgumentParser(description="Обработка аргументов.")
    parser.add_argument(
        "task_type", type=str, help="Тип решаемой задачи", choices=["generate", "solve"]
    )
    parser.add_argument("--algorithm", type=str, help="Второе слово")
    parser.add_argument("--width", type=int, help="Ширина лабиринта", default=None)
    parser.add_argument("--height", type=int, help="Длина лабиринта", default=None)
    parser.add_argument(
        "--file", type=str, help="Файл с описанием лабиринта", default=None
    )
    parser.add_argument(
        "--start", type=str, help="Начальная точка маршрута", default=None
    )
    parser.add_argument("--end", type=str, help="Конечная точка маршрута", default=None)
    parser.add_argument(
        "--output", type=str, help="Путь для сохранения лабиринта", default=None
    )

    args = parser.parse_args()

    print(args)


if __name__ == "__main__":
    main()
