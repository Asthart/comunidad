# middleware.py
import threading
import requests
from django.contrib.auth import get_user_model
from django.http import HttpResponse

class BearerTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImF1dGgiOiJST0xFX0FETUlOLFJPTEVfQURNSU5FQ09TSVNURU1BLFJPTEVfR0VTVE9SIiwiZXhwIjoxNzI4NjU0NzMxfQ.sRlbRXjdDAxTg0I2bhZ2YHwetrc_DJB_alS_J0V4VYRFJIJgdm19oIrQCeKxyiTi5ddu96DSru_22otZGIxJVA"
        test = request.META.get('HTTP_JHI_AUTHENTICATIONTOKEN')
        if token:
            token = token.replace('Bearer ', '')
            #print(token)
            url = "https://innovacrece.uic.cu/api/account"
            headers = {
                'Authorization': f'Bearer {token}'
            }
            response = requests.get(url,headers=headers, verify=False)
            print(response.status_code)
            if response.status_code == 200:
                usuario_data = response.json()
                usuario, created = get_user_model().objects.get_or_create(username=usuario_data['login'], email=usuario_data['email'],first_name=usuario_data['firstName'],last_name=usuario_data['lastName'])
                if created:
                    print("creado")
                    pass
                request.user = usuario
            print("fin 2 if")
        print("fin 1 if")
        return self.get_response(request)