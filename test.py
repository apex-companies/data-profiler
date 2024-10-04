from datetime import datetime



date = '2024-10-02'
date1 = '10022024'
date2 = '10/02/2024'
date3 = '2024-15-45'

datebad = 'iofjwe'



def check_date(val: str):
    print("The original string is : " + str(val))

    # checking if format matches the date 
    res = True
    fmt = '%Y-%m-%d'

    # using try-except to check for truth value
    try:
        datetime.strptime(val, fmt)
    except ValueError:
        return False
    return True

    # print("Does date match format? : " + str(res))


print(check_date(date))
print(check_date(date1))
print(check_date(date2))
print(check_date(date3))
