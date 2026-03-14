def test_home_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid (200 OK)
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"Inicio" in response.data or b"EDF" in response.data

def test_register_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is requested (GET)
    THEN check that the response is valid (200 OK)
    """
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Register" in response.data or b"Registrarse" in response.data

def test_login_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check that the response is valid (200 OK)
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data or b"Iniciar" in response.data
