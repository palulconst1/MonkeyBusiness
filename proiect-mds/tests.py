import requests
import unittest



class TestAPI(unittest.TestCase):
    url = "http://127.0.0.1:8000"
    
    def test_get_root(self):
        r = requests.get(self.url + '/')
        self.assertEqual(r.status_code, 200)

    def test_get_status(self):
        r = requests.get(self.url + '/status')
        self.assertEqual(r.status_code, 200)

    def test_post_RGB(self):
        payload = {'r': 10, 'g': 15, 'b': 20}
        r = requests.post(self.url + '/lamp/rgb', params=payload)
        self.assertEqual(r.status_code, 200)

    def test_post_invalid_RGB(self):
        payload = {'r': "10", 'g': 15, 'b': 20}
        r = requests.post(self.url + '/lamp/rgb', params=payload)
        self.assertEqual(r.status_code, 200)

    def test_post_RGB(self):
        payload = {'r': 10, 'g': 15, 'b': 20}
        r = requests.post(self.url + '/lamp/rgb', params=payload)
        self.assertEqual(r.status_code, 200)

    def test_post_toggle(self):
        r = requests.post(self.url + '/lamp/toggle')
        self.assertEqual(r.status_code, 200)

    def test_post_reading_mode(self):
        r = requests.post(self.url + '/lamp/reading_mode')
        self.assertEqual(r.status_code, 200)

    def test_post_wave(self):
        r = requests.post(self.url + '/lamp/wave')
        self.assertEqual(r.status_code, 200)

    def test_post_intensity(self):
        payload = {'new_intensity': 50}
        r = requests.post(self.url + '/lamp/intensity', params=payload)
        self.assertEqual(r.status_code, 200)

    def test_post_invalid_intensity(self):
        payload = {'new_intensity': 'aaa'}
        r = requests.post(self.url + '/lamp/intensity', params=payload)
        self.assertEqual(r.status_code, 422)


if __name__ == '__main__':
    unittest.main()