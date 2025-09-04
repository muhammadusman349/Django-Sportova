from django.conf import settings
import re


def site_contacts(request):
    raw = getattr(settings, "WHATSAPP_NUMBER", "")
    cleaned = re.sub(r"\D", "", raw)
    return {
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", ""),
        "WHATSAPP_NUMBER": raw,
        "WHATSAPP_NUMBER_CLEAN": cleaned,
    }
