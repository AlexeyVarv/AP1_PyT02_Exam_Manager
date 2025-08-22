import asyncio
import random
from collections import deque

from .exam import Exam
from .exam_statistics import ExamStatistics
from .person import Person

class ExamManager:
    def __init__(self, examiners: list, students: list, questions: list) -> None:
        self.__examiners = self.make_queue(examiners)
        self.__students = self.make_queue(students)
        self.__questions = questions
        self.lock = asyncio.Lock()
        self.statistics = ExamStatistics(self.__students, self.__examiners)

    @staticmethod
    def make_queue(person_list: list) -> deque:
        """Создаёт очередь из списка [first_name, last_name]"""
        queue = deque()
        for first, last in person_list:
            try:
                person = Person(first, last)
                queue.append(person)
            except ValueError as e:
                print(f"[ERROR] Ошибка создания Person: {e}")
                raise
        return queue

    def get_examiner(self) -> Person | None:
        """Возвращает первый объект класса Person из очереди"""
        if self.__examiners:
            return self.__examiners.popleft()
        return None

    def get_student(self) -> Person | None:
        """Возвращает последний объект класса Person из очереди"""
        if self.__students:
            return self.__students.popleft()
        return None

    def get_question_list(self, number=3) -> str | None:
        """Возвращает несколько(по умолчанию 3) вопросов из списка вопросов"""
        try:
            if self.__questions and len(self.__questions) >= 3:
                return random.sample(self.__questions, number)
            else:
                raise ValueError("Недостаточно вопросов для формирования списка")
        except ValueError:
            raise

    def get_statistics(self):
        """Возвращает атрибут statistics"""
        return self.statistics

    async def run_exam(self):
        """Запускает процесс экзамена в несколько потоков по числу экзаменаторов"""
        try:
            tasks = [self.make_exam_slot_a(examiner) for examiner in self.__examiners]
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"[ERROR] Ошибка запуска экзамена: {e}")

    async def make_exam_slot_a(self, examiner) -> None:
        """Моделирует процесс экзамена по заданным условиям"""
        lunch_flag = 0
        while True:
            # Проверяем, нужно ли уйти на обед
            current_time = self.statistics.get_examiner_work_time(examiner)
            if lunch_flag:
                self.statistics.set_examiner_have_luch(examiner, False)

            if current_time >= 30.0 and not lunch_flag:
                lunch_time = random.uniform(12, 18)
                lunch_flag = 1
                self.statistics.set_examiner_have_luch(examiner, True)
                await asyncio.sleep(lunch_time)
                continue

            async with self.lock:
                student = self.get_student()
                self.statistics.assign_student_to_examiner(examiner, student)
                if not student:
                    return

                questions = random.sample(self.__questions, 3)

            time_spent_sec = random.uniform(*self.get_len_exam(examiner))

            # Обработка вопросов
            res_list = []
            for question in questions:
                slot = Exam(examiner, student, question)
                answer = slot.check_answer()
                if answer:
                    async with self.lock:
                        self.statistics.make_questions_dict(question)
                res_list.append(answer)
            result: bool
            rand = random.random()
            if rand < 0.125:
                result = False
            elif rand < 0.25:
                result = True
            else:
                result = res_list.count(True) > res_list.count(False)

            await asyncio.sleep(time_spent_sec)

            async with self.lock:
                self.statistics.update_examiner_stats(examiner, result, time_spent_sec)
                self.statistics.update_student_stats(student, result, time_spent_sec)
                self.statistics.num_student_in_queue -= 1
            # await asyncio.sleep(time_spent_sec)

    @staticmethod
    def get_len_exam(examiner: Person) -> tuple[int, int]:
        """Возвращает длительность экзамена в зависимости от имени экзаменатора"""
        return len(examiner.first_name) - 1, len(examiner.first_name) + 1
