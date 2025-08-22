from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Person:
    """Класс для отображения человека"""
    first_name: str
    last_name: str

    def __post_init__(self):
        """Проверяет корректность данных после инициализации"""
        if not self.first_name or not self.last_name:
            raise ValueError("Имя и фамилия не могут быть пустыми")

        if not re.match(r'^[А-Яа-яA-Za-zёЁ\-]+$', self.first_name) or \
           not re.match(r'^[А-Яа-яA-Za-zёЁ\-]+$', self.last_name):
            raise ValueError("Имя и фамилия должны содержать только буквы")

    def get_full_name(self) -> str:
        """Геттер"""
        return f"{self.first_name}"

    def __str__(self):
        """Перегрузка строки"""
        return self.get_full_name()

    @staticmethod
    def ends_with_russian_vowel(s: str) -> bool:
        """Проверка последней гласной"""
        vowels = {'а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я'}
        return s[-1].lower() in vowels

    @property
    def sex(self) -> str:
        """Атрибут пола"""
        return 'women' if self.ends_with_russian_vowel(self.first_name) else 'men'
