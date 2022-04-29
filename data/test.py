from requests import get, post, delete

print(get('http://localhost:5000/api/enemy').json())
print(get('http://localhost:5000/api/enemy/111').json())
print(get('http://localhost:5000/api/enemy/a').json())
print(post('http://localhost:5000/api/enemy').json())

print(post('http://localhost:5000/api/enemy',
           json={'title': 'Заголовок'}).json())

print(post('http://localhost:5000/api/enemy',
           json={'name': 'Имя',
                 'location': 'Локация',
                 'min_level': 1}).json())

print(delete('http://localhost:5000/api/enemy/999').json())
# новости с id = 999 нет в базе

print(delete('http://localhost:5000/api/enemy/1').json())