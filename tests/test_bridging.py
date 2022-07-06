import unittest
from shapely import wkt
from src.bridging import *


class TestBridging(unittest.TestCase):
    def test_is_free_true(self):
        line = wkt.loads("LineString(0 1, 1 3)")
        mp = wkt.loads("MultiPolygon(((0 0, 1 0, 0 1, 0 0)),((1 3, 2 3, 2 2, 1 3)))")
        self.assertTrue(is_free(line, mp.geoms))

    def test_is_free_intersection(self):
        line = wkt.loads("LineString(0 1, 2 5)")
        mp = wkt.loads("MultiPolygon(((0 0, 1 0, 0 1, 0 0)),((1 3, 2 3, 2 2, 1 3)),((2 5, 3 5, 3 4, 2 5)))")
        self.assertFalse(is_free(line, mp.geoms))

    def test_is_free_touch(self):
        line = wkt.loads("LineString(0 1, 2 5)")
        mp = wkt.loads("MultiPolygon(((0 0, 1 0, 0 1, 0 0)),((0 3, 2 3, 2 2, 0 3)),((2 5, 3 5, 3 4, 2 5)))")
        self.assertFalse(is_free(line, mp.geoms))

    def test_get_neighbours(self):
        edge = (0, 0, 3, 5)
        size1 = 3
        size2 = 6
        neighbours = get_neighbours(edge, size1, size2)
        self.assertEqual(neighbours, [(0, 2, 3, 4), (0, 2, 3, 0), (0, 1, 3, 4), (0, 1, 3, 0)])

    def test_is_secant_touch(self):
        line = wkt.loads("LineString(0 1, 1 3)")
        p = wkt.loads("Polygon((1 3, 2 3, 2 2, 1 3))")
        self.assertFalse(is_secant(line, p))

    def test_is_secant_no(self):
        line = wkt.loads("LineString(0 1, 0 3)")
        p = wkt.loads("Polygon((1 3, 2 3, 2 2, 1 3))")
        self.assertFalse(is_secant(line, p))

    def test_is_secant_cross(self):
        line = wkt.loads("LineString(0 1, 1 3)")
        p = wkt.loads("Polygon((0 3, 2 3, 2 2, 0 3))")
        self.assertTrue(is_secant(line, p))

    def test_is_secant_out_line(self):
        line = wkt.loads("LineString(0 3, 3 3)")
        p = wkt.loads("Polygon((1 3, 2 3, 2 2, 1 3))")
        self.assertTrue(is_secant(line, p))

    def test_is_secant_in_line(self):
        line = wkt.loads("LineString(1 2, 2 3)")
        p = wkt.loads("Polygon((0 3, 2 3, 2 1, 0 3))")
        self.assertFalse(is_secant(line, p))

    def test_get_lines(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)),((0 2, 0 3, 1 3, 0 2)),((2 0, 3 0, 3 1, 2 0)))")
        res = get_lines(mp.geoms)
        correct = {(0, 0, 0, 1): 'bound', (0, 1, 0, 2): 'bound', (0, 2, 0, 0): 'bound',
                   (1, 0, 1, 1): 'bound', (1, 1, 1, 2): 'bound', (1, 2, 1, 0): 'bound',
                   (2, 0, 2, 1): 'bound', (2, 1, 2, 2): 'bound', (2, 2, 2, 0): 'bound',
                   (0, 1, 1, 0): 'edge', (0, 1, 1, 2): 'edge',
                   (0, 1, 2, 0): 'edge', (0, 1, 2, 2): 'edge',
                   (0, 2, 1, 0): 'edge', (0, 2, 1, 2): 'edge',
                   (0, 2, 2, 0): 'edge', (0, 2, 2, 2): 'edge',
                   (1, 0, 2, 0): 'edge', (1, 0, 2, 2): 'edge',
                   (1, 2, 2, 0): 'edge', (1, 2, 2, 2): 'edge'}
        self.assertTrue(res == correct)

    def test_get_quads(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)),((0 2, 0 3, 1 3, 0 2)),((2 0, 3 0, 3 1, 2 0)))")
        vertexes = [geom.exterior.coords for geom in mp.geoms]
        edges = {(0, 1, 1, 0): 'edge', (0, 1, 1, 2): 'edge',
                 (0, 1, 2, 0): 'edge', (0, 1, 2, 2): 'edge',
                 (0, 2, 1, 0): 'edge', (0, 2, 1, 2): 'edge',
                 (0, 2, 2, 0): 'edge', (0, 2, 2, 2): 'edge',
                 (1, 0, 2, 0): 'edge', (1, 0, 2, 2): 'edge',
                 (1, 2, 2, 0): 'edge', (1, 2, 2, 2): 'edge'}
        res = get_quads(edges, vertexes)
        correct = {((0, 1, 1, 0), (0, 2, 1, 2)): 2.0,
                   ((0, 1, 2, 2), (0, 2, 2, 0)): 2.0,
                   ((1, 0, 2, 0), (1, 2, 2, 2)): 4.0}
        self.assertEqual(res, correct)

    def test_handle_edges(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)),((0 2, 0 3, 1 3, 0 2)),((2 0, 3 0, 3 1, 2 0)))")
        vertexes = [geom.exterior.coords for geom in mp.geoms]
        edges = {(0, 0, 0, 1): 'bound', (0, 1, 0, 2): 'bound', (0, 2, 0, 0): 'bound',
                 (1, 0, 1, 1): 'bound', (1, 1, 1, 2): 'bound', (1, 2, 1, 0): 'bound',
                 (2, 0, 2, 1): 'bound', (2, 1, 2, 2): 'bound', (2, 2, 2, 0): 'bound',
                 (0, 1, 1, 0): 'edge', (0, 1, 1, 2): 'edge',
                 (0, 1, 2, 0): 'edge', (0, 1, 2, 2): 'edge',
                 (0, 2, 1, 0): 'edge', (0, 2, 1, 2): 'edge',
                 (0, 2, 2, 0): 'edge', (0, 2, 2, 2): 'edge',
                 (1, 0, 2, 0): 'edge', (1, 0, 2, 2): 'edge',
                 (1, 2, 2, 0): 'edge', (1, 2, 2, 2): 'edge'}
        e1 = (0, 1, 2, 2)
        e2 = (0, 2, 2, 0)
        v = [(0, 1), (2, 2), (0, 2), (2, 0)]
        poly = wkt.loads("POLYGON ((0 1, 3 1, 2 0, 1 0, 0 1))")
        handle_edges(e1, e2, v, poly, edges, vertexes)
        new_edges = {(0, 0, 0, 1): 'bound', (0, 1, 0, 2): 'inner', (0, 2, 0, 0): 'bound',
                     (1, 0, 1, 1): 'bound', (1, 1, 1, 2): 'bound', (1, 2, 1, 0): 'bound',
                     (2, 0, 2, 1): 'bound', (2, 1, 2, 2): 'bound', (2, 2, 2, 0): 'inner',
                     (0, 1, 1, 0): 'edge', (0, 1, 1, 2): 'edge',
                     (0, 1, 2, 0): 'inner', (0, 1, 2, 2): 'bound',
                     (0, 2, 1, 0): 'secant', (0, 2, 1, 2): 'secant',
                     (0, 2, 2, 0): 'bound', (0, 2, 2, 2): 'inner',
                     (1, 0, 2, 0): 'secant', (1, 0, 2, 2): 'edge',
                     (1, 2, 2, 0): 'secant', (1, 2, 2, 2): 'edge'}
        self.assertTrue(edges == new_edges)

    def test_get_bridges(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)),((0 2, 0 3, 1 3, 0 2)),((2 0, 3 0, 3 1, 2 0)))")
        vertexes = [geom.exterior.coords for geom in mp.geoms]
        edges = {(0, 0, 0, 1): 'bound', (0, 1, 0, 2): 'bound', (0, 2, 0, 0): 'bound',
                 (1, 0, 1, 1): 'bound', (1, 1, 1, 2): 'bound', (1, 2, 1, 0): 'bound',
                 (2, 0, 2, 1): 'bound', (2, 1, 2, 2): 'bound', (2, 2, 2, 0): 'bound',
                 (0, 1, 1, 0): 'edge', (0, 1, 1, 2): 'edge',
                 (0, 1, 2, 0): 'edge', (0, 1, 2, 2): 'edge',
                 (0, 2, 1, 0): 'edge', (0, 2, 1, 2): 'edge',
                 (0, 2, 2, 0): 'edge', (0, 2, 2, 2): 'edge',
                 (1, 0, 2, 0): 'edge', (1, 0, 2, 2): 'edge',
                 (1, 2, 2, 0): 'edge', (1, 2, 2, 2): 'edge'}
        quads = {((0, 1, 1, 0), (0, 2, 1, 2)): 2.0,
                 ((0, 1, 2, 2), (0, 2, 2, 0)): 2.0,
                 ((1, 0, 2, 0), (1, 2, 2, 2)): 4.0}
        res_bridge_wkt = [g.wkt for g in get_bridges(vertexes, edges, quads, 2)]
        correct_wkt = ['POLYGON ((0 1, 3 1, 2 0, 1 0, 0 1))', 'POLYGON ((0 1, 0 2, 1 3, 3 1, 0 1))']
        self.assertEqual(res_bridge_wkt, correct_wkt)

    def test_build_bridges_3_1(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)), ((0 2, 0 3, 1 3, 0 2)), ((2 0, 3 0, 3 1, 2 0)))")
        res = build_bridges(mp.geoms, 1)
        correct = wkt.loads("Polygon((1 0, 0 0, 0 1, 0 2, 0 3, 1 3, 3 1, 3 0, 2 0, 1 0))")
        self.assertTrue(res.equals(correct))

    def test_build_bridges_3_2(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)), ((0 2, 0 3, 1 3, 0 2)), ((2 0, 3 0, 3 1, 2 0)))")
        res = build_bridges(mp.geoms, 2)
        correct = wkt.loads("MultiPolygon(((3 1, 3 0, 2 0, 1 0, 0 0, 0 1, 3 1)), ((1 3, 0 2, 0 3, 1 3)))")
        self.assertTrue(res.equals(correct))

    def test_build_bridges_2_1(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)), ((0 2, 0 3, 1 3, 0 2)))")
        res = build_bridges(mp.geoms, 1)
        correct = wkt.loads("Polygon((0 1, 0 2, 0 3, 1 3, 1 0, 0 0, 0 1))")
        self.assertTrue(res.equals(correct))

    def test_build_bridges_3sq_2(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 1, 1 0, 0 0)), "
                       "((0 2, 0 3, 1 3, 1 2, 0 2)), "
                       "((0 5, 0 6, 1 6, 1 5, 0 5)))")
        res = build_bridges(mp.geoms, 2)
        correct = wkt.loads("MultiPolygon(((0 2, 0 3, 1 3, 1 2, 1 1, 1 0, 0 0, 0 1, 0 2)), "
                            "((1 6, 1 5, 0 5, 0 6, 1 6)))")
        self.assertTrue(res.equals(correct))

    def test_build_bridges_3sq_1(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 1, 1 0, 0 0)), "
                       "((0 2, 0 3, 1 3, 1 2, 0 2)), "
                       "((0 5, 0 6, 1 6, 1 5, 0 5)))")
        res = build_bridges(mp.geoms, 1)
        correct = wkt.loads("Polygon((0 2, 0 3, 0 5, 0 6, 1 6, 1 5, 1 3, 1 2, 1 1, 1 0, 0 0, 0 1, 0 2))")
        self.assertTrue(res.equals(correct))

    def test_without_ring(self):
        mp = wkt.loads("MultiPolygon(((0 0, 5 0, 5 1, 4 1, 3 1, 2 1, 1 1, 0 1, 0 0)),"
                       "((0 2, 1 2, 2 2, 3 2, 4 2, 5 2, 5 3, 0 3, 0 2)),"
                       "((7 0, 8 0, 8 2, 7 2, 7 0)))")
        res = build_bridges(mp.geoms, 1)
        correct = wkt.loads("Polygon((2 1, 3 1, 4 1, 5 1, 5 0, 0 0, 0 1, 4 2, 3 2, "
                            "2 2, 1 2, 0 2, 0 3, 5 3, 8 2, 8 0, 7 0, 7 2, 5 2, 1 1, 2 1))")
        self.assertTrue(res.equals(correct))


if __name__ == '__main__':
    unittest.main()