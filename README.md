# PyDip -- Diplomacy Adjudication Engine

------

TL;DR: This is a library intended to resolve orders issued in the [game Diplomacy](https://en.wikipedia.org/wiki/Diplomacy\_(game)).

## Tests

The engine is written to follow recommended rules from the [Diplomacy Adjudicator Test Cases (DATC)](http://web.inter.nl.net/users/L.B.Kruijswijk/) site, with the exception that this engine does not permit ambiguous orders, and Civil Disobedience
procedures are currently simplified.

To run the tests:

    pip install pytest
    pytest

## Basic usage

Main concepts:

* The module `pydip.map` defines the map (class `Map`), which contains territories and adjacencies.
  * Territories are either a `CoastTerritory` (with a `parent`), a `LandTerritory` (with `coasts` which may be empty for land-locked territories), or a `SeaTerritory`.
  * The module also defines a class `SupplyCenterMap` (which additionally handles supply centers) and a class `OwnershipMap` (which additionally handles owned and home territories)
* The module `pydip.player` defines players (class `Player`) which have names and units (class `Unit`).
* The module `pydip.turn` defines functions `resolve_turn`, `resolve_retreat` and `resolve_adjustment`.

The file `example.py` contains a script with comments to get you going.
