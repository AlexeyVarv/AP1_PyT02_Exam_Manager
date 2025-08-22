class FileReader:
    def __init__(self, filename):
        self.filename = filename

    def read_persons(self) -> list:
        """
        Возвращает список [first_name, last_name] из файла или выбрасывает исключение,
        если файл пуст или содержит неверные данные
        """
        persons_list = []

        try:
            with open(self.filename, 'r', encoding='UTF-8') as file:
                lines = [line.strip() for line in file.readlines()]

                # Проверяем, есть ли вообще строки
                if not lines:
                    raise ValueError(f"Файл '{self.filename}' пуст")

                for line in lines:
                    if not line:
                        continue  # пропускаем пустые строки

                    parts = line.split()
                    if len(parts) >= 2:
                        persons_list.append(parts[:2])
                    else:
                        raise ValueError(f"Строка игнорируется (слишком мало данных): {line}")

            return persons_list

        except FileNotFoundError:
            print(f"Файл '{self.filename}' не найден.")
            raise
        except PermissionError:
            print(f"Нет прав на чтение файла '{self.filename}'.")
            raise
        except Exception as e:
            print(f"Произошла ошибка при чтении файла: {e}")
            raise

    def read_questions(self) -> list:
        """
        Возвращает список строк
        """
        questions_list = []
        try:
            with open(self.filename, 'r', encoding='UTF-8') as file:
                for line in file:
                    question = line.strip()
                    if question:
                        questions_list.append(question)
                    else:
                        print("[warn] Пустая строка в файле вопросов — пропущена")
            if len(questions_list) >= 3:
                return questions_list
            else:
                raise ValueError("Недостаточно вопросов для формирования списка")
        except FileNotFoundError:
            print(f"[ERROR] Файл '{self.filename}' не найден.")
            raise
        except PermissionError:
            print(f"[ERROR] Нет прав на чтение файла '{self.filename}'")
            raise
        except Exception as e:
            print(f"[ERROR] Неожиданная ошибка при чтении: {e}")
            raise