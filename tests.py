from course import Student, Course
from survey import Question, Answer, MultipleChoiceQuestion, NumericQuestion, \
    YesNoQuestion, CheckboxQuestion, Survey
from criterion import HomogeneousCriterion, InvalidAnswerError, \
    HeterogeneousCriterion, LonelyMemberCriterion
import grouper
import pytest


def test_student() -> None:
    s = Student(1, "John")
    assert s.id == 1
    assert s.name == "John"
    str(s) == "John"


def test_student_set_answer():
    student = Student(1, "Jane")
    q1 = Question(1, "How are you")
    a1 = Answer("good")
    q2 = Question(2, "hello")
    a2 = Answer("hi")
    a3 = Answer("test")
    student.set_answer(q1, a1)
    student.set_answer(q2, a2)
    student.set_answer(q2, a3)
    assert student.get_answer(q1) == a1
    assert student.get_answer(q2) == a3


def test_student_get_answer() -> None:
    student = Student(1, "Jane")
    q1 = Question(1, "How are you")
    a1 = Answer("good")
    q2 = Question(2, "hello")
    a2 = Answer("hi")
    assert student.get_answer(q1) is None
    student.set_answer(q1, a1)
    student.set_answer(q2, a2)
    assert student.get_answer(q1) == a1
    assert student.get_answer(q2) == a2


def test_course_enrol_students() -> None:
    student_1 = Student(1, "Jane")
    student_2 = Student(2, "John")
    course = Course("math")
    lst = [student_1, student_2]
    course.enroll_students(lst)
    assert course.students == [student_1, student_2]


def test_course_get_students() -> None:
    student_1 = Student(2, "Jane")
    student_2 = Student(1, "John")
    course = Course("math")
    lst = [student_1, student_2]
    course.enroll_students(lst)
    assert course.get_students() == (student_2, student_1)


def test_course_all_answered() -> None:
    student_1 = Student(2, "Jane")
    student_2 = Student(1, "John")
    course = Course("math")
    course_2 = Course("Eng")
    lst = [student_1, student_2]
    lst_2 = [student_1]
    course.enroll_students(lst)
    course_2.enroll_students(lst_2)
    q = CheckboxQuestion(1, "choose", [1, 2, 3])
    a1 = Answer([1])
    a2 = Answer([5])
    student_1.set_answer(q, a1)
    student_2.set_answer(q, a2)
    s = Survey([q])
    assert course.all_answered(s) is False
    assert course_2.all_answered(s) is True


def test_multiple_choice_question_string() -> None:
    q = MultipleChoiceQuestion(1, "how old are you", ['10', '11'])
    assert str(q) == 'how old are you\n10\n11'


def test_multiple_choice_question_validate_answer() -> None:
    q = MultipleChoiceQuestion(1, "how old are you", [10, 11])
    a = Answer(15)
    a2 = Answer("hello")
    a3 = Answer(10)
    assert q.validate_answer(a) is False
    assert q.validate_answer(a2) is False
    assert q.validate_answer(a3) is True


def test_multiple_choice_question_get_similarity() -> None:
    q = MultipleChoiceQuestion(1, "how old are you", [10, 11])
    a1 = Answer("hello")
    a2 = Answer("hel")
    a3 = Answer("hello")
    assert q.get_similarity(a1, a2) == 0.0
    assert q.get_similarity(a1, a3) == 1.0


def test_str_numeric_question() -> None:
    q = NumericQuestion(1, 'choose!', 1, 1000)
    assert str(q) == 'choose! (1, 1000)'


def test_numeric_question_validate_answer() -> None:
    q = NumericQuestion(1, 'choose!', 1, 1000)
    a = Answer(15)
    a2 = Answer("a")
    a3 = Answer(1000)
    a4 = Answer(1001)
    a5 = Answer(True)
    assert q.validate_answer(a) is True
    assert q.validate_answer(a2) is False
    assert q.validate_answer(a3) is True
    assert q.validate_answer(a4) is False
    assert q.validate_answer(a5) is False


