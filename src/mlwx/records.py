"""Recorded values the package checks its inputs against (DECISIONS D98.2).

The SHA-256 of each stage C table (F138.4, session104_stagec_f025_048_table.meta.txt, F149.2). The
product refit reads these tables, so it checks each file against its recorded value first. A test
checks these constants against the record. Tables are named by ICAO code.
"""

DEV_0_24 = {   # F138.4: stagec_dev_<ICAO>.csv.gz
    "EGLC": "af8848e091c79aecac5f809536e4dec20757d288f7ebc1cf3e830d33a69c9126",
    "LFPG": "5b113123c7642eefb8d212cbe5151f43e8ba343a231dc90d4461ed104e6b661f",
    "KDSM": "17461736cd23585781ebf01a842469a1ea6b0e93571bea250869a23271dc0e32",
    "YSDU": "57a11a4f00250304f289de158223eff45f841d572e3c3c7f65e5b6fc6c0fa829",
    "KRNO": "6e2d0779f6b5ea92dc77e3b074030ac3676bd90cffe3b44ab6e3441c06831ec3",
    "KSFO": "11fa6385f05c57cf627734d9caed13927f1e176e07c5fc039f700d30fd1ceff8",
}
DEV_25_48 = {  # session104_stagec_f025_048_table.meta.txt (its SHA-256 27622ada...5859 is in F147.2)
    "EGLC": "947bf2f0920e1a1f972ea9297fcc9bdc5c987562e13ee5daa7ae5ab866066ea9",
    "LFPG": "04dbd411dbd683dfe3a09597ea8407cc75c8afc86100b31a8396caca0ff52c35",
    "KDSM": "bd2d80c01211a3c399d6904068bfb9377b0ad9091e13878621526835434ee2f3",
    "YSDU": "b801fcc2d9e2c9dd843ea920e8dd8ac88f33f5db7057bb4ae1ca46a2b16981ac",
    "KRNO": "3ca1d4ff8933f14c6e898525ba445af080b92c0545989fe39b3d7bdbfdd6bd58",
    "KSFO": "2e355c0146e1bc8923f632d208c084f646ec3ebcd9dfa2bb22e22c363e81b84b",
}
CLAIM_TABLES = {   # F149.2: (hours 0 to 24, hours 25 to 48)
    "EDDM": ("9d9e38201d0aa63ae0da0a20c64254c172f57993df0d99dd767a567a5418c84d",
             "b5600c13948fd7ad6bd6411366b3676211b68dd332e37c3a409262eac3457c7b"),
    "KORD": ("51c69aa5b204f7991ae7522fd850b5b3c4715f017ed4ee2f1b4269a2d4a515ad",
             "2252e3ffb73294e31b4aba1e605f204f70ccc80cbbcb701f79173e0940770662"),
    "CYYZ": ("899e54777fdff5f8ac0b6cc78b15ebea6340a072b23c5acf6c39486c139c25d7",
             "ab631d6e43750071e9b7878cb24127269aae5a3831d1234a299c8a0ab2054b44"),
    "ZGSZ": ("1a83bb1ba7b7c2ed389244fd3362c32e6a641847b3b074680d00a84a858de011",
             "b70b5f4c648fa6e5971084e8993e99fa2d2fffd7394e6e7b262c06aa6d2df0f5"),
    "ZUCK": ("1be74331235cd973b919db7aa8a587b7065eaf154e95f08f03dbf62ac0a89379",
             "35e85af2c47df13afd0fbd8279aadd330157072bb8d1f17f800515619296b096"),
    "NZWN": ("f5c7a598cef58190e593d74cd961fd15912d9fd3ce196f149092807215a92e74",
             "4db4350540342b4a01502731a0daf5b943a6e619a0893ee6bf12ca6ade2f3fc0"),
}


def table_name(airport, hour_set):
    """File name of an airport's stage C table; hour_set is 'f000_024' or 'f025_048'."""
    if airport.role == "development":
        return f"stagec_dev_{airport.icao}.csv.gz" if hour_set == "f000_024" else f"stagec_dev_f025_048_{airport.icao}.csv.gz"
    return f"stagec_claim_{hour_set}_{airport.icao}.csv.gz"


def recorded_sha(airport, hour_set):
    if airport.role == "development":
        return (DEV_0_24 if hour_set == "f000_024" else DEV_25_48)[airport.icao]
    return CLAIM_TABLES[airport.icao][0 if hour_set == "f000_024" else 1]
