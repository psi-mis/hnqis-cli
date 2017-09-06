import pytest

from src.indicator_healtharea_updater import *


@pytest.fixture
def program_indicators():
    return [
        "GSae40Fyppf",
        "dSBYyCUjCXd",
        "tUdBD1JDxpn",
        "sGna2pquXOO",
        "Kswd1r4qWLh",
        "gWxh7DiRmG7",
        "ToQVD4irW3Q",
        "GxdhnY5wmHq",
        "ReQEl5V3z6p"
    ]


def test_create_numerators(program_indicators):
    expected = "I{GSae40Fyppf} + I{dSBYyCUjCXd} + I{tUdBD1JDxpn} + I{sGna2pquXOO} + I{Kswd1r4qWLh} + " \
               "I{gWxh7DiRmG7} + I{ToQVD4irW3Q} + I{GxdhnY5wmHq} + I{ReQEl5V3z6p}"
    actual = create_numerator(program_indicators)
    assert expected == actual
