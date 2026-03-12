from src.figma.models import UIComponent, DesignScreen, DesignContext

# Pages we should ignore
IGNORE_PAGES = {
    "rubbish", "components", "do not use", "archive", "old", "ignore", "temp"
}

# Figma node types we care about
MEANINGFUL_TYPES = {
    "FRAME", "INSTANCE", "GROUP", "COMPONENT", "RECTANGLE", "VECTOR", "TEXT"
}

# Keywords that suggest a component is interactive
INTERACTIVE_KEYWORDS = {
    "button", "btn", "click", "tap", "link", 
    "input", "field", "search", "toggle", 
    "checkbox", "radio", "select", "dropdown",
    "menu", "nav", "tab"
}

# Keywords that help us infer component type
COMPONENT_TYPE_MAP = {
    "button": ["button", "btn", "cta", "submit", "action"],
    "input": ["input", "field", "search", "email", "password", "text"],
    "navigation": ["nav", "navbar", "menu", "sidebar", "header", "footer"],
    "table": ["table", "list", "grid", "row", "cell"],
    "card": ["card", "tile", "item", "panel"],
    "modal": ["modal", "dialog", "popup", "overlay"],
    "form": ["form", "login", "register", "signup", "signin"],
}

class FigmaParser:
    """
    Transforms raw Figma JSON into a clean DesignContext.
    
    This is the noise-reduction layer. Everything that enters 
    here is raw Figma data. Everything that leaves is clean, 
    structured context ready for the LLM.
    """

    def parse(self, raw_figma_data: dict) -> DesignContext:
        """
        Main entry point. Takes raw Figma API response,
        returns a clean DesignContext.
        """
        file_name = raw_figma_data.get('name', 'Unknown')
        document = raw_figma_data.get('document', {})
        pages = document.get('children', [])

        all_screens = []
        valid_page_names = []
        component_summary: dict[str, int] = {}

        for page in pages:
            page_name = page.get("name", "")

            # Skip noise pages
            if self._should_ignore_page(page_name):
                continue

            valid_page_names.append(page_name)
            frames = page.get("children", [])
            
            for frame in frames:
                # Parse each top-level frame into a DesignScreen
                screen = self._parse_screen(frame, page_name)
                if screen:
                    all_screens.append(screen)
                    # Accumulate component counts
                    for comp_type, count in self._count_components(screen):
                        component_summary[comp_type] = (
                            component_summary.get(comp_type, 0) + count
                        )

        inferred_features = self._infer_features(
            valid_page_names, all_screens
        )

        return DesignContext(
            file_name=file_name,
            total_screens=len(all_screens),
            pages=valid_page_names,
            screens=all_screens,
            component_summary=component_summary,
            inferred_features=inferred_features
        )

    def _should_ignore_page(self, page_name: str) -> bool:
        """
        Returns True if this page should be skipped.
        Checks against known noise page names.
        """
        normalised = page_name.lower().strip()
        for ignore_term in IGNORE_PAGES:
            if ignore_term in normalised:
                return True
        return False

    def _parse_screen(
        self, frame: dict, page_name: str
    ) -> DesignScreen | None:
        """
        Parse a single Figma frame into a DesignScreen.
        Returns None if the frame isn't meaningful.
        """
        frame_id = frame.get("id", "")
        frame_name = frame.get("name", "")
        frame_type = frame.get("type", "")

        # Only process actual frames at top level
        if frame_type not in ("FRAME", "COMPONENT"):
            return None
        
        children = frame.get("children", [])
        components = self._extract_components(children, depth=0)

        return DesignScreen(
            id=frame_id,
            name=frame_name,
            page=page_name,
            components=components,
            components_count=len(components)
        )
    
    def _extract_components(
        self, nodes: list, depth: int
    ) -> list[UIComponent]:
        """
        Recursively walk the node tree and extract
        meaningful UI components.
        Cap depth at 3 to avoid over-extraction.
        """
        if depth > 3:
            return []
        
        components = []

        for node in nodes:
            node_type = node.get("type", "")
            node_name = node.get("name", "")

            if node_type not in MEANINGFUL_TYPES:
                continue

            has_text = self._node_has_text(node)
            is_interactive = self._is_interactive(node_name)
            component_type = self._infer_component_type(node_name)
            children = node.get("children", [])

            component = UIComponent(
                id=node.get("id", ""),
                name=node_name,
                type=node_type,
                component_type=component_type,
                children_count=len(children),
                has_text=has_text,
                is_interactive=is_interactive
            )
            components.append(component)

            # Recurse into children
            if children:
                nested = self._extract_components(children, depth + 1)
                components.extend(nested)
            
        return components
    
    def _node_has_text(self, node: dict) -> bool:
        """ Checks if a node has text content. """
        if node.get("type") == "TEXT":
            return True
        for child in node.get("children", []):
            if self._node_has_text(child):
                return True
        return False
    
    def _is_interactive(self, node_name: str) -> bool:
        """Infer if a component is likely interactive from its name."""
        name_lower = node_name.lower()
        return any(kw in name_lower for kw in INTERACTIVE_KEYWORDS)
    
    def _infer_component_type(self, node_name: str) -> str | None:
        """
        Infer a semantic component type from the node name.
        Returns a clean label like 'button', 'input', 'navigation'.
        """
        name_lower = node_name.lower()
        for comp_type, keywords in COMPONENT_TYPE_MAP.items():
            if any(kw in name_lower for kw in keywords):
                return comp_type
        return None

    def _count_components(
        self, screen: DesignScreen
    ) -> list[tuple[str, int]]:
        """Count components by inferred type for the summary."""
        counts: dict[str, int] = {}
        for comp in screen.components:
            if comp.component_type:
                counts[comp.component_type] = (
                    counts.get(comp.component_type, 0) + 1
                )
        return list(counts.items())
    
    def _infer_features(
        self, page_names: list[str], screens: list[DesignScreen]
    ) -> list[str]:
        """
        Infer high-level product features from page names
        and screen names. These become part of the LLM context.
        """
        features = []
        all_names = " ".join(page_names).lower()

        feature_map = {
            "authentication": ["login", "signup", "register", "auth"],
            "dashboard": ["dashboard", "overview", "home"],
            "client management": ["client", "customer", "account"],
            "pipeline": ["pipeline", "funnel", "stage"],
            "project management": ["project", "task", "milestone"],
            "time management": ["time", "calendar", "schedule"],
            "procurement": ["procurement", "purchase", "vendor"],
            "contracts": ["contract", "agreement", "legal"],
            "contacts": ["contact", "people", "directory"],
            "admin": ["admin", "settings", "configuration"],
        }

        for feature, keywords in feature_map.items():
            if any(kw in all_names for kw in keywords):
                features.append(feature)

        return features
    
        
        