# modules/protocol_vetting_system.py
"""
SISTEMA DE VETADO DE PROTOCOLOS
===============================

Este sistema veta todos los protocolos que no sean el protocolo universal oficial
para evitar errores y confusión futura en Vision App.

PROTOCOLOS VETADOS:
- sorteo_protocol.py (protocolo anterior)
- universal_protocol.py (protocolo anterior)
- Cualquier otro protocolo no autorizado

PROTOCOLO AUTORIZADO:
- universal_protocol_official.py (ÚNICO protocolo oficial)
"""

import logging
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ProtocolVettingSystem:
    """
    Sistema de vetado de protocolos para Vision App.
    
    Este sistema asegura que solo el protocolo universal oficial
    sea utilizado en la aplicación.
    """
    
    def __init__(self):
        """Inicializa el sistema de vetado."""
        self.authorized_protocols = {
            "universal_protocol_official": {
                "name": "PROTOCOLO UNIVERSAL OFICIAL DE VISION APP",
                "version": "1.0",
                "status": "AUTHORIZED",
                "file": "modules/universal_protocol_official.py",
                "class": "UniversalProtocolOfficial",
                "description": "Único protocolo oficial autorizado para análisis de sorteos"
            }
        }
        
        self.vetted_protocols = [
            "sorteo_protocol",
            "universal_protocol", 
            "lottery_protocol",
            "powerball_protocol",
            "megamillions_protocol",
            "europrotocol",
            "any_other_protocol"
        ]
        
        logger.info("Sistema de Vetado de Protocolos inicializado")
    
    def check_protocol_authorization(self, protocol_name: str) -> Dict[str, Any]:
        """
        Verifica si un protocolo está autorizado.
        
        Args:
            protocol_name: Nombre del protocolo a verificar
            
        Returns:
            Dict con resultado de la verificación
        """
        try:
            if protocol_name in self.vetted_protocols:
                return {
                    "authorized": False,
                    "status": "VETTED",
                    "message": f"PROTOCOLO VETADO: {protocol_name} no está autorizado. Use 'universal_protocol_official'",
                    "recommendation": "Use 'universal_protocol_official' como único protocolo autorizado"
                }
            
            if protocol_name in self.authorized_protocols:
                return {
                    "authorized": True,
                    "status": "AUTHORIZED",
                    "message": f"PROTOCOLO AUTORIZADO: {protocol_name} está permitido",
                    "details": self.authorized_protocols[protocol_name]
                }
            
            # Protocolo desconocido
            return {
                "authorized": False,
                "status": "UNKNOWN",
                "message": f"PROTOCOLO DESCONOCIDO: {protocol_name} no está registrado",
                "recommendation": "Use 'universal_protocol_official' como único protocolo autorizado"
            }
            
        except Exception as e:
            return {
                "authorized": False,
                "status": "ERROR",
                "message": f"Error verificando protocolo: {str(e)}",
                "recommendation": "Use 'universal_protocol_official' como único protocolo autorizado"
            }
    
    def get_authorized_protocol(self, protocol_name: str = "universal_protocol_official"):
        """
        Obtiene el protocolo autorizado.
        
        Args:
            protocol_name: Nombre del protocolo (solo "universal_protocol_official" está autorizado)
            
        Returns:
            Instancia del protocolo autorizado
            
        Raises:
            ValueError: Si se intenta usar un protocolo vetado
        """
        verification = self.check_protocol_authorization(protocol_name)
        
        if not verification["authorized"]:
            raise ValueError(verification["message"])
        
        # Importar y retornar el protocolo autorizado
        try:
            from modules.universal_protocol_official import UniversalProtocolOfficial
            return UniversalProtocolOfficial()
        except ImportError as e:
            raise ImportError(f"No se pudo importar el protocolo autorizado: {str(e)}")
    
    def list_authorized_protocols(self) -> Dict[str, Any]:
        """Lista todos los protocolos autorizados."""
        return {
            "authorized_protocols": self.authorized_protocols,
            "vetted_protocols": self.vetted_protocols,
            "total_authorized": len(self.authorized_protocols),
            "total_vetted": len(self.vetted_protocols),
            "message": "Solo 'universal_protocol_official' está autorizado. Todos los demás protocolos están vetados."
        }
    
    def vet_protocol(self, protocol_name: str, reason: str = "No autorizado") -> Dict[str, Any]:
        """
        Veta un protocolo específico.
        
        Args:
            protocol_name: Nombre del protocolo a vetar
            reason: Razón del vetado
            
        Returns:
            Dict con resultado del vetado
        """
        try:
            if protocol_name not in self.vetted_protocols:
                self.vetted_protocols.append(protocol_name)
            
            logger.warning(f"PROTOCOLO VETADO: {protocol_name} - Razón: {reason}")
            
            return {
                "vetting_successful": True,
                "protocol_name": protocol_name,
                "reason": reason,
                "status": "VETTED",
                "message": f"Protocolo {protocol_name} ha sido vetado exitosamente"
            }
            
        except Exception as e:
            return {
                "vetting_successful": False,
                "error": str(e),
                "message": f"Error vetando protocolo {protocol_name}"
            }
    
    def check_file_protocols(self) -> Dict[str, Any]:
        """
        Verifica archivos de protocolos en el sistema.
        
        Returns:
            Dict con estado de todos los archivos de protocolos
        """
        try:
            modules_dir = Path("modules")
            protocol_files = {}
            
            # Buscar archivos de protocolos
            for file_path in modules_dir.glob("*protocol*.py"):
                file_name = file_path.stem
                
                if file_name == "universal_protocol_official":
                    protocol_files[file_name] = {
                        "status": "AUTHORIZED",
                        "file_path": str(file_path),
                        "authorized": True
                    }
                elif any(vetted in file_name for vetted in self.vetted_protocols):
                    protocol_files[file_name] = {
                        "status": "VETTED",
                        "file_path": str(file_path),
                        "authorized": False,
                        "warning": "Este protocolo está vetado y no debe ser usado"
                    }
                else:
                    protocol_files[file_name] = {
                        "status": "UNKNOWN",
                        "file_path": str(file_path),
                        "authorized": False,
                        "warning": "Protocolo desconocido - debe ser vetado"
                    }
            
            return {
                "protocol_files_found": len(protocol_files),
                "files": protocol_files,
                "summary": {
                    "authorized": sum(1 for f in protocol_files.values() if f["authorized"]),
                    "vetted": sum(1 for f in protocol_files.values() if f["status"] == "VETTED"),
                    "unknown": sum(1 for f in protocol_files.values() if f["status"] == "UNKNOWN")
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "message": "Error verificando archivos de protocolos"
            }
    
    def enforce_protocol_vetting(self) -> Dict[str, Any]:
        """
        Ejecuta el sistema de vetado completo.
        
        Returns:
            Dict con resultado del enforcement
        """
        try:
            # Verificar archivos de protocolos
            file_check = self.check_file_protocols()
            
            # Verificar protocolos autorizados
            authorized_check = self.list_authorized_protocols()
            
            # Generar reporte de enforcement
            enforcement_report = {
                "enforcement_successful": True,
                "timestamp": "2024-01-01T00:00:00",  # Se actualizará con datetime real
                "file_check": file_check,
                "authorized_protocols": authorized_check,
                "recommendations": []
            }
            
            # Agregar recomendaciones
            if file_check.get("summary", {}).get("unknown", 0) > 0:
                enforcement_report["recommendations"].append(
                    "Vetar protocolos desconocidos encontrados"
                )
            
            if file_check.get("summary", {}).get("vetted", 0) > 0:
                enforcement_report["recommendations"].append(
                    "Confirmar que protocolos vetados no se están usando"
                )
            
            logger.info("Sistema de vetado de protocolos ejecutado exitosamente")
            
            return enforcement_report
            
        except Exception as e:
            return {
                "enforcement_successful": False,
                "error": str(e),
                "message": "Error ejecutando sistema de vetado"
            }


# =================== INSTANCIA GLOBAL DEL SISTEMA ===================

# Instancia global del sistema de vetado
protocol_vetting_system = ProtocolVettingSystem()

def get_authorized_protocol(protocol_name: str = "universal_protocol_official"):
    """
    Función global para obtener protocolo autorizado.
    
    Args:
        protocol_name: Nombre del protocolo (solo "universal_protocol_official" está autorizado)
        
    Returns:
        Instancia del protocolo autorizado
        
    Raises:
        ValueError: Si se intenta usar un protocolo vetado
    """
    return protocol_vetting_system.get_authorized_protocol(protocol_name)

def check_protocol_authorization(protocol_name: str):
    """
    Función global para verificar autorización de protocolo.
    
    Args:
        protocol_name: Nombre del protocolo a verificar
        
    Returns:
        Dict con resultado de la verificación
    """
    return protocol_vetting_system.check_protocol_authorization(protocol_name)

def list_authorized_protocols():
    """Función global para listar protocolos autorizados."""
    return protocol_vetting_system.list_authorized_protocols()

def enforce_protocol_vetting():
    """Función global para ejecutar sistema de vetado."""
    return protocol_vetting_system.enforce_protocol_vetting()







