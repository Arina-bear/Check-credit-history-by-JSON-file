# Check-credit-history-by-JSON-file
This repository stores methods for processing borrowers' data to approve/deny their loan applications.

In the first try block, the correctness of reading the input data from the json_input file is checked.
The check occurs in the following code block:
if json_input.strip().startswith('{') or json_input.strip().startswith('['):

                try:
                    data = json.loads(json_input)
                except json.JSONDecodeError as e:
                    print(f"Error in JSON string: {e}")
print(f"Problem in string {e.lineno}, position {e.pos}")
return False         


The program switches to the try-except construction if the JSON starts with ‘{’ and the array in it starts with ‘[’. Spaces in the first line are also deleted (if any). The data is parsed into the Python dictionary in the try block. If the parsing attempt ends with an exception, it is processed in except by outputting an error message and returning False by the check_client() function.

In the next part of the code, the presence of fields used in the specified mandatory checks of client data is monitored (see paragraphs 2-4)
required_fields = [
            'birthDate',
            'passport', #those are the required fields
            'passport.issuedAt',
            'creditHistory'
        ]
        
      for field in required_fields:
            keys = field.split('.') #splitting nested fields 
            value = data
            for key in keys:
                if not isinstance(value, dict) or key not in value:
        print(f"Required field is missing: {field}")
return False
         value = value[key]

         if field != 'creditHistory' and value[key] is None:
           print(f"The {field} field cannot be null")
            return False

The isinstance(value, dict) function verifies that value is a dictionary and can be accessed by a key. The check_client() function returns False in the case when value is not a dictionary or the key key does not belong to the value dictionary, and an error message is printed. After verifying the existence of the key, the required fields (all except credit history) are checked for zero.

Verification of the borrower's achievement of 20 years is carried out using a fairly simple algorithm (the entire algorithm is immersed in the try block)
1. Importing the borrower's date of birth

  birth_d = datetime.strptime(data['birthDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
2. Calculating the current date
  today = datetime.now()
3. Calculating the age based on leap years
  age = (today - birth_d).days / 365.25
4. Fixing the results in flags
 flagCheck1 = age >= 20 #if True, age check is passed, #False- failed
      #flagCheck45year is used in checking the compliance of the date of issue of #passport
 flagCheck45year = age >= 45

The program switches to the branch except if the borrower's date of birth has not been read:
except ValueError as e:
            print(f"Invalid date of birth format: {e}")
return False

### Matching the date of issue of the passport with the actual age 

The specified compliance check is based on an analysis of the flag value flagCheck45year. A value of True means that the borrower is over 45 and the 45th birthday is calculated, a value of False means the age of the borrower is from 20 to 45 and the day they reach the age of 20 is determined, and then these dates are compared with the date of issue of the passport. The result of the comparison is described by the values of the flagCheck2 flag. If the value is true, the date of issue of the passport is correct and the verification according to this criterion has been passed, otherwise there are inconsistencies and the verification is considered failed. This algorithm is described in the try block, except for the processing of incorrect reading of the passport issue date. If the date is read incorrectly, an error message is displayed, and the check_client() function returns False.
try:
   passp_iss = datetime.strptime(data['passport']['issuedAt'], '%Y-%m-%dT%H:%M:%S.%fZ ') #import of passport issue date
            
    if flagCheck45year:
         threshold_date = birth_d + relativedelta(years=45) #calculating the 45th birthday.
     else:
        threshold_date = birth_d + relativedelta(years=20) #calculating the 20th birthday.
   flagCheck2 = passp_iss > threshold_date
  except ValueError as e:
            print(f"Incorrect format of passport issue date: {e}")
            return False

### Checking your credit history

    There may be several loans in the credit history, so it is necessary to organize a cycle that will go through all the entries in the 'creditHistory'. For the analysis, we will introduce variables that characterize the amount of debt owed for credit histories of the Credit Card type and others.

non_card_violations = 0#the number of non-credit card debts
card_violations = 0#number of credit card arrears
long_overdue_credits = 0#number of loans with a debt of more than 15 days

for credit in credit_history:
    credit_type = credit.get('type', ") #determining the type of loan
    overdue_days = credit.get('numberOfDaysOnOverdue', 0) #number of days overdue
    current_debt = credit.get('currentOverdueDebt', 0) #current overdue debt


Next, there is a division into checking credit card debts and other types of loans.:
if credit_type != 'Credit card':
  if current_debt > 0: #overdue debt
      non_card_violations += 1
         if overdue_days > 60:
non_card_violations += 1 #outstanding for more than 60 days
#Checking for credit cards
else:
  if current_debt > 0: : #overdue debt
      card_violations += 1
      if overdue_days > 30:
      card_violations += 1 arrears of more than 30 days    
#Counting current loans with a delay of >15 days
is_active = (date_end_of_credit is None or datetime.strptime(date_end_of_credit, '%Y-%m-%dT%H:%M:%S.%fZ') > today)
if is_active and overdue_days > 15:
  long_overdue_credits += 1

In this block of code, the loan status (is_active) is initially determined, then the condition "Loan repayment date > current date and there are 15 days of debt" is checked. Such comparisons are correct when importing a module.
 from dateutil.relativedelta import relativedelta
 If the condition is met, the number of specified credits increases by 1.

If at least one condition in any of the checks (except checking the correctness of reading from JSON) is not met, the check_client() function
returns False. This procedure is shown in the following part of the code:

if (non_card_violations > 0 or card_violations > 0 or long_overdue_credits > 2 or not flagCheck1 or not flagCheck2):
    return False                
return True
            
Completing the body of our function, we will describe the handling of exceptions related to credit history analysis and other unexpected errors.:
        except Exception as e:
print(f"Error in credit history analysis: {e}")
return False

except Exception as e:
  print(f"Unexpected error: {type(e).__name__}: {e}")
  return False


Before calling the check_client() function, you must open the client.JSON file in read mode and read the entire contents of the file into the json_string string.
with open("client.JSON", "r", encoding="utf-8") as file:
    json_string = file.read()
result = check_client(json_string)
print("Check result:", result)
