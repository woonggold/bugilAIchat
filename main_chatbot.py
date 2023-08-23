import sqlite3
import random
import pandas as pd
import re
from datetime import datetime

# SQLite 데이터베이스 연결 및 테이블 생성
conn = sqlite3.connect('knowledge_base.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                question TEXT UNIQUE)''')

c.execute('''CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY,
                question_id INTEGER,
                answer TEXT)''')

conn.commit()

# 초기 비밀번호 설정
admin_password = "인공지능주인님"

# 질문을 데이터베이스에 추가하고 질문 ID를 반환
def add_question(question):
    try:
        c.execute("INSERT INTO questions (question) VALUES (?)", (question,))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        c.execute("SELECT id FROM questions WHERE question=?", (question,))
        return c.fetchone()[0]

# 답변을 데이터베이스에 추가
def add_answer(question_id, answer):
    c.execute("INSERT INTO answers (question_id, answer) VALUES (?, ?)", (question_id, answer))
    conn.commit()

# 한 질문에 대한 랜덤한 답변을 반환
def get_random_answer(question):
    c.execute("SELECT id FROM questions WHERE question=?", (question,))
    question_id = c.fetchone()
    if question_id:
        c.execute("SELECT answer FROM answers WHERE question_id=?", (question_id[0],))
        results = c.fetchall()
        if results:
            return random.choice(results)[0]

    return "미안해요, 그 질문에 대한 답변을 알지 못해요."

# 모든 질문 목록을 반환
def get_question_list():
    c.execute("SELECT question FROM questions")
    results = c.fetchall()
    return [result[0] for result in results]

# 한 질문에 대한 모든 답변을 반환
def get_all_answers(question):
    c.execute("SELECT answer FROM answers WHERE question_id IN (SELECT id FROM questions WHERE question=?)", (question,))
    results = c.fetchall()
    if results:
        return [result[0] for result in results]
    else:
        return []

# 관리자 모드에서 질문과 답변 삭제
def admin_delete_question():
    question_list = get_question_list()
    if question_list:
        print("질문 목록:")
        for index, question in enumerate(question_list, 1):
            print(f"{index}. {question}")

        try:
            choice = int(input("삭제할 질문 번호를 입력하세요: ")) - 1
            selected_question = question_list[choice]
            responses = get_all_answers(selected_question)
            print(f"{selected_question}에 대한 답변 목록:")
            for index, response in enumerate(responses, 1):
                print(f"{index}. {response}")

            delete_choice = input("삭제할 답변 번호를 선택하세요 (0은 모두 삭제): ")
            if delete_choice == "0":
                c.execute("DELETE FROM answers WHERE question_id IN (SELECT id FROM questions WHERE question=?)",
                          (selected_question,))
            else:
                delete_choice = int(delete_choice) - 1
                selected_answer = responses[delete_choice]
                c.execute("DELETE FROM answers WHERE answer=?", (selected_answer,))

            conn.commit()
            print("삭제되었습니다.")
        except (ValueError, IndexError):
            print("올바른 번호를 입력해주세요.")
    else:
        print("아직 학습된 질문이 없어요.")

# 관리자 모드에서 비밀번호 변경
def admin_change_password():
    global admin_password
    new_password = input("새로운 비밀번호를 입력하세요: ")
    admin_password = new_password
    print("비밀번호가 변경되었습니다.")

# 관리자 비밀번호 확인
def check_admin_password():
    password = input("비밀번호를 입력하세요: ")
    return password == admin_password

