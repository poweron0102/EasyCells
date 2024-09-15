from typing import Tuple, List

import numpy as np
from numba import njit

from Components.Component import Component, Transform


class Polygon:
    def __init__(self, vertices: List[Tuple[float, float]] | np.ndarray):
        if type(vertices) is list:
            self.vertices = np.array(vertices, dtype=np.float64)
        else:
            self.vertices = vertices

    def get_edges(self) -> np.ndarray:
        """
        Retorna as arestas do polígono como uma lista de vetores
        """
        edges = []
        for i in range(len(self.vertices)):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % len(self.vertices)]
            edges.append(v2 - v1)
        return np.array(edges)

    def get_normals(self):
        """
        Retorna os vetores normais das arestas do polígono
        """
        edges = self.get_edges()
        normals = np.zeros(edges.shape)
        for i in range(len(edges)):
            edge = edges[i]
            # Vetor perpendicular: (-y, x)
            normals[i] = np.array([-edge[1], edge[0]])
            # Normalizando o vetor
            normals[i] /= np.linalg.norm(normals[i])
        return normals

    def apply_transform(self, transform: Transform) -> 'Polygon':
        """
        Aplica uma transformação ao polígono
        """
        new_vertices = np.zeros(self.vertices.shape, dtype=np.float64)
        for i in range(len(self.vertices)):
            x, y = self.vertices[i]
            new_x = x * np.cos(transform.angle) - y * np.sin(transform.angle)
            new_y = x * np.sin(transform.angle) + y * np.cos(transform.angle)
            new_vertices[i] = np.array([new_x, new_y]) * transform.scale + np.array([transform.x, transform.y])

        return Polygon(new_vertices)


class Collider(Component):
    compiled: bool = False

    Colliders: List['Collider'] = []

    def __init__(self, polygons: List[Polygon], mask: int = 0):
        """
        polygons: lista de objetos Polygon
        """
        self.polygons = polygons
        self.compile_numba_functions()
        Collider.Colliders.append(self)
        self.mask = mask

    def on_destroy(self):
        Collider.Colliders.remove(self)

    def check_collision(self, other):
        """
        Verifica colisão entre este Collider e outro Collider usando o SAT
        """
        for polygon in self.polygons:
            for other_polygon in other.polygons:
                if not _sat_collision(polygon.vertices, other_polygon.vertices):
                    return False
        return True

    def compile_numba_functions(self):
        """
        Compila as funções numba para melhorar a desempenho
        """
        if Collider.compiled:
            return
        _sat_collision(self.polygons[0].vertices, self.polygons[0].vertices)
        print("Funções numba compiladas com sucesso!")
        Collider.compiled = True


@njit()
def project_polygon(vertices, axis):
    """
    Projeta os vértices de um polígono sobre um eixo
    """
    min_proj = np.inf
    max_proj = -np.inf
    for i in range(len(vertices)):
        projection = np.dot(vertices[i], axis)
        min_proj = min(min_proj, projection)
        max_proj = max(max_proj, projection)
    return min_proj, max_proj


@njit()
def _sat_collision(vertices_a, vertices_b):
    """
    Usa o Separating Axis Theorem (SAT) para verificar colisão entre dois polígonos convexos
    """
    for i in range(len(vertices_a)):
        # Calcula as arestas e os vetores normais
        v1A = vertices_a[i]
        v2A = vertices_a[(i + 1) % len(vertices_a)]
        edgeA = v2A - v1A
        axisA = np.array([-edgeA[1], edgeA[0]])
        axisA /= np.linalg.norm(axisA)

        # Projeta os dois polígonos sobre o eixo normal
        minA, maxA = project_polygon(vertices_a, axisA)
        minB, maxB = project_polygon(vertices_b, axisA)

        if maxA < minB or maxB < minA:
            return False  # Separação detectada

    for i in range(len(vertices_b)):
        v1B = vertices_b[i]
        v2B = vertices_b[(i + 1) % len(vertices_b)]
        edgeB = v2B - v1B
        axisB = np.array([-edgeB[1], edgeB[0]])
        axisB /= np.linalg.norm(axisB)

        minA, maxA = project_polygon(vertices_a, axisB)
        minB, maxB = project_polygon(vertices_b, axisB)

        if maxA < minB or maxB < minA:
            return False  # Separação detectada

    return True  # Colisão detectada


# Testes
if __name__ == "__main__":
    # Definindo polígonos
    poly1 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])  # Quadrado 1
    poly2 = Polygon([(1, 1), (3, 1), (3, 3), (1, 3)])  # Quadrado 2
    poly3 = Polygon([(4, 4), (6, 4), (5, 6)])  # Triângulo

    # Criando Colliders
    collider1 = Collider([poly1])
    collider2 = Collider([poly2])
    collider3 = Collider([poly3])

    # Testando colisões
    print("Colisão entre quadrado 1 e quadrado 2:", collider1.check_collision(collider2))
    print("Colisão entre quadrado 1 e triângulo:", collider1.check_collision(collider3))
    print("Colisão entre quadrado 2 e triângulo:", collider2.check_collision(collider3))
    print("Colisão entre triângulo e triângulo:", collider3.check_collision(collider3))
    print("Colisão entre quadrado 1 e quadrado 1:", collider1.check_collision(collider1))
    print("Colisão entre quadrado 2 e quadrado 2:", collider2.check_collision(collider2))
    print("Colisão entre triângulo e quadrado 1:", collider3.check_collision(collider1))
    print("Colisão entre triângulo e quadrado 2:", collider3.check_collision(collider2))

    # Saída esperada:
    """
    Colisão entre quadrado 1 e quadrado 2: True
    Colisão entre quadrado 1 e triângulo: False
    Colisão entre quadrado 2 e triângulo: False
    Colisão entre triângulo e triângulo: True
    Colisão entre quadrado 1 e quadrado 1: True
    Colisão entre quadrado 2 e quadrado 2: True
    Colisão entre triângulo e quadrado 1: False
    Colisão entre triângulo e quadrado 2: False
    """