from typing import List

import numpy as np
import pygame as pg
from numba import njit, prange

from Components.Camera import Camera
from Components.Component import Component, Transform
from Geometry import Vec2


class Polygon:
    def __init__(self, vertices: List[List[float]] | np.ndarray):
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
    colliders: List['Collider'] = []

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value
        if value:
            self.loop = self.loop_debug
        else:
            self.loop = self.loop_no_debug

    def __init__(self, polygons: List[Polygon], mask: int = 1, debug: bool = False):
        """
        Polygons: lista de objetos Polygon
        mask: máscara de colisão (bitwise)
        """
        self.word_position = Transform()
        self.polygons: List[Polygon] = polygons
        self.compile_numba_functions()
        self.mask = mask
        self.debug = debug
        Collider.colliders.append(self)

    def init(self):
        self.word_position = self.CalculateGlobalTransform()

    def on_destroy(self):
        Collider.colliders.remove(self)
        self.on_destroy = lambda: None

    def loop_debug(self):
        self.word_position = Transform.Global
        # print(f"collider: {self.__class__}\n   \033[92m    Word position: {self.word_position} \033[0m")
        Camera.instance.debug_draws.append(self.draw)

    def loop_no_debug(self):
        self.word_position = Transform.Global

    def draw(self, cam_x: float, cam_y: float, scale: float):
        """
        for debug only
        """
        position = self.word_position * scale
        position.scale *= scale

        for polygon in self.polygons:
            vertices = polygon.apply_transform(position).vertices
            pg.draw.polygon(
                self.game.screen,
                (255, 0, 0),
                vertices - np.array([cam_x, cam_y]),
                3
            )

    def check_collision_global(self, other) -> bool:
        for polygon in self.polygons:
            polygon = polygon.apply_transform(self.word_position)
            for other_polygon in other.polygons:
                other_polygon = other_polygon.apply_transform(other.word_position)
                if _sat_collision(polygon.vertices, other_polygon.vertices):
                    return True
        return False

    def check_collision(self, other) -> bool:
        for polygon in self.polygons:
            for other_polygon in other.polygons:
                if _sat_collision(polygon.vertices, other_polygon.vertices):
                    return True
        return False

    def compile_numba_functions(self):
        """
        Compila as funções numba para melhorar a desempenho
        """
        if Collider.compiled:
            return

        _sat_collision(self.polygons[0].vertices, self.polygons[0].vertices)
        _ray_polygon_intersection_numba(
            np.array([0, 0], dtype=np.float64),
            np.array([1, 1], dtype=np.float64),
            np.array([
                [0, 0],
                [1, 1],
                [2, 2],
                [4, 4]
            ], dtype=np.float64),
            10
        )

        print("Collider functions compiled")
        Collider.compiled = True

    def bounding_box(self) -> pg.Rect:
        """
        Retorna o menor retângulo que contém o collider
        """
        min_x = np.inf
        min_y = np.inf
        max_x = -np.inf
        max_y = -np.inf

        for polygon in self.polygons:
            polygon = polygon.apply_transform(self.word_position)
            for vertex in polygon.vertices:
                min_x = min(min_x, vertex[0])
                min_y = min(min_y, vertex[1])
                max_x = max(max_x, vertex[0])
                max_y = max(max_y, vertex[1])

        return pg.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def ray_cast(
            self,
            origin: Vec2[float],
            direction: Vec2[float],
            max_distance: float,
    ) -> 'tuple[Vec2[float], Vec2[float]] | None':
        """
        Usa coordenadas globais
        Retorna:
        Vec2: Ponto de interseção
        Vec2: Normal da superfície atingida
        """
        origin_array = np.array([origin.x, origin.y], dtype=np.float64)
        direction_array = np.array([direction.x, direction.y], dtype=np.float64)

        closest_point = None
        closest_normal = None
        closest_distance = max_distance

        for polygon in self.polygons:
            polygon = polygon.apply_transform(self.word_position)
            intersection, normal, distance = _ray_polygon_intersection_numba(origin_array, direction_array,
                                                                             polygon.vertices, max_distance)

            if intersection is not None and distance < closest_distance:
                closest_point = Vec2(intersection[0], intersection[1])
                closest_normal = Vec2(normal[0], normal[1])
                closest_distance = distance

        if closest_point:
            if np.dot(closest_normal.to_tuple, direction_array) > 0:
                closest_normal *= -1
            return closest_point, closest_normal

        return None

    @staticmethod
    def ray_cast_static(
            origin: Vec2[float],
            direction: Vec2[float],
            max_distance: float,
            mask: int
    ) -> 'tuple[Collider, Vec2[float], Vec2[float]] | None':
        """
        Retorna:
        Collider: Collider atingido pelo raio
        Vec2: Ponto de interseção
        Vec2: Normal da superfície atingida
        """
        origin_array = np.array([origin.x, origin.y], dtype=np.float64)
        direction_array = np.array([direction.x, direction.y], dtype=np.float64)

        closest_collider = None
        closest_point = None
        closest_normal = None
        closest_distance = max_distance

        # Itera sobre todos os colliders
        for collider in Collider.colliders:
            if collider.mask & mask == 0:
                continue

            for polygon in collider.polygons:
                polygon = polygon.apply_transform(collider.word_position)
                intersection, normal, distance = _ray_polygon_intersection_numba(origin_array, direction_array,
                                                                                 polygon.vertices, max_distance)

                if intersection is not None and distance < closest_distance:
                    closest_collider = collider
                    closest_point = Vec2(intersection[0], intersection[1])
                    closest_normal = Vec2(normal[0], normal[1])
                    closest_distance = distance

        if closest_collider:
            if np.dot(closest_normal.to_tuple, direction_array) > 0:
                closest_normal *= -1
            return closest_collider, closest_point, closest_normal

        return None


@njit
def _ray_polygon_intersection_numba(origin: np.ndarray, direction: np.ndarray, vertices: np.ndarray,
                                    max_distance: float):
    closest_intersection = None
    closest_normal = None
    closest_distance = max_distance

    num_vertices = len(vertices)

    for i in prange(num_vertices):
        v1 = vertices[i]
        v2 = vertices[(i + 1) % num_vertices]

        edge = v2 - v1
        edge_normal = np.array([-edge[1], edge[0]])  # Normal ortogonal à aresta

        # Calcular a interseção do raio com a aresta (v1, v2)
        denom = np.dot(direction, edge_normal)
        if np.abs(denom) < 1e-6:  # Raio é paralelo à aresta
            continue

        t = np.dot(v1 - origin, edge_normal) / denom
        if t < 0 or t > max_distance:  # Interseção acontece fora do alcance ou atrás do raio continue
            continue

        intersection_point = origin + direction * t

        # Verifica se o ponto de interseção está dentro dos limites da aresta
        edge_direction = (v2 - v1) / np.linalg.norm(v2 - v1)
        proj = np.dot(intersection_point - v1, edge_direction)
        if proj < 0 or proj > np.linalg.norm(v2 - v1):
            continue

        if t < closest_distance:
            closest_distance = t
            closest_intersection = intersection_point
            closest_normal = edge_normal / np.linalg.norm(edge_normal)  # Normalizar

    return closest_intersection, closest_normal, closest_distance


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

# Teste
