from Components.Collider import Collider, Polygon
from Components.TileMap import TileMap


class TileMapCollider(Collider):
    def __init__(self, solids: set[int], tile_size: int, mask: int = 1):
        Collider.Colliders.add(self)
        self.mask = mask
        self.solids = solids
        self.tile_size = tile_size

    def init(self):
        polygons = []
        matrix = self.GetComponent(TileMap).matrix

        for y, row in enumerate(matrix):
            for x, tile in enumerate(row):
                if tile in self.solids:
                    vertices = [
                        (x * self.tile_size, y * self.tile_size),
                        ((x + 1) * self.tile_size, y * self.tile_size),
                        ((x + 1) * self.tile_size, (y + 1) * self.tile_size),
                        (x * self.tile_size, (y + 1) * self.tile_size)
                    ]
                    polygons.append(Polygon(vertices))

        self.polygons = polygons
        self.compile_numba_functions()