def test_numeric_question_get_similarity() -> None:
    q = NumericQuestion(1, 'choose!', 0, 10)
    a1 = Answer(5)
    a2 = Answer(6)
    assert q.get_similarity(a1, a2) == 0.9


def test_yesno_question_string() -> None:
    q = YesNoQuestion(1, 'choose!')
    assert str(q) == 'choose! (Yes or No)'


def test_yesno_question_validate_answer() -> None:
    q = YesNoQuestion(1, 'choose!')
    a1 = Answer(False)
    a2 = Answer(1)
    assert q.validate_answer(a1) is True
    assert q.validate_answer(a2) is False


def test_yesno_question_get_similarity() -> None:
    q = YesNoQuestion(1, 'choose')
    a1 = Answer(True)
    a2 = Answer(False)
    assert q.get_similarity(a1, a2) == 0.0


def test_checkbox_question_validate_answer() -> None:
    q = CheckboxQuestion(1, "choose", ['a', 'b', 'c'])
    a1 = Answer([])
    a2 = Answer(['a', 'c'])
    a3 = Answer(['a', 'a'])
    a4 = Answer(True)
    assert q.validate_answer(a1) is False
    assert q.validate_answer(a2) is True
    assert q.validate_answer(a3) is False
    assert q.validate_answer(a4) is False


def test_checkbox_question_get_similarity() -> None:
    q = CheckboxQuestion(1, "choose", ['a', 'b', 'c'])
    a2 = Answer(['a', 'b', 'd'])
    a3 = Answer(['a', 'b', 'c'])
    assert q.get_similarity(a2, a3) == 0.5


def test_answer_is_valid() -> None:
    a_multiple = Answer("a")
    a_checkbox = Answer(["a", "b"])
    a_yesno = Answer(True)
    a_yesno_2 = Answer(1)
    a_numeric = Answer(15)

    assert a_multiple.is_valid(MultipleChoiceQuestion(1, "choose", ["a", "b"]))\
           is True
    assert a_multiple.is_valid(MultipleChoiceQuestion(1, "choose", ["c", "b"])) \
           is False
    assert a_checkbox.is_valid(CheckboxQuestion(2, "choose", ["a", "b"])) is \
           True
    assert a_checkbox.is_valid(CheckboxQuestion(2, "choose", ["a", "a"])) is \
           False
    assert a_yesno.is_valid(YesNoQuestion(1, "choose")) is True
    assert a_yesno_2.is_valid(YesNoQuestion(1, "choose")) is False
    assert a_numeric.is_valid(NumericQuestion(1, "5+10", 1, 20)) is True
    assert a_numeric.is_valid(NumericQuestion(1, "5+10", 18, 20)) is False


def test_homogeneous_criterion() -> None:
    q = CheckboxQuestion(1, "choose", [1, 2, 3, 4])
    a1 = Answer([1, 2, 3, 4])
    a2 = Answer([1, 2])
    a3 = Answer(["hello"])
    c = HomogeneousCriterion()
    assert c.score_answers(q, [a1, a2]) == 0.5
    # assert c.score_answers(q, [a3]) is InvalidAnswerError
    assert c.score_answers(q, [a1]) == 1.0


def test_heterogeneous_criterion() -> None:
    q = CheckboxQuestion(1, "choose", [1, 2, 3, 4])
    a1 = Answer([1, 2, 3, 4])
    a2 = Answer([1])
    a3 = Answer(["hello"])
    c = HeterogeneousCriterion()
    assert c.score_answers(q, [a1, a2]) == 0.75
    # assert c.score_answers(q, [a3]) is InvalidAnswerError
    assert c.score_answers(q, [a1]) == 0.0