# 사용자와 상호작용
while True:
    user_input = input("사용자: ")

    if user_input.lower() == "종료":
        break

    elif user_input.lower() == "학습":
        question = input("새로운 질문: ")
        answer = input("질문에 대한 답변: ")
        question_id = add_question(question)
        add_answer(question_id, answer)
        print("새로운 지식을 학습했어요.")

    elif user_input.lower().startswith("관리자:"):
        if check_admin_password():
            admin_command = user_input.lower().replace("관리자:", "")
            if admin_command == "리스트":
                question_list = get_question_list()
                if question_list:
                    print("질문 목록:")
                    for index, question in enumerate(question_list, 1):
                        print(f"{index}. {question}")

                    try:
                        choice = int(input("선택할 질문 번호를 입력하세요: ")) - 1
                        selected_question = question_list[choice]
                        responses = get_all_answers(selected_question)
                        print(f"{selected_question}에 대한 답변 목록:")
                        for index, response in enumerate(responses, 1):
                            print(f"{index}. {response}")
                    except (ValueError, IndexError):
                        print("올바른 번호를 입력해주세요.")
                else:
                    print("아직 학습된 질문이 없어요.")

            elif admin_command == "리스트삭제":
                admin_delete_question()

            elif admin_command == "비밀번호변경":
                admin_change_password()

            else:
                print("알 수 없는 관리자 명령입니다.")
        else:
            print("비밀번호가 올바르지 않아 관리자 모드에 접근할 수 없어요.")

    elif user_input.lower() == "내일급식":
        # Excel 파일 불러오기
        try:
            xls_data = pd.read_excel('급식식단정보.xls')
            today = datetime.today().strftime('%Y%m%d')
            user_date = today + 1

            # 날짜가 존재하는지 확인
            if str(user_date) in xls_data['급식일자'].astype(str).values.tolist():
                # 날짜에 해당하는 행 가져오기
                meal_row = xls_data[xls_data['급식일자'].astype(str) == str(user_date)]

                # 조식, 중식, 석식 각각의 정보 가져오기
                breakfast_info = meal_row[meal_row['식사명'] == '조식']['요리명'].values[0]
                lunch_info = meal_row[meal_row['식사명'] == '중식']['요리명'].values[0]
                dinner_info = meal_row[meal_row['식사명'] == '석식']['요리명'].values[0]

                # 괄호와 그 안의 내용 제거하고 ,로 변환
                breakfast_info = re.sub(r'\([^)]*\)', '', breakfast_info)
                breakfast_info = breakfast_info.replace('<br/>', ',').strip()
                lunch_info = re.sub(r'\([^)]*\)', '', lunch_info)
                lunch_info = lunch_info.replace('<br/>', ',').strip()
                dinner_info = re.sub(r'\([^)]*\)', '', dinner_info)
                dinner_info = dinner_info.replace('<br/>', ',').strip()

                print(f"{user_date}의 급식 메뉴:")
                print(f"조식: {breakfast_info}")
                print(f"중식: {lunch_info}")
                print(f"석식: {dinner_info}")

            else:
                print("입력한 날짜의 급식 정보를 찾을 수 없습니다.")


        except FileNotFoundError:
            print("급식식단정보.xls 파일을 찾을 수 없습니다.")
    elif user_input.lower() == "오늘급식":
        # Excel 파일 불러오기
        try:
            xls_data = pd.read_excel('급식식단정보.xls')
            today = datetime.today().strftime('%Y%m%d')
            user_date = today

            # 날짜가 존재하는지 확인
            if str(user_date) in xls_data['급식일자'].astype(str).values.tolist():
                # 날짜에 해당하는 행 가져오기
                meal_row = xls_data[xls_data['급식일자'].astype(str) == str(user_date)]

                # 조식, 중식, 석식 각각의 정보 가져오기
                breakfast_info = meal_row[meal_row['식사명'] == '조식']['요리명'].values[0]
                lunch_info = meal_row[meal_row['식사명'] == '중식']['요리명'].values[0]
                dinner_info = meal_row[meal_row['식사명'] == '석식']['요리명'].values[0]

                # 괄호와 그 안의 내용 제거하고 ,로 변환
                breakfast_info = re.sub(r'\([^)]*\)', '', breakfast_info)
                breakfast_info = breakfast_info.replace('<br/>', ',').strip()
                lunch_info = re.sub(r'\([^)]*\)', '', lunch_info)
                lunch_info = lunch_info.replace('<br/>', ',').strip()
                dinner_info = re.sub(r'\([^)]*\)', '', dinner_info)
                dinner_info = dinner_info.replace('<br/>', ',').strip()

                print(f"{user_date}의 급식 메뉴:")
                print(f"조식: {breakfast_info}")
                print(f"중식: {lunch_info}")
                print(f"석식: {dinner_info}")

            else:
                print("입력한 날짜의 급식 정보를 찾을 수 없습니다.")


        except FileNotFoundError:
            print("급식식단정보.xls 파일을 찾을 수 없습니다.")
    elif user_input.lower() == "급식":
        # Excel 파일 불러오기
        try:
            xls_data = pd.read_excel('급식식단정보.xls')
            # 사용자에게 날짜를 물어보고 입력 받기
            user_date = input("날짜를 입력하세요 (예: 20230101): ")
            
            if user_date.lower() == "오늘급식":
                today = datetime.today().strftime('%Y%m%d')
                user_date = today

            # 날짜가 존재하는지 확인
            if str(user_date) in xls_data['급식일자'].astype(str).values.tolist():
                # 날짜에 해당하는 행 가져오기
                meal_row = xls_data[xls_data['급식일자'].astype(str) == str(user_date)]

                # 조식, 중식, 석식 각각의 정보 가져오기
                breakfast_info = meal_row[meal_row['식사명'] == '조식']['요리명'].values[0]
                lunch_info = meal_row[meal_row['식사명'] == '중식']['요리명'].values[0]
                dinner_info = meal_row[meal_row['식사명'] == '석식']['요리명'].values[0]

                # 괄호와 그 안의 내용 제거하고 ,로 변환
                breakfast_info = re.sub(r'\([^)]*\)', '', breakfast_info)
                breakfast_info = breakfast_info.replace('<br/>', ',').strip()
                lunch_info = re.sub(r'\([^)]*\)', '', lunch_info)
                lunch_info = lunch_info.replace('<br/>', ',').strip()
                dinner_info = re.sub(r'\([^)]*\)', '', dinner_info)
                dinner_info = dinner_info.replace('<br/>', ',').strip()

                print(f"{user_date}의 급식 메뉴:")
                print(f"조식: {breakfast_info}")
                print(f"중식: {lunch_info}")
                print(f"석식: {dinner_info}")

            else:
                print("입력한 날짜의 급식 정보를 찾을 수 없습니다.")


        except FileNotFoundError:
            print("급식식단정보.xls 파일을 찾을 수 없습니다.")

    else:
        response = get_random_answer(user_input)
        print("챗봇:", response)

# 데이터베이스 연결 종료
conn.close()
