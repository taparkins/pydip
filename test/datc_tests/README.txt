These tests were taken from the Diplomacy Adjudicator Test Cases (DATC) site
(http://web.inter.nl.net/users/L.B.Kruijswijk/)

These tests are included only as supplementary to other tests in the suite, since they are a strong standard for showing
compatibility with expected Diplomacy rule set.

DATC comes from the perspective of wanting an adjudicator that handles IRL games as well as online games. Consequently,
several test cases include illegal move actions. However, pydip intentionally disallows illegal moves from being submit.
To that end, some basic tests with illegal moves will be included (to ensure that those moves are properly prevented),
but many tests are excluded as illegitimate (because they depend on illegal moves being possible).

Any tests that are excluded or modified will be documented in the appropriate test file.