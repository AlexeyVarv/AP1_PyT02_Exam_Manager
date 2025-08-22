import asyncio
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

from .person import Person

console = Console()

class ExamStatistics:
    STUDENT_STATUSES = ('Очередь', 'Сдал', 'Провалил')
    STUDENT_INDICATORS_TITLES = ('Студент', 'Статус')
    EXAMINERS_INDICATORS_TITLES = ('Экзаменатор', 'Текущий студент', 'Всего студентов', 'Завалил', 'Время работы')
    FINAL_INDICATORS_TITLES = ('Экзаменатор', 'Всего студентов', 'Завалил', 'Время работы')

    def __init__(self, students_queue=None, examiners_queue=None) -> None:
        self.students_queue = students_queue
        self.examiners_queue = examiners_queue

        self.students_stat_dict = {}
        self.examiners_stat_dict = {}
        self.questions_stat_dict = defaultdict(int)
        self.num_student_in_queue = 0
        self.lock = asyncio.Lock()

        if students_queue:
            self.make_students_dict()
            self.num_student_in_queue = len(students_queue)

        if examiners_queue:
            self.make_examiners_dict()

    def make_students_dict(self) -> None:
        """Создаёт словарь статусов для студентов"""
        for student in self.students_queue:
            self.students_stat_dict[student] = {
                "student_status": self.STUDENT_STATUSES[0],
                "time_spent": 0.0
            }

    def make_examiners_dict(self) -> None:
        """Создаёт словарь статистики для экзаменаторов"""
        for examiner in self.examiners_queue:
            self.examiners_stat_dict[examiner] = {
                "current_student": None,
                "total_students": 0,
                "failed_students": 0,
                "time_worked": 0.0,
                "on_lunch_break": False
            }

    def make_questions_dict(self, question: str, result=1) -> None:
        """Создаёт словарь верно отвеченных вопросов"""
        self.questions_stat_dict[question] += result

    def assign_student_to_examiner(self, examiner: Person, student: Person) -> None:
        """Вносит в словарь экзаменаторов текущего студента"""
        stats = self.examiners_stat_dict[examiner]
        stats["current_student"] = student

    def update_examiner_stats(self, examiner: Person, result: int, time_spent: float) -> None:
        """Вносит в словарь экзаменаторов статистику экзамена"""
        stats = self.examiners_stat_dict[examiner]
        stats["total_students"] += 1
        if not result:
            stats["failed_students"] += 1
        stats["time_worked"] += time_spent

    def update_student_stats(self, student: Person, result:int, time_spent: float) -> None:
        """Вносит в словарь статистику студента"""
        stats = self.students_stat_dict[student]
        if result:
            stats["student_status"] = ExamStatistics.STUDENT_STATUSES[1]
        else:
            stats["student_status"] = ExamStatistics.STUDENT_STATUSES[2]
        stats["time_spent"] = time_spent

    def get_exam_time(self) -> float:
        """Возвращает длительность экзамена(максимум по экзаменаторам)"""
        return max(
            stat["time_worked"] for stat in self.examiners_stat_dict.values()
        )

    def get_all_best_examiners(self) -> list[tuple[Person, float]]:
        """Ищем лучшего экзаменатора. Возвращает список кортежей (экзаменатор, время экзамена)"""
        all_with_rate = [
            (examiner, stat["failed_students"] / stat["total_students"])
            for examiner, stat in self.examiners_stat_dict.items()
            if stat["total_students"] > 0
        ]

        # Находим минимальное значение провала
        if not all_with_rate:
            return []

        min_rate = min(all_with_rate, key=lambda x: x[1])[1]

        # Фильтруем всех экзаменаторов с этим минимумом
        best_examiners = [item[0] for item in all_with_rate if item[1] == min_rate]
        return best_examiners

    def get_all_best_students(self) -> list[tuple[Person, float]]:
        """Ищем лучшего студента. Возвращает список кортежей (студент, время экзамена)"""
        all_with_rate = [
            (student, stat["time_spent"])
            for student, stat in self.students_stat_dict.items()
            if stat["student_status"] == ExamStatistics.STUDENT_STATUSES[1]
        ]

        if not all_with_rate:
            return []

        min_rate = min(all_with_rate, key=lambda x: x[1])[1]

        # Фильтруем всех студентов с этим минимумом
        best_students = [item[0] for item in all_with_rate if item[1] == min_rate]
        return best_students

    def get_all_failed_students(self) -> list[tuple[Person, float]]:
        """Ищем худшего студента. Возвращает список кортежей (студент, время экзамена)"""
        all_with_rate = [
            (student, stat["time_spent"])
            for student, stat in self.students_stat_dict.items()
            if stat["student_status"] == ExamStatistics.STUDENT_STATUSES[2]
        ]

        if not all_with_rate:
            return []

        min_rate = min(all_with_rate, key=lambda x: x[1])[1]

        # Фильтруем всех студентов с этим минимумом
        failed_students = [item[0] for item in all_with_rate if item[1] == min_rate]
        return failed_students

    def get_all_best_questions(self) -> list[tuple[str, int]]:
        """Лучший вопрос. Возвращает список кортежей (вопрос, количество правильных ответов)"""
        if not self.questions_stat_dict:
            return []

        max_count = max(self.questions_stat_dict.values())
        best_questions = [
            question
            for question, count in self.questions_stat_dict.items()
            if count == max_count
        ]
        return best_questions

    def get_exam_summary(self, success_goal=0.85) -> bool:
        """Вывод, удался экзамен или нет (экзамен удался, если сдало больше 85% студентов)"""
        sum_fail = sum(values["failed_students"] for values in self.examiners_stat_dict.values())
        total_students = sum(values["total_students"] for values in self.examiners_stat_dict.values())

        return False if not total_students else (1 - sum_fail / total_students) > success_goal

    def get_examiners_table(self) -> Table:
        """Создаёт таблицу экзаменаторов с текущей статистикой"""
        table = Table(title="Статистика экзаменаторов")
        for title in self.EXAMINERS_INDICATORS_TITLES:
            table.add_column(title)

        for examiner, stats in self.examiners_stat_dict.items():
            row = [
                str(examiner),
                str(stats["current_student"]) if stats["current_student"] and not stats["on_lunch_break"] else "-",
                str(stats["total_students"]),
                str(stats["failed_students"]),
                f"{stats['time_worked']:.2f} сек"
            ]
            table.add_row(*row)

        return table

    def get_students_table(self) -> Table:
        """Создаёт таблицу студентов с текущей статистикой"""
        table = Table(title="Статистика студентов")
        for title in self.STUDENT_INDICATORS_TITLES:
            table.add_column(title)

        sorted_students = sorted(
            self.students_stat_dict.items(),
            key=lambda item: self.STUDENT_STATUSES.index(item[1]["student_status"])
        )

        for student, stats in sorted_students:
            row = [
                str(student),
                str(stats["student_status"])
            ]
            table.add_row(*row)

        return table

    def get_final_table(self) -> Table:
        """Создаёт итоговую таблицу экзаменаторов с текущей статистикой"""
        table = Table(title="Итоговая статистика")
        for title in self.FINAL_INDICATORS_TITLES:
            table.add_column(title)

        for examiner, stats in self.examiners_stat_dict.items():
            row = [
                str(examiner),
                str(stats["total_students"]),
                str(stats["failed_students"]),
                f"{stats['time_worked']:.2f} сек"
            ]
            table.add_row(*row)

        return table

    def get_examiner_work_time(self, examiner) -> float:
        """Возвращает время работы конкретного экзаменатора"""
        stats = self.examiners_stat_dict.get(examiner, {})
        return stats.get("time_worked", 0.0)

    def set_examiner_have_luch(self, examiner, have_lunch: bool) -> bool:
        """Устанавливает, обедает ли экзаменатор сейчас"""
        if examiner in self.examiners_stat_dict:
            self.examiners_stat_dict[examiner]["on_lunch_break"] = have_lunch
            return True
        return False

    def get_accompanying_info_text(self) -> str:
        """Возвращает строку с информацией о текущем состоянии экзамена"""
        time_total = self.get_exam_time()
        students_left = len(self.students_queue)
        return (f"[bold]Осталось в очереди[/]: {students_left}\n"
                f"[bold]Время с момента начала экзамена[/]: {time_total:0.2f} сек")

    def get_summary_info_text(self) -> str:
        """Возвращает строку с информацией об итоге экзамена"""
        time_total = self.get_exam_time()
        best_students = self.get_all_best_students()
        best_examiners = self.get_all_best_examiners()
        failed_students = self.get_all_failed_students()
        best_questions = self.get_all_best_questions()
        exam_summary = "экзамен удался" if self.get_exam_summary() else "экзамен не удался"
        return (
            f"[bold]Время с момента начала экзамена и до момента и его завершения:[/] {time_total:.2f} сек\n"
            f"[bold]Имена лучших студентов:[/] {self.format_list(best_students, style='green')}\n"
            f"[bold]Имена лучших экзаменаторов:[/] {self.format_list(best_examiners, style='blue')}\n"
            f"[bold]Имена студентов, которых после экзамена отчислят:[/] "
            f"{self.format_list(failed_students, style='red')}\n"
            f"[bold]Лучшие вопросы:[/] {self.format_list(best_questions, style='yellow')}\n"
            f"[bold]Вывод:[/] {exam_summary}\n"
        )

    @staticmethod
    def format_list(items, style="") -> str:
        """Возвращает строку из итерируемого объекта"""
        if not items:
            return "[i]нет данных[/]"
        str_items = [str(item) for item in items]
        if style:
            str_items = [f"[{style}]{item}[/{style}]" for item in str_items]
        return ", ".join(str_items)

    def get_layout(self) -> Panel:
        """Возвращает панель из объектов библиотеки rich"""
        layout = Layout()
        layout.split(
            Layout(name="students", renderable=self.get_students_table(), size=13),
            Layout(name="examiners", renderable=self.get_examiners_table() if self.num_student_in_queue \
                else self.get_final_table()),
            Layout(name="footer", renderable=self.get_accompanying_info_text() if self.num_student_in_queue \
                else self.get_summary_info_text()),

        )
        return Panel(layout, title="📊 Экзамен", border_style="blue")

    async def update_both_tables(self, interval=1) -> None:
        """Управляет обновлением информации о ходе экзамена при изменении состояния"""
        prev_examiner_state = self._get_examiner_state()
        prev_student_state = self._get_student_state()

        with Live(self.get_layout(), refresh_per_second=4, console=console) as live:
            while True:
                curr_examiner_state = self._get_examiner_state()
                curr_student_state = self._get_student_state()

                if curr_examiner_state != prev_examiner_state or curr_student_state != prev_student_state:
                    live.update(self.get_layout())
                    prev_examiner_state = curr_examiner_state
                    prev_student_state = curr_student_state

                async with self.lock:
                    if not self.num_student_in_queue:
                        live.update(self.get_layout())
                        break

                await asyncio.sleep(interval)

    def _get_examiner_state(self) -> tuple:
        """Возвращает текущее состояние словаря экзаменаторов"""
        return tuple(
            (examiner, stat["current_student"], stat["total_students"],
             stat["failed_students"], stat["time_worked"], stat["on_lunch_break"])
            for examiner, stat in self.examiners_stat_dict.items()
        )

    def _get_student_state(self) -> tuple:
        """Возвращает текущее состояние словаря студентов"""
        return tuple(
            (student, status)
            for student, status in self.students_stat_dict.items()
        )