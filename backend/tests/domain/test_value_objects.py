import pytest
from petfit.domain.value_objects.email_vo import Email
from petfit.domain.value_objects.password import Password, PasswordValidationError
import bcrypt
from pydantic import BaseModel, ValidationError


def test_valid_email():
    email = Email("user@example.com")
    assert email.value() == "user@example.com"


def test_invalid_email():
    with pytest.raises(ValueError):
        Email("invalid-email")

# Testes para a validação da senha (método _is_valid)
def test_password_valid_creation():
    """Deve criar uma instância de Password com uma senha válida."""
    password = Password("SenhaSegura123")
    assert isinstance(password, Password)
    assert password.hashed_value() is not None
    assert password.hashed_value() != "SenhaSegura123" # Deve ser hasheada

def test_password_invalid_short():
    """Deve levantar ValueError para senha muito curta."""
    with pytest.raises(ValueError, match="Password must be at least 8 characters and contain letters and numbers."):
        Password("Curta1")

def test_password_invalid_no_alpha():
    """Deve levantar ValueError para senha sem letras."""
    with pytest.raises(ValueError, match="Password must be at least 8 characters and contain letters and numbers."):
        Password("123456789")

def test_password_invalid_no_digit():
    """Deve levantar ValueError para senha sem números."""
    with pytest.raises(ValueError, match="Password must be at least 8 characters and contain letters and numbers."):
        Password("abcdefgh")

def test_password_invalid_mixed_short():
    """Deve levantar ValueError para senha mista mas muito curta."""
    with pytest.raises(ValueError, match="Password must be at least 8 characters and contain letters and numbers."):
        Password("Ab1")

# Testes para o hashing e verificação
def test_password_hashing():
    """Deve hashear a senha corretamente e o hash deve ser diferente do texto claro."""
    plain_password = "MinhaSenhaSecreta123"
    password = Password(plain_password)
    hashed_value = password.hashed_value()
    assert hashed_value.startswith("$2b$") # Verifica o formato do hash bcrypt
    assert len(hashed_value) > 20 # Verifica um comprimento razoável
    assert bcrypt.checkpw(plain_password.encode('utf-8'), hashed_value.encode('utf-8'))

def test_password_verification_correct():
    """Deve verificar corretamente uma senha correta."""
    password = Password("OutraSenhaForte456")
    assert password.verify("OutraSenhaForte456") is True

def test_password_verification_incorrect():
    """Deve falhar na verificação com uma senha incorreta."""
    password = Password("OutraSenhaForte456")
    assert password.verify("SenhaErrada789") is False

def test_password_verification_different_hash_same_password():
    """Deve verificar corretamente se hashes diferentes da mesma senha funcionam."""
    # Bcrypt gera hashes diferentes para a mesma senha (devido ao salt)
    password1 = Password("SenhaUnica111")
    password2 = Password("SenhaUnica111")
    assert password1.hashed_value() != password2.hashed_value()
    assert password1.verify("SenhaUnica111") is True
    assert password2.verify("SenhaUnica111") is True

# Testes para o construtor com 'hashed=True'
def test_password_creation_with_prehashed():
    """Deve criar Password a partir de um hash existente."""
    original_password = "SenhaProntaParaHash789"
    hashed_from_bcrypt = bcrypt.hashpw(original_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    password_obj = Password(hashed_from_bcrypt, hashed=True)
    assert isinstance(password_obj, Password)
    assert password_obj.hashed_value() == hashed_from_bcrypt
    assert password_obj.verify(original_password) is True
    # Uma senha marcada como hashed=True não deve passar pela validação de texto claro
    # Tentar criar uma senha inválida com hashed=True (mas é um hash válido) não deve falhar
    short_hash = bcrypt.hashpw(b"short", bcrypt.gensalt()).decode('utf-8')
    pw_from_short_hash = Password(short_hash, hashed=True)
    assert pw_from_short_hash.hashed_value() == short_hash


# Testes para métodos especiais (__eq__, __str__, __hash__)
def test_password_equality_same_hash():
    """Objetos Password com o mesmo hash devem ser iguais."""
    password1 = Password("TesteIgualdade123")
    # Crie outro objeto Password com o mesmo hash para testar a igualdade
    password2 = Password(password1.hashed_value(), hashed=True)
    assert password1 == password2

def test_password_equality_different_hash():
    """Objetos Password com hashes diferentes não devem ser iguais."""
    password1 = Password("TesteIgualdade123")
    password2 = Password("OutroHash456")
    assert password1 != password2

def test_password_equality_with_hash_string():
    """Um objeto Password deve ser igual a sua string de hash."""
    password = Password("StringHashTest789")
    assert password == password.hashed_value()
    # Testar com uma string que parece um hash mas não é
    assert password != "nao_e_um_hash_valido"

def test_password_str_representation():
    """A representação em string deve ser a esperada."""
    password = Password("TesteStr111")
    assert str(password) == "<HASHED_PASSWORD>"

def test_password_hashable():
    """Objetos Password devem ser 'hashable' (usáveis em sets/dict keys)."""
    password1 = Password("HashableTest123")
    password2 = Password(password1.hashed_value(), hashed=True) # Mesmo hash
    password3 = Password("HashableTest456")

    s = {password1, password2, password3}
    assert len(s) == 2 # password1 e password2 devem ser considerados o mesmo

# Testes para integração Pydantic
class User(BaseModel):
    username: str
    password: Password

def test_pydantic_model_valid_password():
    """Pydantic deve validar e criar o objeto Password corretamente."""
    user_data = {"username": "testuser", "password": "SenhaPydanticSegura123"}
    user = User(**user_data)
    assert isinstance(user.password, Password)
    assert user.password.verify("SenhaPydanticSegura123") is True
    assert user.password.hashed_value() == bcrypt.hashpw("SenhaPydanticSegura123".encode('utf-8'), user.password.hashed_value().encode('utf-8')).decode('utf-8')


def test_pydantic_model_invalid_password():
    """Pydantic deve levantar ValidationError para senha inválida."""
    user_data_short = {"username": "testuser", "password": "Curta"}
    with pytest.raises(ValidationError):
        User(**user_data_short)

    user_data_no_alpha = {"username": "testuser", "password": "123456789"}
    with pytest.raises(ValidationError):
        User(**user_data_no_alpha)

def test_pydantic_model_serialization():
    """Pydantic deve serializar o objeto Password para seu valor hasheado."""
    user = User(username="serializeuser", password="SenhaParaSerializar123")
    
    # Ao exportar para um dicionário, esperamos o hash, não o objeto Password
    exported_data = user.model_dump() # ou user.dict() em Pydantic V1
    
    assert "password" in exported_data
    assert isinstance(exported_data["password"], str)
    assert exported_data["password"].startswith("$2b$")
    
    # Verificar que o hash exportado é o mesmo que o hash real da instância
    assert exported_data["password"] == user.password.hashed_value()