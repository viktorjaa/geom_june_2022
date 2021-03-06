from shapely.geometry import Point, LineString, Polygon, MultiPolygon

# Альтернативная обработка уменьшения количества числа вершин.
# По очереди на приоритетном ребре удаляется одна из точек,
# а другая сохраняется, если удаленная точка вогнутая,
# или заменяется пересечением соседей ребра, если удаленная тчока выпуклая
# Приоритет определяется прибавляемой площадью при замене точек.

# В текущей реализации алгоритм долго обрабатывает большое число вершин.


class StraightLine:
    """Sets a straight line with two points."""
    def __init__(self, p1, p2):
        self.a = p1.y - p2.y
        self.b = p2.x - p1.x
        self.c = p2.x * self.a + p2.y * self.b

    def inter_point(self, other):
        """Finds the intersection of this and another straight line."""
        d = self.a * other.b - self.b * other.a
        dx = self.c * other.b - self.b * other.c
        dy = self.a * other.c - self.c * other.a
        if d == 0:
            return []
        else:
            x = dx / d
            y = dy / d
            return Point(x, y)


class ChangeList(list):
    """List of ChangePoint instances."""
    def fill(self, geom):
        """Get ChangePoint instances from list of Points."""
        for point in geom[:-1]:
            change = self.ChangePoint(point)
            self.append(change)
        for elem in self:
            self._calc_elem(elem)
        return self

    def _calc_elem(self, elem):
        """Initiates calc_change of some element."""
        index = self.index(elem)
        next_ch = self[(index + 1) % len(self)]
        prev_ch = self[index - 1]
        preprev_ch = self[index - 2]
        poly = self.polygonize()
        elem.calc_change(next_ch, prev_ch, preprev_ch, poly)

    def recalc_elem(self, elem):
        """Makes calc_change of some element when in changes."""
        index = self.index(elem)
        next_ch = self[(index + 1) % len(self)]
        after_next_ch = self[(index + 2) % len(self)]
        prev_ch = self[index - 1]
        preprev_ch = self[index - 2]
        prev_ch.update(next_ch, elem, preprev_ch)
        self.remove(elem)
        self._calc_elem(preprev_ch)
        self._calc_elem(prev_ch)
        self._calc_elem(next_ch)
        self._calc_elem(after_next_ch)

    def get_min(self):
        return min(self, key=lambda x: x.area)

    def recalc_min(self):
        self.recalc_elem(self.get_min())

    def polygonize(self):
        """Makes polygon from current points."""
        return Polygon([item.point for item in self])

    class ChangePoint:
        """Keeps coordinates of point, its convexity and additional area for its change."""
        def __init__(self, point):
            self._point = Point(point)
            self._method = "no_method"
            self._area = float("inf")

        @property
        def point(self):
            return self._point

        @point.setter
        def point(self, point):
            self._point = point

        @property
        def area(self):
            return self._area

        @property
        def method(self):
            return self._method

        def calc_change(self, next_ch, prev_ch, preprev_ch, poly):
            """Calculates convexity and additional area for change of point."""
            try:
                prev_p = prev_ch.point
                next_p = next_ch.point
                line = LineString([prev_p, next_p]).difference(prev_p).difference(next_p)
                if poly.covers(line):
                    self._method = "convex"
                    preprev_p = preprev_ch.point
                    convex_point = self._find_convex_point(preprev_p, prev_p,
                                                           self._point, next_p)
                    self._area = Polygon([convex_point, self._point, prev_p]).area
                else:
                    self._method = "concave"
                    self._area = Polygon([self.point, next_p, prev_p]).area
            except ValueError:
                self._method = "no_method"
                self._area = float("inf")

        @classmethod
        def _find_convex_point(cls, preprev_p, prev_p, this_p, next_p):
            """Findes point to change convex point."""
            l_prev = StraightLine(preprev_p, prev_p)
            l_next = StraightLine(this_p, next_p)
            new_p = l_next.inter_point(l_prev)
            if new_p:
                if cls._check_position(next_p, this_p, new_p, prev_p, preprev_p):
                    return new_p
                else:
                    raise ValueError("No point of intersection on the interesting side.")
            else:
                raise ValueError("No point of intersection, edges are ||.")

        @staticmethod
        def _check_position(next_p, this_p, new_p, prev_p, preprev_p):
            """Checks if convex point not violate initial geometry."""
            def are_ordered(a1, a2, a3):
                return a1 >= a2 >= a3 or a1 <= a2 <= a3

            prev_x = are_ordered(preprev_p.x, prev_p.x, new_p.x)
            prev_y = are_ordered(preprev_p.y, prev_p.y, new_p.y)
            next_x = are_ordered(next_p.x, this_p.x, new_p.x)
            next_y = are_ordered(next_p.y, this_p.y, new_p.y)
            return prev_x and prev_y and next_x and next_y

        def update(self, next_ch, elem_ch, prev_ch):
            """Changes coordinates of point."""
            try:
                if elem_ch.method == "convex":
                    prev_p = prev_ch.point
                    elem_p = elem_ch.point
                    next_p = next_ch.point
                    convex_point = self._find_convex_point(prev_p, self.point,
                                                           elem_p, next_p)
                    self._point = convex_point
            except Exception as e:
                print(e)


def get_changes(geoms):
    """Makes ChangeList."""
    changes = []
    for geom in geoms:
        geom_changes = ChangeList().fill(geom)
        changes.append(geom_changes)
    return changes


def get_change_of_min(changes):
    """Returns polygon which contains ChangePoint with minimal area."""
    mns = [change.get_min() for change in changes]
    mn = min(mns, key=lambda x: x.area)
    index = mns.index(mn)
    return index


def simplify(polygons, m):
    """Simplifies amount of vertexes."""
    geoms = [list(polygon.exterior.coords) for polygon in polygons]
    n = sum([len(geom) - 1 for geom in geoms])
    changes = get_changes(geoms)
    for cnt in range(n - m):
        index = get_change_of_min(changes)
        changes[index].recalc_min()
    return MultiPolygon([change.polygonize() for change in changes])
