import asyncio
import aiohttp
import os
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()
prompt = Prompt(console=console)


async def download_image(session, url, filename, path, table):
    """Скачивает изображение и сохраняет в указанной директории"""
    status = "Ошибка"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                full_path = os.path.join(path, os.path.basename(filename))
                data = await response.read()
                with open(full_path, "wb") as f:
                    f.write(data)
                console.print(f"[green]Сохранено: {full_path}[/]")
                status = "Успех"
            else:
                console.print(f"[red]Ошибка загрузки {url}: статус {response.status}[/]")
            await update_downloads_table(table, url, status)
    except Exception as e:
        console.print(f"[red]Ошибка при загрузке {url}: {e}[/]")
        await update_downloads_table(table, url, status)


async def get_urls_and_start_downloads(session, path, table):
    """Читает ссылки от пользователя и запускает загрузку"""
    tasks = []
    counter = 1

    while True:
        url = input(f"Введите ссылку на изображение (или Enter, чтобы закончить): ").strip()
        if not url:
            return tasks

        filename = f"image_{counter}.jpg"
        task = asyncio.create_task(download_image(session, url, filename, path, table))
        tasks.append(task)
        counter += 1


async def get_valid_download_path():
    """Запрашивает у пользователя путь до папки, где будут сохранены изображения"""
    while True:
        path = prompt.ask("[bold blue]Введите путь для сохранения изображений", default=os.getcwd())

        # Проверяем, существует ли путь
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                console.print(f"[green]Создана новая директория: {path}[/]")
            except Exception as e:
                console.print(f"[red]Невозможно создать путь: {e}[/]")
                continue

        # Проверяем доступ на запись
        test_file = os.path.join(path, ".write_test")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            return path
        except (PermissionError, OSError) as e:
            console.print(f"[red]Нет прав на запись в эту папку: {e}[/]")


def get_downloads_table() -> Table:
    """Создаёт таблицу загрузок с текущей статистикой"""
    table = Table(title="Статистика загрузок")
    for title in ("Ссылка", "Статус"):
        table.add_column(title)

    return table


async def update_downloads_table(table, url, status):
    """Обновляет таблицу загрузок с текущей статистикой"""
    table.add_row(url, status)


async def main():
    path = await get_valid_download_path()
    table = get_downloads_table()
    async with aiohttp.ClientSession() as session:
        # Параллельно читаем ввод и запускаем загрузки
        tasks = await get_urls_and_start_downloads(session, path, table)

        # Ждём завершения всех загрузок
        if tasks:
            console.print("[blue]Загружаем последние файлы...[/]")
            await asyncio.gather(*tasks)
        console.print("[bold green]Все загрузки завершены.[/]")
        console.print(table)


if __name__ == "__main__":
    asyncio.run(main())
