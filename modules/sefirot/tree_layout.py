# modules/sefirot/tree_layout.py
"""
Layout y estructura del Árbol de la Vida para visualización
Coordenadas, senderos y organización espacial de las Sefirot
"""

from typing import Dict, List, Tuple, Any
import networkx as nx
from .constants import SEFIROT, SENDEROS

def get_tree_coordinates() -> Dict[int, Tuple[float, float]]:
    """
    Obtiene las coordenadas (x, y) de todas las Sefirot para visualización.
    
    Returns:
        Diccionario con coordenadas por número de Sefirá
    """
    return {sefira_num: sefira_info.coordenadas 
            for sefira_num, sefira_info in SEFIROT.items()}

def create_tree_graph() -> nx.Graph:
    """
    Crea un grafo de NetworkX representando el Árbol de la Vida.
    
    Returns:
        Grafo con nodos (Sefirot) y aristas (senderos)
    """
    G = nx.Graph()
    
    # Agregar nodos (Sefirot)
    for sefira_num, sefira_info in SEFIROT.items():
        G.add_node(
            sefira_num,
            nombre=sefira_info.nombre,
            pilar=sefira_info.pilar,
            energia=sefira_info.energia,
            color=sefira_info.color,
            coordenadas=sefira_info.coordenadas,
            peso_base=sefira_info.peso_base
        )
    
    # Agregar aristas (senderos)
    for sefira_a, sefira_b in SENDEROS:
        G.add_edge(sefira_a, sefira_b)
    
    return G

def get_senderos_info() -> List[Dict[str, Any]]:
    """
    Obtiene información detallada de todos los senderos.
    
    Returns:
        Lista de diccionarios con información de cada sendero
    """
    senderos_info = []
    
    for sefira_a, sefira_b in SENDEROS:
        sefira_a_info = SEFIROT[sefira_a]
        sefira_b_info = SEFIROT[sefira_b]
        
        senderos_info.append({
            "from_sefira": sefira_a,
            "to_sefira": sefira_b,
            "from_nombre": sefira_a_info.nombre,
            "to_nombre": sefira_b_info.nombre,
            "from_coords": sefira_a_info.coordenadas,
            "to_coords": sefira_b_info.coordenadas,
            "pilar_from": sefira_a_info.pilar,
            "pilar_to": sefira_b_info.pilar,
            "energia_from": sefira_a_info.energia,
            "energia_to": sefira_b_info.energia
        })
    
    return senderos_info

def calculate_sendero_length(sefira_a: int, sefira_b: int) -> float:
    """
    Calcula la longitud de un sendero entre dos Sefirot.
    
    Args:
        sefira_a: Número de la primera Sefirá
        sefira_b: Número de la segunda Sefirá
        
    Returns:
        Longitud euclidiana del sendero
    """
    coords_a = SEFIROT[sefira_a].coordenadas
    coords_b = SEFIROT[sefira_b].coordenadas
    
    return ((coords_a[0] - coords_b[0])**2 + (coords_a[1] - coords_b[1])**2)**0.5

def get_sefira_neighbors(sefira_num: int) -> List[int]:
    """
    Obtiene las Sefirot vecinas de una Sefirá específica.
    
    Args:
        sefira_num: Número de la Sefirá
        
    Returns:
        Lista de números de Sefirot vecinas
    """
    neighbors = []
    
    for sefira_a, sefira_b in SENDEROS:
        if sefira_a == sefira_num:
            neighbors.append(sefira_b)
        elif sefira_b == sefira_num:
            neighbors.append(sefira_a)
    
    return neighbors

def get_pilar_layout() -> Dict[str, List[Tuple[float, float]]]:
    """
    Obtiene las coordenadas agrupadas por pilar.
    
    Returns:
        Diccionario con coordenadas por pilar
    """
    from .constants import PILARES
    
    layout = {}
    
    for pilar, sefirot_list in PILARES.items():
        coords = []
        for sefira_num in sefirot_list:
            coords.append(SEFIROT[sefira_num].coordenadas)
        layout[pilar] = coords
    
    return layout

