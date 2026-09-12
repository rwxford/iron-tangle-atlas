"""Structural regression tests; these do not verify the novel's facts."""
import copy
import json
from pathlib import Path
import unittest
from scripts.validate_data import validate

ROOT = Path(__file__).resolve().parents[1]


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
        cls.html = (ROOT / 'index.html').read_text(encoding='utf-8')

    def setUp(self):
        self.data = copy.deepcopy(self.source)

    def assert_detected(self, text):
        self.assertTrue(any(text in e for e in validate(self.data)['errors']), text)

    def test_baseline_and_embedded_parity(self):
        self.assertEqual(validate(self.data, self.html)['errors'], [])

    def test_duplicate_id(self):
        self.data['nodes'].append(copy.deepcopy(self.data['nodes'][0]))
        self.assert_detected('duplicate ID')

    def test_missing_source(self):
        self.data['nodes'][0]['sources'] = ['missing-source']
        self.assert_detected('unknown reference')

    def test_missing_edge_endpoint(self):
        self.data['edges'][0]['to'] = 'nonexistent-station'
        self.assert_detected('unknown reference')

    def test_alias_collision(self):
        next(n for n in self.data['nodes'] if n['id'] == 'tangerine-plum-83')['aliases']['nightmare'] = '83(a)'
        self.assert_detected('duplicate service alias')

    def test_published_alias_contract(self):
        next(n for n in self.data['nodes'] if n['id'] == 'red-yellow-83')['aliases']['nightmare'] = '83(z)'
        self.assert_detected('published alias changed')

    def test_invalid_chapter(self):
        self.data['events'][0]['chapter'] = 'tomorrow'
        self.assert_detected('chapter must be')

    def test_half_missing_coordinate(self):
        self.data['nodes'][0]['x'] = None
        self.assert_detected('coordinates must be')

    def test_primary_without_primary_source(self):
        self.data['nodes'][0]['tier'] = 'primary'
        self.data['nodes'][0]['sources'] = ['index']
        self.assert_detected('primary label lacks')

    def test_location_and_travel_conflict(self):
        self.data['events'][0]['location'] = 'red-81'
        self.data['events'][0]['travel'] = {'to': 'red-81'}
        self.assert_detected('cannot both be set')

    def test_embedded_data_drift(self):
        self.data['nodes'][0]['note'] = 'Deliberate mismatch'
        self.assertIn('index.html embedded dataset differs from data.json', validate(self.data, self.html)['errors'])

    def test_missing_embedded_data(self):
        self.assertIn('index.html embedded dataset is missing or invalid', validate(self.data, '<html></html>')['errors'])

    def test_bad_collection_shape(self):
        self.data['edges'] = 'invalid'
        self.assert_detected('edges must be a list')


if __name__ == '__main__':
    unittest.main()
