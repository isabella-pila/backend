import bcrypt # Você precisará instalar `pip install bcrypt`
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing import Self

class PasswordValidationError(Exception):
    pass

class Password:
    def __init__(self, value: str, hashed: bool = False):
        if not hashed:
            if not self._is_valid(value):
                raise ValueError("Password must be at least 8 characters and contain letters and numbers.")
            self._value = self._hash_password(value) # Armazenar o hash
        else:
            self._value = value # Já é um hash

    def _is_valid(self, password: str) -> bool:
        # Estas validações são para a senha em TEXTO CLARO antes de hash
        return len(password) >= 8 and any(c.isalpha() for c in password) and any(c.isdigit() for c in password)

    def _hash_password(self, password: str) -> str:
        # Hashear a senha
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_bytes.decode('utf-8')

    def verify(self, plain_password: str) -> bool:
        # Verificar uma senha em texto claro contra o hash armazenado
        return bcrypt.checkpw(plain_password.encode('utf-8'), self._value.encode('utf-8'))

    def hashed_value(self) -> str:
        # Método para obter o valor hash para armazenamento
        return self._value

    def __eq__(self, other) -> bool:
        # Comparar senhas (talvez com outro objeto Password ou string hash)
        if isinstance(other, Password):
            return self._value == other._value
        # Se você precisar comparar com um string hash diretamente
        if isinstance(other, str) and other.startswith("$2b$"): # Verifica se é um hash bcrypt
            return self._value == other
        return NotImplemented

    # Remova ou mude o __str__ se ele estiver sendo usado para serialização
    # Se for apenas para debug, pode manter (mas cuidado onde é printado)
    def __str__(self) -> str:
        return "<HASHED_PASSWORD>" # NUNCA mostre o hash aqui em produção, apenas para debug

    def __hash__(self) -> int:
        return hash(self._value)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type, handler: GetCoreSchemaHandler) -> CoreSchema:
        def validate_from_str(value: str) -> Self:
            # Pydantic passa a string de entrada, validamos e criamos Password
            return cls(value, hashed=False) # Garante que a validação e o hash ocorram

        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(cls),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(validate_from_str)
                ])
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.hashed_value(), # Serializa o hash para o Pydantic
            )
        )