def get_tree_bounds() -> Dict[str, float]:
    """
    Calcula los límites del Árbol de la Vida.
    
    Returns:
        Diccionario con límites min/max x/y
    """
    coords = get_tree_coordinates()
    x_coords = [coord[0] for coord in coords.values()]
    y_coords = [coord[1] for coord in coords.values()]
    
    return {
        "min_x": min(x_coords),
        "max_x": max(x_coords),
        "min_y": min(y_coords),
        "max_y": max(y_coords),
        "width": max(x_coords) - min(x_coords),
        "height": max(y_coords) - min(y_coords)
    }

def get_central_sefirot() -> List[int]:
    """
    Obtiene las Sefirot centrales del Árbol (Tiferet y sus vecinas).
    
    Returns:
        Lista de números de Sefirot centrales
    """
    return [6] + get_sefira_neighbors(6)  # Tiferet + sus vecinas

def get_superior_sefirot() -> List[int]:
    """
    Obtiene las Sefirot superiores del Árbol.
    
    Returns:
        Lista de números de Sefirot superiores
    """
    return [1, 2, 3]  # Keter, Chokmah, Binah

def get_inferior_sefirot() -> List[int]:
    """
    Obtiene las Sefirot inferiores del Árbol.
    
    Returns:
        Lista de números de Sefirot inferiores
    """
    return [7, 8, 9, 10]  # Netzach, Hod, Yesod, Malkuth

def get_vertical_paths() -> List[List[int]]:
    """
    Obtiene los caminos verticales principales del Árbol.
    
    Returns:
        Lista de caminos verticales
    """
    return [
        [1, 2, 4, 7, 10],  # Pilar derecho
        [1, 3, 5, 8, 9],   # Pilar izquierdo
        [1, 2, 6, 9]       # Pilar central
    ]

def get_horizontal_connections() -> List[Tuple[int, int]]:
    """
    Obtiene las conexiones horizontales del Árbol.
    
    Returns:
        Lista de pares de Sefirot conectadas horizontalmente
    """
    horizontal = []
    
    for sefira_a, sefira_b in SENDEROS:
        # Verificar si están en el mismo nivel (misma coordenada y)
        coords_a = SEFIROT[sefira_a].coordenadas
        coords_b = SEFIROT[sefira_b].coordenadas
        
        if abs(coords_a[1] - coords_b[1]) < 0.1:  # Mismo nivel
            horizontal.append((sefira_a, sefira_b))
    
    return horizontal

def get_tree_symmetry_axis() -> float:
    """
    Calcula el eje de simetría del Árbol de la Vida.
    
    Returns:
        Coordenada x del eje de simetría
    """
    coords = get_tree_coordinates()
    x_coords = [coord[0] for coord in coords.values()]
    return (min(x_coords) + max(x_coords)) / 2

def validate_tree_structure() -> bool:
    """
    Valida que la estructura del Árbol esté correctamente definida.
    
    Returns:
        True si la estructura es válida, False en caso contrario
    """
    try:
        # Verificar que todas las Sefirot tengan coordenadas
        for sefira_num in SEFIROT:
            coords = SEFIROT[sefira_num].coordenadas
            if not isinstance(coords, tuple) or len(coords) != 2:
                return False
            if not all(isinstance(x, (int, float)) for x in coords):
                return False
        
        # Verificar que todos los senderos conecten Sefirot válidas
        for sefira_a, sefira_b in SENDEROS:
            if sefira_a not in SEFIROT or sefira_b not in SEFIROT:
                return False
        
        # Verificar que el grafo sea conexo
        G = create_tree_graph()
        if not nx.is_connected(G):
            return False
        
        return True
        
    except Exception:
        return False





