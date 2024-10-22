from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mangum import Mangum

# FastAPI app
app = FastAPI()

# Adaptación para lambda
handler = Mangum(app)

# Mocked temp vars
mocked_description = "Hola! Mi nombre es Carlos Fontela, soy un desarrollador de software amante de las metodologías ágiles."
mocked_fav_book_description = "Me gustó mucho, coincido con varios de los aspectos nombrados por el autor. Java es un lenguaje de programación de propósito general, concurrente, orientado a objetos que fue diseñado específicamente para tener tan pocas dependencias de implementación como fuera posible. UML es un lenguaje de modelado gráfico que se utiliza para especificar, visualizar, construir y documentar un sistema de software."

@app.get("/users/{username}")
def get_user_profile(username: str):
    
    mocked_user = {
        'name': 'Carlos Fontela',
        'username': 'carlosfontela',
        'profilePicture': '[url]',
        'description': mocked_description,
        'favouriteBook': {
            'title': 'Java y UML',
            'cover': '[url]',
            'description': mocked_fav_book_description
        },
        'groups': [
            {
                'name': 'Agile beasts',
                'members': 14
            },
            {
                'name': 'FIUBA',
                'members': 518
            },
            {
                'name': 'Borges Lovers',
                'members': 1234
            },
        ]
    }
    
    return mocked_user