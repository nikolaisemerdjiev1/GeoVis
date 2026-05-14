from __future__ import annotations


COUNTRY_CODE_TO_NAME = {
    "AD": "Andorra",
    "AE": "United Arab Emirates",
    "AR": "Argentina",
    "AT": "Austria",
    "AU": "Australia",
    "BD": "Bangladesh",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "BO": "Bolivia",
    "BR": "Brazil",
    "CA": "Canada",
    "CH": "Switzerland",
    "CL": "Chile",
    "CN": "China",
    "CO": "Colombia",
    "CZ": "Czechia",
    "DE": "Germany",
    "DK": "Denmark",
    "EE": "Estonia",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "GB": "United Kingdom",
    "GR": "Greece",
    "HK": "Hong Kong",
    "HR": "Croatia",
    "HU": "Hungary",
    "ID": "Indonesia",
    "IE": "Ireland",
    "IL": "Israel",
    "IN": "India",
    "IS": "Iceland",
    "IT": "Italy",
    "JP": "Japan",
    "KR": "South Korea",
    "LK": "Sri Lanka",
    "LT": "Lithuania",
    "LV": "Latvia",
    "MX": "Mexico",
    "MY": "Malaysia",
    "NG": "Nigeria",
    "NL": "Netherlands",
    "NO": "Norway",
    "NZ": "New Zealand",
    "PE": "Peru",
    "PH": "Philippines",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "RS": "Serbia",
    "RU": "Russia",
    "SE": "Sweden",
    "SG": "Singapore",
    "SK": "Slovakia",
    "TH": "Thailand",
    "TR": "Turkey",
    "UA": "Ukraine",
    "US": "United States",
    "UY": "Uruguay",
    "ZA": "South Africa",
}

COUNTRY_ALIASES = {
    "CZECH REPUBLIC": "Czechia",
    "RUSSIAN FEDERATION": "Russia",
    "SOUTH KOREA": "South Korea",
    "KOREA, REPUBLIC OF": "South Korea",
    "UNITED STATES OF AMERICA": "United States",
    "USA": "United States",
    "UK": "United Kingdom",
    "GREAT BRITAIN": "United Kingdom",
}


def normalize_country(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return None

    upper = cleaned.upper()
    if upper in {"UNKNOWN", "N/A", "NA", "NULL"}:
        return None
    if len(upper) == 2 and upper in COUNTRY_CODE_TO_NAME:
        return COUNTRY_CODE_TO_NAME[upper]
    if upper in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[upper]

    return cleaned
