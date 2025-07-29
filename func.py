import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
def check_client(json_input):
    try: 
        if json_input.strip().startswith('{') or json_input.strip().startswith('['):
                # Это JSON-строка
                try:
                    data = json.loads(json_input)
                except json.JSONDecodeError as e:
                    print(f"Ошибка в JSON-строке: {e}")
                    print(f"Проблема в строке {e.lineno}, позиция {e.pos}")
                    return False         
        # 2. Проверка обязательных полей
        required_fields = [
            'birthDate',
            'passport',
            'passport.issuedAt',
            'creditHistory'
        ]
        
        for field in required_fields:
            keys = field.split('.')
            value = data
            for key in keys:
                if not isinstance(value, dict) or key not in value:
                    print(f"Отсутствует обязательное поле: {field}")
                    return False
                if field != 'creditHistory' and value[key] is None:
                  print(f"Поле {field} не может быть null")
                  return False
                value = value[key]
        # 3. Проверка 1 (Возраст)
        try:
            birth_d = datetime.strptime(data['birthDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
            today = datetime.now()
            age = (today - birth_d).days / 365.25  # Точный расчет с учетом високосных лет
            
            flagCheck1 = age >= 20
            #flagCheck45year используется в проверке №2
            flagCheck45year = age >= 45
            
        except ValueError as e:
            print(f"Неверный формат даты рождения: {e}")
            return False

        # 4. Проверка 2 (Паспорт)
        try:
            passp_iss = datetime.strptime(data['passport']['issuedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
            
            if flagCheck45year:
                threshold_date = birth_d + relativedelta(years=45)
            else:
                threshold_date = birth_d + relativedelta(years=20)
                
            flagCheck2 = passp_iss > threshold_date
            
        except ValueError as e:
            print(f"Неверный формат даты выдачи паспорта: {e}")
            return False

        # 5. Проверка 3 (Кредитная история)
        try:
            credit_history = data['creditHistory']
            #переменные для контроля
            non_card_violations = 0#задолженность не для кредитной карты
            card_violations = 0#задолженность для кредитной карты
            long_overdue_credits = 0#переменная,для подсчета текущих кредитов с просроченностью более 15 дней
            
            for credit in credit_history:
                credit_type = credit.get('type', '')
                overdue_days = credit.get('numberOfDaysOnOverdue', 0)
                current_debt = credit.get('currentOverdueDebt', 0)
                date_end_of_credit = credit.get('repaidAt')
                
                # Проверка для не кредитных карт
                if credit_type != 'Кредитная карта':
                    if current_debt > 0:
                        non_card_violations += 1
                    if overdue_days > 60:
                        non_card_violations += 1
                # Проверка для кредитных карт
                else:
                    if current_debt > 0:
                        card_violations += 1
                    if overdue_days > 30:
                        card_violations += 1
                # Подсчет  текущих кредитов с просрочкой >15 дней
                is_active = (date_end_of_credit is None or
                    datetime.strptime(date_end_of_credit, '%Y-%m-%dT%H:%M:%S.%fZ') > today)
                if is_active and overdue_days > 15:
                 long_overdue_credits += 1
            # Итоговая проверка всех условий
            if (non_card_violations > 0 or 
                card_violations > 0 or 
                long_overdue_credits > 2 or 
                not flagCheck1 or 
                not flagCheck2):
                return False
                
            return True
            
        except Exception as e:
            print(f"Ошибка при анализе кредитной истории: {e}")
            return False

    except Exception as e:
        print(f"Неожиданная ошибка: {type(e).__name__}: {e}")
        return False


with open("client.JSON", "r", encoding="utf-8") as file:
    json_string = file.read()
result = check_client(json_string)
print("Результат проверки:", result)