# Geocoding Failures Summary

## Myanmar
- **Status**: Resolved (Manually added to geocode_cache.json)
- **Failed rows**: 1,372 / 15,680 (Now geocoded)
- **Resolved Admin2 values**:
    - Hopang
    - Pa Laung Self-Administered Zone
    - Pyay
    - Tachileik
    - Kokang Self-Administered Zone
    - Muse
    - Mongmit

- **Fix Instruction**: To resolve these failures, manually add entries to your geocoding cache file (e.g., `geocode_cache.json`). The format should be:
  `"<Admin2_value>|<admin1>|<country>": [<latitude>, <longitude>]`
  For example:
  `"Hopang|SomeAdmin1|Myanmar": [19.6789, 96.1989]`

## Ukraine
- **Status**: Resolved (Manually added to geocode_cache.json)
- **Failed rows**: 1,200 (Now geocoded)
- **Resolved Admin2 values**:
    - Feodosiiskyi
    - Perekopskyi
    - Dzhankoiskyi
    - Kurmanskyi
    - Bakhchysaraiskyi
    - Simferopolskyi
    - Bilohirskyi
    - Berezivskyi
    - Rozdilnianskyi
    - Yevpatoriiskyi

- **Unresolved**:
    - nan (Invalid administrative unit)