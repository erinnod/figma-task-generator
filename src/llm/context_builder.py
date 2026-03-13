from __future__ import annotations
from src.figma.models import DesignContext, DesignScreen

class ContextBuilder:
    """
    Transforms a DesignContext into a structured text representation
    suitable for LLM reasoning.

    This is the bridge between the parsing stage and the LLM stage.
    The output of this class is what gets embedded into the prompt.
    """

    def build(self, design_context: DesignContext) -> str:
        """
        Build a clean, structured text summary of the design.
        Returns a string ready to be inserted into an LLM prompt.
        """
        sections = [
            self._build_overview(design_context),
            self._build_features(design_context),
            self._build_component_summary(design_context),
            self._build_screens(design_context),
        ]

        return "\n\n".join(sections)

    def _build_overview(self, context: DesignContext) -> str:
        return f"""## Design Overview
File: {context.file_name}
Total screens: {context.total_screens}
Pages / Sections: {", ".join(context.pages)}"""

    def _build_features(self, context: DesignContext) -> str:
        features = "\n".join(
            f"- {feature}" for feature in context.inferred_features
        )
        return f"""## Inferred Product Features
{features}"""

    def _build_component_summary(self, context: DesignContext) -> str:
        lines = ["## Component Summary"]
        for comp_type, count in sorted(
            context.component_summary.items(), key=lambda x: x[0]
        ):
            lines.append(f"- {comp_type}: {count}")
        return "\n".join(lines)

    def _build_screens(self, context: DesignContext) -> str:
        lines = ["## Screens by Section"]

        # Group screens by page
        pages: dict[str, list[DesignScreen]] = {}
        for screen in context.screens:
            if screen.page not in pages:
                pages[screen.page] = []
            pages[screen.page].append(screen)

        for page_name, screens in pages.items():
            lines.append(f"### {page_name}")
            for screen in screens[:10]: # cap to 10 per page
                interactive = [
                    c.name for c in screen.components if c.is_interactive
                ][:5] # top 5 interactive components

                line = f"- {screen.name}"
                if interactive:
                    line += f" (interactive: {', '.join(interactive)})"
                lines.append(line)

            if len(screens) > 10:
                lines.append(
                    f"  ... and {len(screens) - 10} more screens"
                )

        return "\n".join(lines)

def build_screen_context(
    self,
    screen: "DesignScreen",
    full_context: "DesignContext"
) -> str:
    """
    Build context for a single screen.
    Includes the screen's own components plus
    the broader product context for better reasoning.
    """
    # Product overview so the LLM knows what kind of app this is
    product_summary = (
        f"Product: {full_context.file_name}\n"
        f"Features: {', '.join(full_context.inferred_features)}\n"
        f"Total screens in product: {full_context.total_screens}"
    )

    # This specific screen's details
    components = screen.components
    interactive = [c for c in components if c.is_interactive]
    by_type = {}
    for c in components:
        if c.component_type:
            by_type.setdefault(c.component_type, []).append(c.name)

    component_lines = []
    for comp_type, names in by_type.items():
        # Show up to 5 examples per type to keep context tight
        examples = names[:5]
        extra = len(names) - 5
        line = f"  - {comp_type.title()}: {', '.join(examples)}"
        if extra > 0:
            line += f" (+{extra} more)"
        component_lines.append(line)

    screen_detail = (
        f"Screen: {screen.name}\n"
        f"Page/Section: {screen.page}\n"
        f"Total components: {len(components)}\n"
        f"Interactive elements: {len(interactive)}\n"
        f"Components by type:\n" +
        "\n".join(component_lines)
        if component_lines
        else "No components extracted"
    )

    return f"{product_summary}\n\n{screen_detail}"
