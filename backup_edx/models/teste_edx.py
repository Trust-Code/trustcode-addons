import requests

url_registro = 'http://54.164.167.243/register'

s = requests.Session()

response = s.get(url_registro)
token = response.cookies['csrftoken']

payload = {
    'csrfmiddlewaretoken': token,
    'email': 'teste@trustcode.com.br',
    'name': 'Trustcode Teste',
    'username': 'trustcodeTeste',
    'password': 'asd9@#&',
    'level_of_education': 'none',
    'gender': 'o',
    'year_of_birth': '1998',
    'mailing_address': 'teste@trustcode.com.br',
    'goals': 'Insert something here',
    'terms_of_service': 'true',
    'honor_code': 'true'
}

url_create = 'http://54.164.167.243/create_account'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-CSRFToken': token, 'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://54.164.167.243/register',
    }

r = s.post(url_create, data=payload, headers=headers)

print(r.text)
