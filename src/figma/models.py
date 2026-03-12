from pydantic import BaseModel
from typing import Optional

class UIComponent(BaseModel):
    """
    Represents a single UI element extracted from a Figma frame.
    Examples: Button, Input, Card, Navigation bar, Table
    """
    id: str
    name: str
    type: str
    component_type: Optional[str]
    children_count: int = 0
    has_text: bool = False
    is_interactive: bool = False

class DesignScreen(BaseModel):
    """
    Represents a single screen or view extracted from Figma.
    Examples: Login Screen, Dashboard, Client List
    """
    id: str
    name: str
    page: str
    components: list[UIComponent] = []
    components_count: int = 0

class DesignContext(BaseModel):
    """
    The complete structured representation of a Figma file.
    This is what gets passed to the LLM — nothing else.
    """
    file_name: str
    total_screens: int
    pages: list[str]
    screens: list[DesignScreen]
    component_summary: dict[str, int]
    inferred_features: list[str]