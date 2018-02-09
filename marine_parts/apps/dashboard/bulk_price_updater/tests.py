import pyexcel as p
import django.test as test


test_data = \
    [
        {
            'IMMFGC' : 'A/P',
            'IMITMC' : '4721',
            'IMDESC' : 'PACKING-TEFLON 3/16X',
            'IMSUOM' : 'EA',
            'List' : '27.13',
            'Dealer': '23.26',
            'Your Price' : '23.26'
        },
        {
            'IMMFGC': 'A/P',
            'IMITMC': '4723',
            'IMDESC': 'PACKING-TEFLON 5/16X	',
            'IMSUOM': 'EA',
            'List': '12.43',
            'Dealer': '10.66',
            'Your Price': '10.66'
        },
        {
            'IMMFGC' : 'A/P',
            'IMITMC' : '4725',
            'IMDESC' : 'PACKING-TEFLON 1/2X3',
            'IMSUOM' :'EA',
            'List' : '79.43',
            'Dealer': '68.12',
            'Your Price' : '68.12'
        },
        {
            'IMMFGC': 'ABA',
            'IMITMC': '13302',
            'IMDESC': 'RUBBER LINED CLAMP',
            'IMSUOM': 'EA',
            'List': '1.8',
            'Dealer': '0.83',
            'Your Price': '0.68'
        }
    ]


class Test_(test.TestCase):

    def load_fixtures(self):
        pass

    def setUp(self):

    def test_updateAllProducts_return6(self):
        pass