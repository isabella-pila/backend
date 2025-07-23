import pytest
from petfit.domain.entities.user import User
from petfit.domain.entities.recipe import Recipe
#from petfit.domain.entities.comment import Comment
from petfit.domain.value_objects.email_vo import Email
from petfit.domain.value_objects.password import Password


def test_create_user():
    email = Email("user@example.com")
    pwd = Password("Secret@123")
    user = User("1", "User", email, pwd)
    assert user.id == "1"


def test_create_user2():
    email = Email("user@example.com")
    pwd = Password("Secret@123")
    user = User("1", "User", email, pwd)
    assert user.email == "user@example.com"


def test_invalid_email():
    with pytest.raises(ValueError):
        User("1", "User", Email("usercom"), Password("Secret@123"))


def test_create_recipe():
    recipe = Recipe("1", "Title", "Ovo, leite, açúcar", "Misture tudo e ponha no forno", "true")
    assert recipe.title == "Title"

# Adicione estes testes ao seu arquivo tests/domain/test_entities.py

def test_create_recipe_and_verify_all_attributes():
    """
    Testa a criação de uma receita e verifica TODOS os seus atributos.
    """
    recipe = Recipe(
        id="recipe-01",
        title="Bolo de Chocolate",
        ingredients="Farinha, ovos, chocolate",
        instructions="Misturar tudo e assar.",
        is_public=True
    )
    
    assert recipe.id == "recipe-01"
    assert recipe.title == "Bolo de Chocolate"
    assert recipe.ingredients == "Farinha, ovos, chocolate"
    assert recipe.instructions == "Misturar tudo e assar."
    assert recipe.is_public is True

def test_create_private_recipe():
    """
    Testa a criação de uma receita privada, cobrindo o caso onde 'is_public=False'.
    """
    recipe = Recipe(
        id="recipe-02",
        title="Receita Secreta",
        ingredients="Segredo",
        instructions="Segredo",
        is_public=False  # Testando o cenário não padrão
    )
    
    assert recipe.id == "recipe-02"
    assert recipe.title == "Receita Secreta"
    assert recipe.is_public is False

def test_user_creation_and_verify_all_attributes():
    """
    Testa a criação de um usuário e verifica todos os seus atributos.
    """
    email = Email("test@user.com")
    password = Password("ValidPass@123")
    user = User(
        id="user-01",
        name="Test User",
        email=email,
        password=password
    )

    assert user.id == "user-01"
    assert user.name == "Test User"
    
    # --- CORREÇÃO AQUI ---
    # Remova o .value e compare o objeto diretamente.
    assert user.email == "test@user.com"
    
    # Verificamos se o objeto Password foi atribuído corretamente.
    assert user.password is password