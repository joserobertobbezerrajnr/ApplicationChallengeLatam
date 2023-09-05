import requests

# URL de destino
url = 'https://advana-challenge-check-api-cr-k4hdbggvoq-uc.a.run.app/software-engineer'

# Dados que você deseja enviar no corpo da solicitação POST (exemplo)
data = {
    "name": "Jose Bezerra",
    "mail": "joserobertobarbosabezeerra@gmail.com",
    "github_url": "https://github.com/joserobertobbezerrajnr/ApplicationChallengeLatam.git",
    "api_url": "https://jose-bezera.api"
}

# Faz a solicitação POST
response = requests.post(url, json=data)

# Verifica a resposta
if response.status_code == 200:
    print("Solicitação POST bem-sucedida!")
    print("Resposta do servidor:", response.text)
else:
    print("Erro na solicitação POST. Código de status:", response.status_code)
    print("Resposta do servidor:", response.text)