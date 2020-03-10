import pytest
from bw2data.tests import bw2test
from brightway2 import Database, Method, methods, projects, methods
from shutil import rmtree
import numpy as np

@pytest.fixture
@bw2test
def data_for_testing():
    # Make sure we are starting off with an empty project
    assert not len(Database('test_db'))
    assert not len(Database('biosphere'))

    biosphere = Database("biosphere")
    biosphere.register()
    biosphere.write({
        ("biosphere", "Water 1, from nature, in kg"): {
            'categories': ['natural resource'],
            'exchanges': [],
            'name': 'Water 1, from nature, in kg',
            'type': 'natural resource',
            'unit': 'kilogram'
        },
        ("biosphere", "Water 2, from nature, in kg"): {
            'categories': ['natural resource'],
            'exchanges': [],
            'name': 'Water 2, from nature, in kg',
            'type': 'natural resource',
            'unit': 'kilogram'
        },
        ("biosphere", "Water, from nature, in m3"): {
            'categories': ['natural resource'],
            'exchanges': [],
            'name': 'Water, from nature, in m3',
            'type': 'natural resource',
            'unit': 'cubic meter'
        },
        ("biosphere", "Water 1, to water, in kg"): {
            'categories': ['water'],
            'exchanges': [],
            'name': 'Water 1, to water, in kg',
            'type': 'emission',
            'unit': 'kilogram'
        },
        ("biosphere", "Water 2, to water, in kg"): {
            'categories': ['water', 'specific water'],
            'exchanges': [],
            'name': 'Water 2, to water, in kg',
            'type': 'emission',
            'unit': 'kilogram'
        },
        ("biosphere", "Water, to water, in m3"): {
            'categories': ['water'],
            'exchanges': [],
            'name': 'Water, to water, in m3',
            'type': 'emission',
            'unit': 'cubic meter'
        },
        ("biosphere", "Water, to air, in kg"): {
            'categories': ['air'],
            'exchanges': [],
            'name': 'Water to air, in kg',
            'type': 'emission',
            'unit': 'kilogram'
        },
        ("biosphere", "Water, to air, in m3"): {
            'categories': ['water'],
            'exchanges': [],
            'name': 'Water to air, in m3',
            'type': 'emission',
            'unit': 'cubic meter'
        },
        ("biosphere", "Something else"): {
            'categories': ['air'],
            'exchanges': [],
            'name': 'Something else to air, in m3',
            'type': 'emission',
            'unit': 'kg'
        },

    })
    assert len(Database('biosphere')) == 9

    test_db = Database("test_db")
    test_db.register()
    test_db.write({
        ("test_db", "X"): {
            'name': 'X',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'skip',
                'ratio': None,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
            ],
        },
        ("test_db", "A"): {
            'name': 'A',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'default',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'A'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1,
                    'formula': 'some_good_formula'
                },
                {
                    'name': 'Water 2, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1,
                    'formula': 'some bad formula'
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                    'loc': 1.0,
                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water, to air, in kg',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Water, to air, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(4.0),
                    'scale': 0.1
                },
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -6.0,
                    'input': ('test_db', 'L'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(6),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -7.0,
                    'input': ('test_db', 'N'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(7),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 8,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(8),
                    'scale': 0.1,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 9,
                    'input': ('test_db', 'U'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(9),
                    'scale': 0.1,
                },
            ],
        },
        ("test_db", "B"): {
            'name': 'B',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'inverse',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'B'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 2, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water, to air, in kg',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Water, to air, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(4.0),
                    'scale': 0.1
                },
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -6.0,
                    'input': ('test_db', 'L'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(6),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -7.0,
                    'input': ('test_db', 'N'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(7),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 8,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 9,
                    'input': ('test_db', 'U'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
            ],
        },
        ("test_db", "C"): {
            'name': 'C',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'default',
                'ratio': 2,
                'balance': 20
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'C'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 1, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 2, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Water 2, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(4.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water, to air, in kg',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Water, to air, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(4.0),
                    'scale': 0.1
                },
                {
                    'name': 'Somtething else, to air',
                    'unit': 'kilogram',
                    'amount': 100.0,
                    'input': ("biosphere", "Something else"),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(100.0),
                    'scale': 0.1
                },
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -6.0,
                    'input': ('test_db', 'L'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(6),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -7.0,
                    'input': ('test_db', 'N'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(7),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 16,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(16),
                    'scale': 0.1,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 18,
                    'input': ('test_db', 'U'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(18),
                    'scale': 0.1,
                },
            ],
        },
        ("test_db", "D"): {
            'name': 'D',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'inverse',
                'ratio': 2,
                'balance': 20
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'D'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 1, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 2, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Water 2, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water, to air, in kg',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Water, to air, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(4.0),
                    'scale': 0.1
                },
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -6.0,
                    'input': ('test_db', 'L'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(6),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -7.0,
                    'input': ('test_db', 'N'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(7),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 16,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 18,
                    'input': ('test_db', 'T'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
            ],
        },
        ("test_db", "E"): {
            'name': 'E',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'default',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'E'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 2, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water, from nature, in m3',
                    'unit': 'cubic meter',
                    'amount': 0.001,
                    'input': ('biosphere', 'Water, from nature, in m3'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.001),
                    'scale': 0.1
                },
                {
                    'name': 'Water to water, in m3',
                    'unit': 'cubic meter',
                    'amount': 0.003,
                    'input': ('biosphere', 'Water, to water, in m3'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.003),
                    'scale': 0.1
                },
                {
                    'name': 'Water, to air, in m3',
                    'unit': 'cubic meter',
                    'amount': 0.004,
                    'input': ('biosphere', 'Water, to air, in m3'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.004),
                    'scale': 0.1
                },
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
                {
                    'name': 'ww',
                    'unit': 'cubic meter',
                    'amount': -0.006,
                    'input': ('test_db', 'M'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.006),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -7.0,
                    'input': ('test_db', 'N'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(7),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 8,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(8),
                    'scale': 0.1,
                },
                {
                    'name': 'tap water',
                    'unit': 'cubic meter',
                    'amount': 0.009,
                    'input': ('test_db', 'T'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.009),
                    'scale': 0.1,
                },
            ],
        },
        ("test_db", "F"): {
            'name': 'F',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'inverse',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'F'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 2, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water, from nature, in m3',
                    'unit': 'cubic meter',
                    'amount': 0.001,
                    'input': ('biosphere', 'Water, from nature, in m3'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water to water, in m3',
                    'unit': 'cubic meter',
                    'amount': 0.003,
                    'input': ('biosphere', 'Water, to water, in m3'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.003),
                    'scale': 0.1
                },
                {
                    'name': 'Water, to air, in m3',
                    'unit': 'cubic meter',
                    'amount': 0.004,
                    'input': ('biosphere', 'Water, to air, in m3'),
                    'type': 'biosphere',
                    'uncertainty type': 1,
                    'loc': np.log(0.004),
                    'scale': 0.1
                },
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
                {
                    'name': 'ww',
                    'unit': 'cubic meter',
                    'amount': -0.006,
                    'input': ('test_db', 'M'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.006),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -7.0,
                    'input': ('test_db', 'N'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(7),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 8,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'tap water',
                    'unit': 'cubic meter',
                    'amount': 0.009,
                    'input': ('test_db', 'T'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
            ],
        },
        ("test_db", "G"): {
            'name': 'G',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'set_static',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'G'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 2, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water, to air, in kg',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Water, to air, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -6.0,
                    'input': ('test_db', 'L'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -7.0,
                    'input': ('test_db', 'N'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 8,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 9,
                    'input': ('test_db', 'U'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
            ],
        },
        ("test_db", "H"): {
            'name': 'H',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'set_static',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'H'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 2, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1

                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water, to air, in kg',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Water, to air, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -6.0,
                    'input': ('test_db', 'L'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -7.0,
                    'input': ('test_db', 'N'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 8,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 9,
                    'input': ('test_db', 'U'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
            ],
        },
        ("test_db", "I"): {
            'name': 'I',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'skip',
                'ratio': None,
                'balance': -20
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'I'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1

                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1

                },
                {
                    'name': 'Water, to air, in kg',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Water, to air, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(4.0),
                    'scale': 0.1
                },
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -6.0,
                    'input': ('test_db', 'L'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(6.0),
                    'scale': 0.1,
                    'negative': True
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -7.0,
                    'input': ('test_db', 'N'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
            ],
        },
        ("test_db", "J"): {
            'name': 'J',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'skip',
                'ratio': None,
                'balance': 20
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'J'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 2, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(2.0),
                    'scale': 0.1
                },
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 8,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(8),
                    'scale': 0.1,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 9,
                    'input': ('test_db', 'U'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(9),
                    'scale': 0.1,
                },
            ],
        },
        ("test_db", "K"): {
            'name': 'K',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'non-water product',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'skip',
                'ratio': None,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'K'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 2, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 2.0,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water, to air, in kg',
                    'unit': 'kilogram',
                    'amount': 4.0,
                    'input': ('biosphere', 'Water, to air, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'non-water product',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'X'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -6.0,
                    'input': ('test_db', 'L'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -7.0,
                    'input': ('test_db', 'N'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 8,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 9,
                    'input': ('test_db', 'U'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
            ],
        },
        ("test_db", "L"): {
            'name': 'wastewater treatment',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'ww',
            'production amount': -1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'default',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -1.0,
                    'input': ('test_db', 'L'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 1,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
            ]
        },
        ("test_db", "M"): {
            'name': 'wastewater treatment, in m3',
            'unit': 'cubic meter',
            'location': 'GLO',
            'reference product': 'ww',
            'production amount': -1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'default',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'ww',
                    'unit': 'cubic meter',
                    'amount': -1.0,
                    'input': ('test_db', 'M'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1000.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1000.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water, to water, in m3',
                    'unit': 'cubic meter',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water, to water, in m3'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 1000,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1000),
                    'scale': 0.1,
                },
            ]
        },
        ("test_db", "N"): {
            'name': 'wastewater treatment, in kg, 2',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'ww',
            'production amount': -1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'inverse',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -1.0,
                    'input': ('test_db', 'N'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 1,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },

            ]
        },
        ("test_db", "O"): {
            'name': 'wastewater treatment, in m3, 2',
            'unit': 'cubic meter',
            'location': 'GLO',
            'reference product': 'ww',
            'production amount': -1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'inverse',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'ww',
                    'unit': 'cubic meter',
                    'amount': -1.0,
                    'input': ('test_db', 'O'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1000.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1000.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water, to water, in m3',
                    'unit': 'cubic meter',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water, to water, in m3'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 1000,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },

            ]
        },
        ("test_db", "P"): {
            'name': 'wastewater treatment, in kg, 3',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'ww',
            'production amount': -1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'default',
                'ratio': 2,
                'balance': 1
            },
            'exchanges': [
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -1.0,
                    'input': ('test_db', 'P'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 0.5,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.5),
                    'scale': 0.1
                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 0.5,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.5),
                    'scale': 0.1
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 1,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1,
                },
            ]
        },
        ("test_db", "Q"): {
            'name': 'wastewater treatment, in kg, 4',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'ww',
            'production amount': -1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'inverse',
                'ratio': 2,
                'balance': 1
            },
            'exchanges': [
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -1.0,
                    'input': ('test_db', 'Q'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 0.5,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.5),
                    'scale': 0.1
                },
                {
                    'name': 'Water 2, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 0.5,
                    'input': ('biosphere', 'Water 2, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.5),
                    'scale': 0.1
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 1,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
            ]
        },
        ("test_db", "R"): {
            'name': 'wastewater treatment market, in kg',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'ww',
            'production amount': -1,
            'activity type': 'market activity',
            'expected results': {
                'strategy': 'default',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -1.0,
                    'input': ('test_db', 'R'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -0.25,
                    'input': ('test_db', 'L'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.25),
                    'scale': 0.1
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -0.25,
                    'input': ('test_db', 'N'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.25),
                    'scale': 0.1
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -0.25,
                    'input': ('test_db', 'P'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.25),
                    'scale': 0.1
                },
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': -0.25,
                    'input': ('test_db', 'Q'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.25),
                    'scale': 0.1
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 1,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1),
                    'scale': 0.1
                },
            ]
        },
        ("test_db", "S"): {
            'name': 'tap water production, in kg',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'tap water',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'default',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'S'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 2, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 2, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
            ]
        },
        ("test_db", "T"): {
            'name': 'tap water production, in cubic meter',
            'unit': 'cubic meter',
            'location': 'GLO',
            'reference product': 'tap water',
            'production amount': 1,
            'activity type': 'ordinary transforming activity',
            'expected results': {
                'strategy': 'default',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'ww',
                    'unit': 'cubic meter',
                    'amount': 1.0,
                    'input': ('test_db', 'T'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, from nature, in kg',
                    'unit': 'kilogram',
                    'amount': 1000.0,
                    'input': ('biosphere', 'Water 1, from nature, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1000.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water, from nature, in m3',
                    'unit': 'cubic meter',
                    'amount': 1.0,
                    'input': ('biosphere', 'Water, from nature, in m3'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1.0),
                    'scale': 0.1
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 1000.0,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(1000.0),
                    'scale': 0.1
                },
            ]
        },
        ("test_db", "U"): {
            'name': 'tap water market',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'tap water',
            'production amount': 1,
            'activity type': 'market activity',
            'expected results': {
                'strategy': '',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'ww',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'U'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 0.1,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.1),
                    'scale': 0.1
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 1.1,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },

            ]
        },
        ("test_db", "V"): {
            'name': 'tap water market',
            'unit': 'kilogram',
            'location': 'GLO',
            'reference product': 'tap water',
            'production amount': 1,
            'activity type': 'market activity',
            'expected results': {
                'strategy': 'tap_water_market',
                'ratio': 1,
                'balance': 0
            },
            'exchanges': [
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'V'),
                    'type': 'production',
                    'uncertainty type': 0,
                },
                {
                    'name': 'Water 1, to water, in kg',
                    'unit': 'kilogram',
                    'amount': 0.1,
                    'input': ('biosphere', 'Water 1, to water, in kg'),
                    'type': 'biosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.1),
                    'scale': 0.1
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 1.0,
                    'input': ('test_db', 'S'),
                    'type': 'technosphere',
                    'uncertainty type': 0,
                },
                {
                    'name': 'tap water',
                    'unit': 'kilogram',
                    'amount': 0.1,
                    'input': ('test_db', 'V'), #self
                    'type': 'technosphere',
                    'uncertainty type': 2,
                    'loc': np.log(0.1),
                    'scale': 0.1
                },
            ]
        },
    })
    yield {'project': projects.current}

    rmtree(projects.dir, ignore_errors=True)