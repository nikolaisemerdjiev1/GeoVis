from __future__ import annotations


REGION_ALIASES: dict[str, dict[str, str]] = {
    "United States": {
        "AL": "Alabama",
        "AK": "Alaska",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DC": "District of Columbia",
        "FL": "Florida",
        "GA": "Georgia",
        "HI": "Hawaii",
        "IA": "Iowa",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "MA": "Massachusetts",
        "MD": "Maryland",
        "ME": "Maine",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MO": "Missouri",
        "MS": "Mississippi",
        "MT": "Montana",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "NE": "Nebraska",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NV": "Nevada",
        "NY": "New York",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VA": "Virginia",
        "VT": "Vermont",
        "WA": "Washington",
        "WI": "Wisconsin",
        "WV": "West Virginia",
        "WY": "Wyoming",
    },
    "Canada": {
        "AB": "Alberta",
        "BC": "British Columbia",
        "MB": "Manitoba",
        "NB": "New Brunswick",
        "NL": "Newfoundland and Labrador",
        "NS": "Nova Scotia",
        "NT": "Northwest Territories",
        "NU": "Nunavut",
        "ON": "Ontario",
        "PE": "Prince Edward Island",
        "QC": "Quebec",
        "SK": "Saskatchewan",
        "YT": "Yukon",
    },
    "Brazil": {
        "AC": "Acre",
        "AL": "Alagoas",
        "AM": "Amazonas",
        "AP": "Amapa",
        "BA": "Bahia",
        "CE": "Ceara",
        "DF": "Federal District",
        "ES": "Espirito Santo",
        "GO": "Goias",
        "MA": "Maranhao",
        "MG": "Minas Gerais",
        "MS": "Mato Grosso do Sul",
        "MT": "Mato Grosso",
        "PA": "Para",
        "PB": "Paraiba",
        "PE": "Pernambuco",
        "PI": "Piaui",
        "PR": "Parana",
        "RJ": "Rio de Janeiro",
        "RN": "Rio Grande do Norte",
        "RO": "Rondonia",
        "RR": "Roraima",
        "RS": "Rio Grande do Sul",
        "SC": "Santa Catarina",
        "SE": "Sergipe",
        "SP": "Sao Paulo",
        "TO": "Tocantins",
    },
    "Australia": {
        "ACT": "Australian Capital Territory",
        "NSW": "New South Wales",
        "NT": "Northern Territory",
        "QLD": "Queensland",
        "SA": "South Australia",
        "TAS": "Tasmania",
        "VIC": "Victoria",
        "WA": "Western Australia",
    },
    "Japan": {
        "AICHI": "Aichi",
        "AKITA": "Akita",
        "AOMORI": "Aomori",
        "CHIBA": "Chiba",
        "EHIME": "Ehime",
        "FUKUI": "Fukui",
        "FUKUOKA": "Fukuoka",
        "FUKUSHIMA": "Fukushima",
        "GIFU": "Gifu",
        "GUNMA": "Gunma",
        "HIROSHIMA": "Hiroshima",
        "HOKKAIDO": "Hokkaido",
        "HYOGO": "Hyogo",
        "IBARAKI": "Ibaraki",
        "ISHIKAWA": "Ishikawa",
        "IWATE": "Iwate",
        "KAGAWA": "Kagawa",
        "KAGOSHIMA": "Kagoshima",
        "KANAGAWA": "Kanagawa",
        "KOCHI": "Kochi",
        "KUMAMOTO": "Kumamoto",
        "KYOTO": "Kyoto",
        "MIE": "Mie",
        "MIYAGI": "Miyagi",
        "MIYAZAKI": "Miyazaki",
        "NAGANO": "Nagano",
        "NAGASAKI": "Nagasaki",
        "NARA": "Nara",
        "NIIGATA": "Niigata",
        "OITA": "Oita",
        "OKAYAMA": "Okayama",
        "OKINAWA": "Okinawa",
        "OSAKA": "Osaka",
        "SAGA": "Saga",
        "SAITAMA": "Saitama",
        "SHIGA": "Shiga",
        "SHIMANE": "Shimane",
        "SHIZUOKA": "Shizuoka",
        "TOCHIGI": "Tochigi",
        "TOKUSHIMA": "Tokushima",
        "TOKYO": "Tokyo",
        "TOTTORI": "Tottori",
        "TOYAMA": "Toyama",
        "WAKAYAMA": "Wakayama",
        "YAMAGATA": "Yamagata",
        "YAMAGUCHI": "Yamaguchi",
        "YAMANASHI": "Yamanashi",
    },
}

COUNTRIES_WITH_REGION_SUPPORT = frozenset(REGION_ALIASES)


def clean_region(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return None
    if cleaned.upper() in {"UNKNOWN", "N/A", "NA", "NULL"}:
        return None
    return cleaned


def normalize_region(country: str | None, region: str | None) -> str | None:
    cleaned = clean_region(region)
    if cleaned is None:
        return None
    if country not in REGION_ALIASES:
        return cleaned

    aliases = REGION_ALIASES[country]
    upper = cleaned.upper().replace(".", "")
    return aliases.get(upper, cleaned)


def supports_regions(country: str | None) -> bool:
    return country in COUNTRIES_WITH_REGION_SUPPORT
