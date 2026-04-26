from .models import FooterSection, TopbarSection


def footer_section(request):
    """Inject FooterSection singleton into every template (used by footer component)."""
    return {"footer": FooterSection.get_solo()}


def topbar_section(request):
    """Inject TopbarSection singleton into every template (used by navbar component)."""
    return {"topbar": TopbarSection.get_solo()}
