# modules/protocol_security_enhancement.py
"""
SISTEMA DE SEGURIDAD Y VALIDACIÓN AVANZADA PARA PROTOCOLO UNIVERSAL OFICIAL
===========================================================================

Sistema completo de seguridad, validación y protección para el protocolo universal oficial.
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

@dataclass
class SecurityValidation:
    """Resultado de validación de seguridad."""
    validation_id: str
    validation_type: str
    passed: bool
    confidence_score: float
    details: Dict[str, Any]
    timestamp: datetime
    recommendations: List[str]

@dataclass
class AccessControl:
    """Control de acceso para operaciones del protocolo."""
    user_id: str
    permission_level: str
    allowed_operations: List[str]
    expiration_time: Optional[datetime]
    restrictions: Dict[str, Any]

@dataclass
class SecurityAudit:
    """Auditoría de seguridad."""
    audit_id: str
    operation: str
    user_id: str
    timestamp: datetime
    success: bool
    details: Dict[str, Any]
    risk_level: str

class ProtocolSecurityEnhancement:
    """
    Sistema de seguridad y validación avanzada para el protocolo universal oficial.
    """
    
    def __init__(self):
        """Inicializa el sistema de seguridad."""
        self.security_config_dir = Path("security_config")
        self.security_config_dir.mkdir(exist_ok=True)
        
        # Configuración de seguridad
        self.security_config = self._load_security_config()
        
        # Almacenamiento de validaciones y auditorías
        self.security_validations: List[SecurityValidation] = []
        self.access_controls: Dict[str, AccessControl] = {}
        self.security_audits: List[SecurityAudit] = []
        
        # Claves de encriptación
        self.encryption_key = self._generate_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        
        # Configuración de validaciones
        self.validation_rules = self._load_validation_rules()
        
        logger.info("Sistema de Seguridad del Protocolo inicializado")
    
    def validate_user_permissions(self, user_id: str, operation: str) -> SecurityValidation:
        """
        Valida permisos de usuario para una operación específica.
        
        Args:
            user_id: ID del usuario
            operation: Operación a realizar
            
        Returns:
            Resultado de validación de seguridad
        """
        try:
            validation_id = f"perm_{user_id}_{operation}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Verificar si el usuario tiene control de acceso
            access_control = self.access_controls.get(user_id)
            
            if not access_control:
                # Usuario no registrado - denegar acceso
                validation = SecurityValidation(
                    validation_id=validation_id,
                    validation_type="user_permissions",
                    passed=False,
                    confidence_score=0.0,
                    details={
                        "user_id": user_id,
                        "operation": operation,
                        "reason": "user_not_registered"
                    },
                    timestamp=datetime.now(),
                    recommendations=["Registrar usuario en sistema de acceso"]
                )
            else:
                # Verificar permisos
                if operation in access_control.allowed_operations:
                    # Verificar expiración
                    if access_control.expiration_time and datetime.now() > access_control.expiration_time:
                        validation = SecurityValidation(
                            validation_id=validation_id,
                            validation_type="user_permissions",
                            passed=False,
                            confidence_score=0.0,
                            details={
                                "user_id": user_id,
                                "operation": operation,
                                "reason": "access_expired"
                            },
                            timestamp=datetime.now(),
                            recommendations=["Renovar permisos de acceso"]
                        )
                    else:
                        # Acceso autorizado
                        validation = SecurityValidation(
                            validation_id=validation_id,
                            validation_type="user_permissions",
                            passed=True,
                            confidence_score=0.9,
                            details={
                                "user_id": user_id,
                                "operation": operation,
                                "permission_level": access_control.permission_level,
                                "expiration_time": access_control.expiration_time.isoformat() if access_control.expiration_time else None
                            },
                            timestamp=datetime.now(),
                            recommendations=[]
                        )
                else:
                    # Operación no permitida
                    validation = SecurityValidation(
                        validation_id=validation_id,
                        validation_type="user_permissions",
                        passed=False,
                        confidence_score=0.0,
                        details={
                            "user_id": user_id,
                            "operation": operation,
                            "reason": "operation_not_allowed",
                            "allowed_operations": access_control.allowed_operations
                        },
                        timestamp=datetime.now(),
                        recommendations=["Solicitar permisos adicionales para esta operación"]
                    )
            
            # Agregar a historial de validaciones
            self.security_validations.append(validation)
            
            # Registrar auditoría
            self._log_security_audit(user_id, operation, validation.passed, validation.details)
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validando permisos de usuario: {e}")
            return SecurityValidation(
                validation_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                validation_type="user_permissions",
                passed=False,
                confidence_score=0.0,
                details={"error": str(e)},
                timestamp=datetime.now(),
                recommendations=["Revisar configuración de seguridad"]
            )
    
    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encripta datos sensibles.
        
        Args:
            data: Datos a encriptar
            
        Returns:
            Datos encriptados
        """
        try:
            # Convertir datos a JSON string
            json_data = json.dumps(data, default=str)
            
            # Encriptar
            encrypted_data = self.fernet.encrypt(json_data.encode())
            
            # Codificar en base64 para almacenamiento
            encoded_data = base64.b64encode(encrypted_data).decode()
            
            return {
                "encrypted": True,
                "data": encoded_data,
                "encryption_timestamp": datetime.now().isoformat(),
                "encryption_method": "fernet"
            }
            
        except Exception as e:
            logger.error(f"Error encriptando datos: {e}")
            return {
                "encrypted": False,
                "error": str(e),
                "original_data": data
            }
    
    def decrypt_sensitive_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Desencripta datos sensibles.
        
        Args:
            encrypted_data: Datos encriptados
            
        Returns:
            Datos desencriptados
        """
        try:
            if not encrypted_data.get("encrypted", False):
                return encrypted_data
            
            # Decodificar de base64
            encoded_data = encrypted_data["data"]
            encrypted_bytes = base64.b64decode(encoded_data.encode())
            
            # Desencriptar
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            
            # Convertir de JSON string a dict
            original_data = json.loads(decrypted_data.decode())
            
            return {
                "decrypted": True,
                "data": original_data,
                "decryption_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error desencriptando datos: {e}")
            return {
                "decrypted": False,
                "error": str(e),
                "encrypted_data": encrypted_data
            }
    
    def validate_data_integrity(self, data: Dict[str, Any], expected_hash: str = None) -> SecurityValidation:
        """
        Valida integridad de datos.
        
        Args:
            data: Datos a validar
            expected_hash: Hash esperado (opcional)
            
        Returns:
            Resultado de validación de integridad
        """
        try:
            validation_id = f"integrity_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Calcular hash de los datos
            json_data = json.dumps(data, sort_keys=True, default=str)
            data_hash = hashlib.sha256(json_data.encode()).hexdigest()
            
            # Validar estructura de datos
            structure_valid = self._validate_data_structure(data)
            
            # Validar tipos de datos
            types_valid = self._validate_data_types(data)
            
            # Validar rangos de valores
            ranges_valid = self._validate_data_ranges(data)
            
            # Calcular puntuación de confianza
            confidence_score = 0.0
            if structure_valid:
                confidence_score += 0.4
            if types_valid:
                confidence_score += 0.3
            if ranges_valid:
                confidence_score += 0.3
            
            # Verificar hash si se proporciona
            hash_valid = True
            if expected_hash:
                hash_valid = data_hash == expected_hash
                if hash_valid:
                    confidence_score += 0.1
            
            validation = SecurityValidation(
                validation_id=validation_id,
                validation_type="data_integrity",
                passed=structure_valid and types_valid and ranges_valid and hash_valid,
                confidence_score=min(confidence_score, 1.0),
                details={
                    "data_hash": data_hash,
                    "expected_hash": expected_hash,
                    "structure_valid": structure_valid,
                    "types_valid": types_valid,
                    "ranges_valid": ranges_valid,
                    "hash_valid": hash_valid
                },
                timestamp=datetime.now(),
                recommendations=self._generate_integrity_recommendations(
                    structure_valid, types_valid, ranges_valid, hash_valid
                )
            )
            
            # Agregar a historial
            self.security_validations.append(validation)
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validando integridad de datos: {e}")
            return SecurityValidation(
                validation_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                validation_type="data_integrity",
                passed=False,
                confidence_score=0.0,
                details={"error": str(e)},
                timestamp=datetime.now(),
                recommendations=["Revisar formato de datos"]
            )
    
    def validate_protocol_execution(self, execution_data: Dict[str, Any]) -> SecurityValidation:
        """
        Valida ejecución del protocolo.
        
        Args:
            execution_data: Datos de ejecución del protocolo
            
        Returns:
            Resultado de validación de ejecución
        """
        try:
            validation_id = f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Validar estructura de ejecución
            structure_valid = self._validate_execution_structure(execution_data)
            
            # Validar secuencia de pasos
            sequence_valid = self._validate_step_sequence(execution_data)
            
            # Validar tiempos de ejecución
            timing_valid = self._validate_execution_timing(execution_data)
            
            # Validar resultados
            results_valid = self._validate_execution_results(execution_data)
            
            # Calcular puntuación de confianza
            confidence_score = 0.0
            if structure_valid:
                confidence_score += 0.3
            if sequence_valid:
                confidence_score += 0.3
            if timing_valid:
                confidence_score += 0.2
            if results_valid:
                confidence_score += 0.2
            
            validation = SecurityValidation(
                validation_id=validation_id,
                validation_type="protocol_execution",
                passed=structure_valid and sequence_valid and timing_valid and results_valid,
                confidence_score=confidence_score,
                details={
                    "structure_valid": structure_valid,
                    "sequence_valid": sequence_valid,
                    "timing_valid": timing_valid,
                    "results_valid": results_valid,
                    "execution_id": execution_data.get("execution_id"),
                    "lottery_type": execution_data.get("lottery_type")
                },
                timestamp=datetime.now(),
                recommendations=self._generate_execution_recommendations(
                    structure_valid, sequence_valid, timing_valid, results_valid
                )
            )
            
            # Agregar a historial
            self.security_validations.append(validation)
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validando ejecución del protocolo: {e}")
            return SecurityValidation(
                validation_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                validation_type="protocol_execution",
                passed=False,
                confidence_score=0.0,
                details={"error": str(e)},
                timestamp=datetime.now(),
                recommendations=["Revisar datos de ejecución"]
            )
    
    def create_access_control(self, user_id: str, permission_level: str, 
                            allowed_operations: List[str], expiration_hours: int = 24) -> AccessControl:
        """
        Crea control de acceso para un usuario.
        
        Args:
            user_id: ID del usuario
            permission_level: Nivel de permisos
            allowed_operations: Operaciones permitidas
            expiration_hours: Horas hasta expiración
            
        Returns:
            Control de acceso creado
        """
        try:
            expiration_time = datetime.now() + timedelta(hours=expiration_hours)
            
            access_control = AccessControl(
                user_id=user_id,
                permission_level=permission_level,
                allowed_operations=allowed_operations,
                expiration_time=expiration_time,
                restrictions={}
            )
            
            # Agregar a controles de acceso
            self.access_controls[user_id] = access_control
            
            # Registrar auditoría
            self._log_security_audit(
                user_id, 
                "create_access_control", 
                True, 
                {"permission_level": permission_level, "operations": allowed_operations}
            )
            
            logger.info(f"Control de acceso creado para usuario {user_id}")
            return access_control
            
        except Exception as e:
            logger.error(f"Error creando control de acceso: {e}")
            raise
    
    def revoke_access_control(self, user_id: str) -> bool:
        """
        Revoca control de acceso de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si se revocó exitosamente
        """
        try:
            if user_id in self.access_controls:
                del self.access_controls[user_id]
                
                # Registrar auditoría
                self._log_security_audit(user_id, "revoke_access_control", True, {})
                
                logger.info(f"Control de acceso revocado para usuario {user_id}")
                return True
            else:
                logger.warning(f"Usuario {user_id} no tiene control de acceso")
                return False
                
        except Exception as e:
            logger.error(f"Error revocando control de acceso: {e}")
            return False
    
    def get_security_report(self) -> Dict[str, Any]:
        """
        Genera reporte de seguridad.
        
        Returns:
            Reporte completo de seguridad
        """
        try:
            # Calcular estadísticas de validaciones
            total_validations = len(self.security_validations)
            passed_validations = sum(1 for v in self.security_validations if v.passed)
            validation_success_rate = passed_validations / total_validations if total_validations > 0 else 0
            
            # Calcular estadísticas de auditorías
            total_audits = len(self.security_audits)
            successful_audits = sum(1 for a in self.security_audits if a.success)
            audit_success_rate = successful_audits / total_audits if total_audits > 0 else 0
            
            # Identificar riesgos
            risk_analysis = self._analyze_security_risks()
            
            # Generar recomendaciones
            recommendations = self._generate_security_recommendations(risk_analysis)
            
            security_report = {
                "report_timestamp": datetime.now().isoformat(),
                "validation_statistics": {
                    "total_validations": total_validations,
                    "passed_validations": passed_validations,
                    "success_rate": validation_success_rate
                },
                "audit_statistics": {
                    "total_audits": total_audits,
                    "successful_audits": successful_audits,
                    "success_rate": audit_success_rate
                },
                "access_controls": {
                    "total_users": len(self.access_controls),
                    "active_controls": len([ac for ac in self.access_controls.values() 
                                          if not ac.expiration_time or ac.expiration_time > datetime.now()])
                },
                "risk_analysis": risk_analysis,
                "recommendations": recommendations,
                "security_status": "secure" if validation_success_rate > 0.9 and audit_success_rate > 0.9 else "needs_attention"
            }
            
            return security_report
            
        except Exception as e:
            logger.error(f"Error generando reporte de seguridad: {e}")
            return {"error": str(e)}
    
    def _load_security_config(self) -> Dict[str, Any]:
        """Carga configuración de seguridad."""
        try:
            config_file = self.security_config_dir / "security_config.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Configuración por defecto
                default_config = {
                    "encryption_enabled": True,
                    "validation_enabled": True,
                    "audit_enabled": True,
                    "max_failed_attempts": 3,
                    "session_timeout_hours": 24,
                    "password_policy": {
                        "min_length": 8,
                        "require_uppercase": True,
                        "require_lowercase": True,
                        "require_numbers": True,
                        "require_special_chars": True
                    }
                }
                
                # Guardar configuración por defecto
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
                
                return default_config
                
        except Exception as e:
            logger.error(f"Error cargando configuración de seguridad: {e}")
            return {}
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Carga reglas de validación."""
        try:
            rules_file = self.security_config_dir / "validation_rules.json"
            
            if rules_file.exists():
                with open(rules_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Reglas por defecto
                default_rules = {
                    "execution_structure": {
                        "required_fields": ["execution_id", "lottery_type", "steps", "success_rate"],
                        "field_types": {
                            "execution_id": "string",
                            "lottery_type": "string",
                            "success_rate": "number"
                        }
                    },
                    "step_sequence": {
                        "min_steps": 1,
                        "max_steps": 9,
                        "required_steps": ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                    },
                    "timing_validation": {
                        "max_total_duration": 3600,  # 1 hora
                        "min_step_duration": 1,      # 1 segundo
                        "max_step_duration": 300     # 5 minutos
                    }
                }
                
                # Guardar reglas por defecto
                with open(rules_file, 'w', encoding='utf-8') as f:
                    json.dump(default_rules, f, indent=2)
                
                return default_rules
                
        except Exception as e:
            logger.error(f"Error cargando reglas de validación: {e}")
            return {}
    
    def _generate_encryption_key(self) -> bytes:
        """Genera clave de encriptación."""
        try:
            key_file = self.security_config_dir / "encryption.key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Generar nueva clave
                key = Fernet.generate_key()
                
                # Guardar clave
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                return key
                
        except Exception as e:
            logger.error(f"Error generando clave de encriptación: {e}")
            return Fernet.generate_key()
    
    def _validate_data_structure(self, data: Dict[str, Any]) -> bool:
        """Valida estructura de datos."""
        try:
            # Validaciones básicas de estructura
            if not isinstance(data, dict):
                return False
            
            # Validar que no esté vacío
            if not data:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_data_types(self, data: Dict[str, Any]) -> bool:
        """Valida tipos de datos."""
        try:
            # Validar tipos básicos
            for key, value in data.items():
                if not isinstance(key, str):
                    return False
                
                # Validar que el valor sea serializable
                json.dumps(value, default=str)
            
            return True
            
        except Exception:
            return False
    
    def _validate_data_ranges(self, data: Dict[str, Any]) -> bool:
        """Valida rangos de valores."""
        try:
            # Validar rangos específicos
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    # Validar que no sea infinito o NaN
                    if not (float('-inf') < value < float('inf')):
                        return False
                
                elif isinstance(value, str):
                    # Validar longitud de strings
                    if len(value) > 10000:  # Límite de 10KB por string
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_execution_structure(self, execution_data: Dict[str, Any]) -> bool:
        """Valida estructura de ejecución."""
        try:
            rules = self.validation_rules.get("execution_structure", {})
            required_fields = rules.get("required_fields", [])
            
            # Verificar campos requeridos
            for field in required_fields:
                if field not in execution_data:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_step_sequence(self, execution_data: Dict[str, Any]) -> bool:
        """Valida secuencia de pasos."""
        try:
            rules = self.validation_rules.get("step_sequence", {})
            required_steps = rules.get("required_steps", [])
            
            steps_data = execution_data.get("steps", {})
            
            # Verificar que todos los pasos requeridos estén presentes
            for step in required_steps:
                if step not in steps_data:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_execution_timing(self, execution_data: Dict[str, Any]) -> bool:
        """Valida tiempos de ejecución."""
        try:
            rules = self.validation_rules.get("timing_validation", {})
            max_total_duration = rules.get("max_total_duration", 3600)
            min_step_duration = rules.get("min_step_duration", 1)
            max_step_duration = rules.get("max_step_duration", 300)
            
            # Validar duración total
            total_duration = execution_data.get("total_duration_seconds", 0)
            if total_duration > max_total_duration:
                return False
            
            # Validar duraciones de pasos
            steps_data = execution_data.get("steps", {})
            for step_data in steps_data.values():
                step_duration = step_data.get("duration_seconds", 0)
                if step_duration < min_step_duration or step_duration > max_step_duration:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_execution_results(self, execution_data: Dict[str, Any]) -> bool:
        """Valida resultados de ejecución."""
        try:
            # Validar que haya resultados
            if "results" not in execution_data:
                return False
            
            # Validar que los resultados no estén vacíos
            results = execution_data["results"]
            if not results:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _generate_integrity_recommendations(self, structure_valid: bool, types_valid: bool, 
                                          ranges_valid: bool, hash_valid: bool) -> List[str]:
        """Genera recomendaciones de integridad."""
        recommendations = []
        
        if not structure_valid:
            recommendations.append("Revisar estructura de datos")
        
        if not types_valid:
            recommendations.append("Verificar tipos de datos")
        
        if not ranges_valid:
            recommendations.append("Validar rangos de valores")
        
        if not hash_valid:
            recommendations.append("Verificar integridad de hash")
        
        return recommendations
    
    def _generate_execution_recommendations(self, structure_valid: bool, sequence_valid: bool,
                                          timing_valid: bool, results_valid: bool) -> List[str]:
        """Genera recomendaciones de ejecución."""
        recommendations = []
        
        if not structure_valid:
            recommendations.append("Revisar estructura de ejecución")
        
        if not sequence_valid:
            recommendations.append("Verificar secuencia de pasos")
        
        if not timing_valid:
            recommendations.append("Optimizar tiempos de ejecución")
        
        if not results_valid:
            recommendations.append("Revisar resultados de ejecución")
        
        return recommendations
    
    def _analyze_security_risks(self) -> Dict[str, Any]:
        """Analiza riesgos de seguridad."""
        try:
            risks = {
                "high_risk": [],
                "medium_risk": [],
                "low_risk": []
            }
            
            # Analizar validaciones fallidas recientes
            recent_validations = [v for v in self.security_validations 
                                if (datetime.now() - v.timestamp).total_seconds() < 3600]  # Última hora
            
            failed_validations = [v for v in recent_validations if not v.passed]
            
            if len(failed_validations) > 5:
                risks["high_risk"].append("Alto número de validaciones fallidas en la última hora")
            
            # Analizar controles de acceso expirados
            expired_controls = [ac for ac in self.access_controls.values() 
                              if ac.expiration_time and ac.expiration_time < datetime.now()]
            
            if len(expired_controls) > 0:
                risks["medium_risk"].append(f"{len(expired_controls)} controles de acceso expirados")
            
            # Analizar auditorías fallidas
            recent_audits = [a for a in self.security_audits 
                           if (datetime.now() - a.timestamp).total_seconds() < 3600]
            
            failed_audits = [a for a in recent_audits if not a.success]
            
            if len(failed_audits) > 3:
                risks["medium_risk"].append("Múltiples auditorías fallidas recientes")
            
            return risks
            
        except Exception as e:
            logger.error(f"Error analizando riesgos: {e}")
            return {"error": str(e)}
    
    def _generate_security_recommendations(self, risk_analysis: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones de seguridad."""
        recommendations = []
        
        high_risks = risk_analysis.get("high_risk", [])
        medium_risks = risk_analysis.get("medium_risk", [])
        
        if high_risks:
            recommendations.append("REVISIÓN INMEDIATA REQUERIDA: Riesgos de seguridad altos detectados")
            recommendations.extend([f"- {risk}" for risk in high_risks])
        
        if medium_risks:
            recommendations.append("Atención requerida: Riesgos de seguridad medios detectados")
            recommendations.extend([f"- {risk}" for risk in medium_risks])
        
        if not high_risks and not medium_risks:
            recommendations.append("Sistema de seguridad funcionando correctamente")
        
        return recommendations
    
    def _log_security_audit(self, user_id: str, operation: str, success: bool, details: Dict[str, Any]):
        """Registra auditoría de seguridad."""
        try:
            audit = SecurityAudit(
                audit_id=f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                operation=operation,
                user_id=user_id,
                timestamp=datetime.now(),
                success=success,
                details=details,
                risk_level="high" if not success else "low"
            )
            
            self.security_audits.append(audit)
            
            # Mantener solo las últimas 1000 auditorías
            if len(self.security_audits) > 1000:
                self.security_audits = self.security_audits[-1000:]
                
        except Exception as e:
            logger.error(f"Error registrando auditoría: {e}")


# =================== INSTANCIA GLOBAL ===================

# Instancia global del sistema de seguridad
protocol_security_enhancement = ProtocolSecurityEnhancement()

def get_security_enhancement() -> ProtocolSecurityEnhancement:
    """Obtiene la instancia global del sistema de seguridad."""
    return protocol_security_enhancement






