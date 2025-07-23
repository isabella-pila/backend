from typing import List, Optional

class Recipe:
    def __init__(
        self,
        id: str,
        title: str,
        ingredients: str,
        instructions: str,
        is_public: bool = True,
    
    ):
        self.id = id
        self.title = title
        self.ingredients = ingredients
        self.instructions = instructions
        self.is_public = is_public

