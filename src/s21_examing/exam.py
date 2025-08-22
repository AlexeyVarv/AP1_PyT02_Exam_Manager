import random
from .person import Person

class Exam:
    def __init__(self, examiner: Person, student: Person, question: str) -> None:
        self.examiner = examiner
        self.student = student
        self.question = question.split()

    def random_answer_from_list(self) -> str | None:
        """Возвращает случайное слово(ответ) из вопроса"""
        f_const = 1.618
        if self.question:
            weights = self.calculate_weights(f_const)

            return random.choices(self.question, weights=weights, k=1)[0]
        return None

    def calculate_weights(self, f_const):
        """Возвращает список веса (вероятности выбора) слова в вопросе"""
        if not self.question:
            return []

        n = len(self.question)
        weights = []
        total = 0.0

        for i in range(n):
            if i == 0:
                weight = 1 / f_const
            elif i == n - 1:
                weight = 1 - total
            else:
                weight = (1 - total) / f_const

            weights.append(weight)
            total += weight

        return weights

    def get_student_answer(self) -> str | None:
        """Возвращает ответ студента в зависимости от пола"""
        if self.question:
            if self.student.sex == 'women':
                self.question = self.question[::-1]

            return self.random_answer_from_list()
        return None

    def get_examiner_answer(self) -> list | None:
        """Возвращает список ответов (минимум 1 ответ) экзаменатора в зависимости от пола"""
        if self.question:
            if self.examiner.sex == 'women':
                self.question = self.question[::-1]

        examiner_answer = [(self.random_answer_from_list())]

        if examiner_answer:
            while self.question:
                if random.random() < 2 / 3:
                    break
                self.question.remove(examiner_answer[-1])
                if self.question:
                    examiner_answer.append(self.random_answer_from_list())
            return examiner_answer
        return None

    def check_answer(self) -> bool:
        """
        Возвращает результат экзамена -
        если ответ студента есть в списке экзаменатора, то True,
        если нет, то False
        """
        student_answer = self.get_student_answer()
        right_answer_list = self.get_examiner_answer()
        if student_answer in right_answer_list:
            return True
        return False