def test_lonely_member_criterion() -> None:
    q = CheckboxQuestion(1, "choose", [1, 2, 3, 4])
    q2 = YesNoQuestion(2, "choose")
    a1 = Answer([1, 2, 3, 4])
    a2 = Answer([1])
    a3 = Answer([1])
    a4 = Answer(True)
    a5 = Answer(False)
    a6 = Answer(True)
    a7 = Answer(False)
    c = LonelyMemberCriterion()
    assert c.score_answers(q, [a1, a2]) == 0.0
    assert c.score_answers(q, [a2, a3]) == 1.0
    assert c.score_answers(q2, [a4, a5, a6, a7]) == 1.0


def test_survey_len() -> None:
    q1 = CheckboxQuestion(1, "choose", [1, 2, 3, 4])
    q2 = CheckboxQuestion(2, "choose", [1, 2, 3, 4])
    q3 = CheckboxQuestion(3, "choose", [1, 2, 3, 4])
    q_list = [q1, q2, q3]
    s = Survey(q_list)
    assert len(s) == 3


def test_survey_contains() -> None:
    q1 = CheckboxQuestion(1, "choose", [1, 2, 3, 4])
    q2 = CheckboxQuestion(2, "choose", [1, 2, 3, 4])
    q3 = CheckboxQuestion(3, "choose", [1, 2, 3, 4])
    q4 = 5
    q_list = [q1, q2]
    s = Survey(q_list)
    assert q1 in s
    assert q3 not in s
    assert q4 not in s


def test_survey_str() -> None:
    q1 = CheckboxQuestion(1, "choose", [1, 2, 3, 4])
    q_list = [q1]
    s = Survey(q_list)
    assert str(s) == "question id: 1\ntext:\nchoose\n1\n2\n3\n4\n"


def test_survey_get_questions() -> None:
    q1 = CheckboxQuestion(1, "choose", [1, 2, 3, 4])
    q2 = CheckboxQuestion(2, "choose", [1, 2, 3, 4])
    q3 = CheckboxQuestion(3, "choose", [1, 2, 3, 4])
    q_list = [q1, q2, q3]
    s = Survey(q_list)
    assert s.get_questions() == [q1, q2, q3]


def test_survey_get_criterion() -> None:
    q1 = CheckboxQuestion(1, "choose", [1, 2, 3, 4])
    q2 = CheckboxQuestion(2, "choose", [1, 2, 3, 4])
    q3 = CheckboxQuestion(3, "choose", [1, 2, 3, 4])
    q_list = [q1, q2, q3]
    s = Survey(q_list)
    assert isinstance(s._get_criterion(q1), HomogeneousCriterion)


def test_survey_get_weight() -> None:
    q1 = CheckboxQuestion(1, "choose", [1, 2, 3, 4])
    q2 = CheckboxQuestion(2, "choose", [1, 2, 3, 4])
    q3 = CheckboxQuestion(3, "choose", [1, 2, 3, 4])
    q_list = [q1, q2, q3]
    s = Survey(q_list)
    assert s._get_weight(q1) == 1


def test_survey_set_weight() -> None:
    q1 = CheckboxQuestion(1, "choose", [1, 2, 3, 4])
    q2 = CheckboxQuestion(2, "choose", [1, 2, 3, 4])
    q3 = CheckboxQuestion(3, "choose", [1, 2, 3, 4])
    q_list = [q1, q2, q3]
    s = Survey(q_list)
    assert s.set_weight(3, q1)
    assert s._get_weight(q1) == 3


def test_survey_set_weight() -> None:
    q1 = CheckboxQuestion(1, "choose", [1, 2, 3, 4])
    q2 = CheckboxQuestion(2, "choose", [1, 2, 3, 4])
    q3 = CheckboxQuestion(3, "choose", [1, 2, 3, 4])
    q_list = [q1, q2, q3]
    s = Survey(q_list)
    assert s.set_weight(3, q1)
    assert s._get_weight(q1) == 3


if __name__ == '__main__':
    import pytest
    pytest.main(['tests.py'])
