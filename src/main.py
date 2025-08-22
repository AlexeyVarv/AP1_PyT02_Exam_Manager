import asyncio
from s21_examing import ExamManager
from s21_examing import FileReader

def main():
    try:
        students = FileReader('students.txt').read_persons()
        examiners = FileReader('examiners.txt').read_persons()
        questions = FileReader('questions.txt').read_questions()
        test_exam = ExamManager(examiners, students, questions)
        asyncio.run(main_async(test_exam))
    except Exception as e:
        print(f"[ERROR] Ошибка во входных данных: {e}")

async def main_async(manager):
    try:
        exam_task = asyncio.create_task(manager.run_exam())
        stats_task = asyncio.create_task(manager.statistics.update_both_tables())
        await asyncio.gather(exam_task, stats_task)
    except Exception as e:
        print(f"[ERROR] Ошибка в ходе экзамена: {e}")

if __name__ == "__main__":
    main()