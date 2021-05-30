from app.models.language import Language


def get_frontier_api_url_for_language(language: Language) -> str:
    """Get the Frontier API URL according to the specified language."""
    languages_mapping = {
        Language.ENGLISH: "en-US",
        Language.FRENCH: "fr-FR",
        Language.GERMAN: "de-DE",
        Language.SPANISH: "es-ES",
        Language.RUSSIAN: "ru-RU",
    }
    return f"https://cms.zaonce.net/{languages_mapping[language]}/jsonapi/node"
