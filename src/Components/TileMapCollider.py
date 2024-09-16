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
        tile_map = self.GetComponent(TileMap)
        matrix = tile_map.matrix

        size2 = self.tile_size * tile_map.size[0] / 2, self.tile_size * tile_map.size[1] / 2
        print(size2)

        for y, row in enumerate(matrix):
            for x, tile in enumerate(row):
                if tile in self.solids:
                    vertices = [
                        (x * self.tile_size - size2[0], y * self.tile_size - size2[1]),
                        ((x + 1) * self.tile_size - size2[0], y * self.tile_size - size2[1]),
                        ((x + 1) * self.tile_size - size2[0], (y + 1) * self.tile_size - size2[1]),
                        (x * self.tile_size - size2[0], (y + 1) * self.tile_size - size2[1])
                    ]
                    polygons.append(Polygon(vertices))

        self.polygons = polygons
        self.compile_numba_functions()
