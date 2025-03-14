import requests  
  
url = "http://127.0.0.1:8000/api"  
# url = "http://simadancing.ru/api"  


data = {  
	"venue_name": "ДК Гагарина"  
}  
response = requests.post(url+'/venues/', json=data)  # Use json=data to send as JSON  
print(response.json())  # Get the response body as JSON  
  
  
  
  
for section in ["Балкон", "Амфитеатр", "Партер"]:  
    if section == "Балкон":  
        for row in range(1, 8):  
            for seat_num in range(1, 29):  
                data = {  
                    "section": section,  
                    "row": str(row),  
                    "number": str(seat_num),  
                    "venue_id": 1  
                }  
                response = requests.post(url + '/seats/', json=data)  # Use json=data to send as JSON  
                print(response.json())  # Get the response body as JSON  
    if section == "Амфитеатр":  
        for row in range(13, 19):  
            for seat_num in range(1, 29):  
                data = {  
                    "section": section,  
                    "row": str(row),  
                    "number": str(seat_num),  
                    "venue_id": 1  
                }  
                response = requests.post(url + '/seats/', json=data)  # Use json=data to send as JSON  
                print(response.json())  # Get the response body as JSON  
  
    if section == "Партер":  
        for row in range(1, 14):  
            for seat_num in range(1, 29):  
                data = {  
                    "section": section,  
                    "row": str(row),  
                    "number": str(seat_num),  
                    "venue_id": 1  
                }  
                response = requests.post(url + '/seats/', json=data)  # Use json=data to send as JSON  
                print(response.json())  # Get the response body as JSON