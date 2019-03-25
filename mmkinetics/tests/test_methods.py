import unittest
import numpy as np
import methods

wilkinson_x = np.array([0.138, 0.220, 0.291, 0.560, 0.766, 1.460])
wilkinson_y = np.array([0.148, 0.171, 0.234, 0.324, 0.390, 0.493])
class TestMethods(unittest.TestCase):
    def test_lineweaver_burk_with_wilkinson(self):
        expected_results = ''
        results = methods.lineweaver_burk(wilkinson_x, wilkinson_y)
        assert results.name  == 'Lineweaver-Burk'
        assert results.error is None
        assert results.SS   == 0.0
        assert results.v_hat is None
        assert round(results.V, 3)  == 0.585
        assert round(results.Km, 3) == 0.441

if __name__ == '__main__':
    unittest.main()
