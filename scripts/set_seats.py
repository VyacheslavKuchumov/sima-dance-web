import requests  
import itertools  
  
url = "http://127.0.0.1:8000/api/booking"  
# url = "http://simadancing.ru/api"  
# url = "http://192.168.50.223/api"
  
  
  
  
for section in ["Балкон", "Амфитеатр", "Партер"]:  
    if section == "Балкон":  
        for row in range(1, 7+1):
            if row in range(1, 2+1):  
                for seat_num in range(1, 28+1):  
                    data = {  
                        "section": section,  
                        "row": row,  
                        "number": seat_num
                    }  
                    response = requests.post(url + '/seats/', json=data)  # Use json=data to send as JSON  
                    print(response.json())  # Get the response body as JSON  
            if row in range(3, 6+1):
                for seat_num in range(1, 24+1):  
                    data = {  
                        "section": section,  
                        "row": row,  
                        "number": seat_num
                    }  
                    response = requests.post(url + '/seats/', json=data)
                    print(response.json())
            if row == 7:
                for seat_num in range(1, 26+1):  
                    data = {  
                        "section": section,  
                        "row": row,  
                        "number": seat_num
                    }  
                    response = requests.post(url + '/seats/', json=data)
                    print(response.json())
    
    ################
    
    
    if section == "Амфитеатр":  
        for row in range(13, 18+1):
            if row == 13:
                for seat_num in itertools.chain(range(2, 11+1), range(16, 26+1)):  
                    data = {  
                        "section": section,  
                        "row": row,
                        "number": seat_num
                    }  
                    response = requests.post(url + '/seats/', json=data)
                    print(response.json())
            if row in range(14, 17+1):
                for seat_num in range(1, 26+1):  
                    data = {  
                        "section": section,  
                        "row": row,
                        "number": seat_num
                    }  
                    response = requests.post(url + '/seats/', json=data)
                    print(response.json())
            if row == 18:
                for seat_num in range(1, 31+1):  
                    data = {  
                        "section": section,  
                        "row": row,  
                        "number": seat_num
                    }  
                    response = requests.post(url + '/seats/', json=data)
                    print(response.json())    
            
    
    #############
    
    
    if section == "Партер":  
        for row in range(1, 12+1):
            if row == 1:
                for seat_num in range(1, 16+1):  
                    data = {  
                        "section": section,  
                        "row": row,  
                        "number": seat_num
                    }  
                    response = requests.post(url + '/seats/', json=data)
                    print(response.json())
            if row == 2:
                for seat_num in range(1, 18+1):  
                    data = {  
                        "section": section,  
                        "row": row,  
                        "number": seat_num
                    }  
                    response = requests.post(url + '/seats/', json=data)
                    print(response.json())        
            if row == 3:
                for seat_num in range(1, 20+1):  
                    data = {  
                        "section": section,  
                        "row": row,  
                        "number": seat_num
                    }  
                    response = requests.post(url + '/seats/', json=data)
                    print(response.json())
            if row in range(4, 5+1):
                for seat_num in range(1, 22+1):  
                    data = {  
                        "section": section,  
                        "row": row,  
                        "number": seat_num
                    }  
                    response = requests.post(url + '/seats/', json=data)
                    print(response.json())
            if row in range(6, 12+1):
                for seat_num in range(1, 24+1):  
                    data = {  
                        "section": section,  
                        "row": row,  
                        "number": seat_num
                    }
                    response = requests.post(url + '/seats/', json=data)
                    print(response.json())
                   
           