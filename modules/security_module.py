# modules/security_module.py
import hashlib
import hmac
import secrets
import base64
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import streamlit as st

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserRole:
    """Rol de usuario con permisos específicos."""
    name: str
    permissions: List[str]
    description: str
    created_at: datetime
    is_active: bool = True

@dataclass
class User:
    """Usuario del sistema con autenticación y autorización."""
    username: str
    email: str
    role: str
    password_hash: str
    salt: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None

@dataclass
class AccessLog:
    """Registro de acceso al sistema."""
    id: str
    username: str
    action: str
    resource: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    success: bool
    details: Dict[str, Any]

@dataclass
class SecurityEvent:
    """Evento de seguridad del sistema."""
    id: str
    event_type: str  # "login", "logout", "access_denied", "data_access", "admin_action"
    severity: str  # "low", "medium", "high", "critical"
    timestamp: datetime
    username: str
    description: str
    ip_address: str
    details: Dict[str, Any]
    resolved: bool = False

class SecurityModule:
    """Módulo de seguridad avanzada con cifrado y gestión de accesos."""
    
    def __init__(self):
        self.users = {}
        self.roles = {}
        self.access_logs = []
        self.security_events = []
        self.encryption_key = None
        self.session_tokens = {}
        self.rate_limits = {}
        
        # Inicializar roles por defecto
        self._initialize_default_roles()
        
        # Inicializar usuario admin por defecto
        self._initialize_admin_user()
    
    def _initialize_default_roles(self):
        """Inicializa roles por defecto del sistema."""
        admin_role = UserRole(
            name="admin",
            permissions=[
                "read_all", "write_all", "delete_all", "user_management",
                "system_config", "security_audit", "data_export"
            ],
            description="Administrador completo del sistema",
            created_at=datetime.now()
        )
        
        analyst_role = UserRole(
            name="analyst",
            permissions=[
                "read_news", "read_analysis", "read_results", "export_data"
            ],
            description="Analista con acceso a datos y resultados",
            created_at=datetime.now()
        )
        
        viewer_role = UserRole(
            name="viewer",
            permissions=[
                "read_news", "read_results"
            ],
            description="Visualizador con acceso limitado",
            created_at=datetime.now()
        )
        
        self.roles["admin"] = admin_role
        self.roles["analyst"] = analyst_role
        self.roles["viewer"] = viewer_role
    
    def _initialize_admin_user(self):
        """Inicializa usuario administrador por defecto."""
        admin_password = "admin123"  # Cambiar en producción
        salt = self._generate_salt()
        password_hash = self._hash_password(admin_password, salt)
        
        admin_user = User(
            username="admin",
            email="admin@vision.com",
            role="admin",
            password_hash=password_hash,
            salt=salt,
            created_at=datetime.now()
        )
        
        self.users["admin"] = admin_user
        logger.info("Usuario administrador inicializado")
    
    def _generate_salt(self, length: int = 32) -> str:
        """Genera un salt aleatorio para hashing de contraseñas."""
        return secrets.token_hex(length)
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Genera hash de contraseña usando PBKDF2."""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key.decode()
        except Exception as e:
            logger.error(f"Error hasheando contraseña: {e}")
            # Fallback simple
            return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verifica una contraseña contra su hash almacenado."""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key.decode() == stored_hash
        except Exception as e:
            logger.error(f"Error verificando contraseña: {e}")
            # Fallback simple
            expected_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return expected_hash == stored_hash
    
    def _generate_session_token(self, username: str) -> str:
        """Genera un token de sesión único."""
        token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=24)
        
        self.session_tokens[token] = {
            "username": username,
            "expires_at": expiry,
            "created_at": datetime.now()
        }
        
        return token
    
    def _validate_session_token(self, token: str) -> Optional[str]:
        """Valida un token de sesión y retorna el username."""
        if token not in self.session_tokens:
            return None
        
        session = self.session_tokens[token]
        if datetime.now() > session["expires_at"]:
            del self.session_tokens[token]
            return None
        
        return session["username"]
    
    def _check_rate_limit(self, username: str, action: str) -> bool:
        """Verifica límites de tasa para prevenir ataques."""
        current_time = datetime.now()
        key = f"{username}:{action}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Limpiar entradas antiguas (últimos 5 minutos)
        cutoff = current_time - timedelta(minutes=5)
        self.rate_limits[key] = [t for t in self.rate_limits[key] if t > cutoff]
        
        # Verificar límite (máximo 10 intentos por 5 minutos)
        if len(self.rate_limits[key]) >= 10:
            return False
        
        self.rate_limits[key].append(current_time)
        return True
    
    def _log_access(self, username: str, action: str, resource: str, 
                    success: bool, ip_address: str = "unknown", 
                    user_agent: str = "unknown", details: Dict = None):
        """Registra un acceso al sistema."""
        access_log = AccessLog(
            id=str(len(self.access_logs) + 1),
            username=username,
            action=action,
            resource=resource,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details or {}
        )
        
        self.access_logs.append(access_log)
        
        # Mantener solo los últimos 1000 logs
        if len(self.access_logs) > 1000:
            self.access_logs = self.access_logs[-1000:]
    
    def _log_security_event(self, event_type: str, severity: str, username: str,
                           description: str, ip_address: str = "unknown", 
                           details: Dict = None):
        """Registra un evento de seguridad."""
        security_event = SecurityEvent(
            id=str(len(self.security_events) + 1),
            event_type=event_type,
            severity=severity,
            timestamp=datetime.now(),
            username=username,
            description=description,
            ip_address=ip_address,
            details=details or {}
        )
        
        self.security_events.append(security_event)
        
        # Mantener solo los últimos 500 eventos
        if len(self.security_events) > 500:
            self.security_events = self.security_events[-500:]
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = "unknown") -> Dict[str, Any]:
        """Autentica un usuario y retorna token de sesión."""
        try:
            # Verificar límites de tasa
            if not self._check_rate_limit(username, "login"):
                self._log_security_event(
                    "rate_limit_exceeded", "high", username,
                    "Límite de tasa excedido para login", ip_address
                )
                return {
                    "success": False,
                    "error": "Demasiados intentos de login. Intenta más tarde."
                }
            
            # Verificar si el usuario existe
            if username not in self.users:
                self._log_access(username, "login", "auth", False, ip_address)
                return {
                    "success": False,
                    "error": "Usuario o contraseña incorrectos"
                }
            
            user = self.users[username]
            
            # Verificar si la cuenta está bloqueada
            if user.locked_until and datetime.now() < user.locked_until:
                remaining_time = user.locked_until - datetime.now()
                self._log_access(username, "login", "auth", False, ip_address)
                return {
                    "success": False,
                    "error": f"Cuenta bloqueada. Intenta en {int(remaining_time.total_seconds() / 60)} minutos"
                }
            
            # Verificar contraseña
            if not self._verify_password(password, user.password_hash, user.salt):
                user.failed_attempts += 1
                
                # Bloquear cuenta después de 5 intentos fallidos
                if user.failed_attempts >= 5:
                    user.locked_until = datetime.now() + timedelta(minutes=30)
                    self._log_security_event(
                        "account_locked", "high", username,
                        "Cuenta bloqueada por múltiples intentos fallidos", ip_address
                    )
                
                self._log_access(username, "login", "auth", False, ip_address)
                return {
                    "success": False,
                    "error": "Usuario o contraseña incorrectos"
                }
            
            # Login exitoso
            user.failed_attempts = 0
            user.last_login = datetime.now()
            
            # Generar token de sesión
            session_token = self._generate_session_token(username)
            
            self._log_access(username, "login", "auth", True, ip_address)
            self._log_security_event(
                "login_success", "low", username,
                "Login exitoso", ip_address
            )
            
            return {
                "success": True,
                "session_token": session_token,
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "permissions": self.roles[user.role].permissions
                }
            }
            
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return {
                "success": False,
                "error": "Error interno del sistema"
            }
    
    def validate_access(self, session_token: str, resource: str, action: str) -> bool:
        """Valida si un usuario tiene acceso a un recurso."""
        try:
            username = self._validate_session_token(session_token)
            if not username:
                return False
            
            user = self.users[username]
            if not user.is_active:
                return False
            
            role = self.roles[user.role]
            if not role.is_active:
                return False
            
            # Verificar permisos
            required_permission = f"{action}_{resource}"
            if required_permission in role.permissions:
                return True
            
            # Verificar permisos generales
            if f"{action}_all" in role.permissions:
                return True
            
            # Verificar permisos de lectura para recursos específicos
            if action == "read" and "read_all" in role.permissions:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error validando acceso: {e}")
            return False
    
    def encrypt_data(self, data: Union[str, bytes, Dict]) -> Dict[str, str]:
        """Cifra datos sensibles."""
        try:
            if not self.encryption_key:
                # Generar nueva clave si no existe
                self.encryption_key = Fernet.generate_key()
            
            fernet = Fernet(self.encryption_key)
            
            if isinstance(data, dict):
                data_str = json.dumps(data)
            elif isinstance(data, bytes):
                data_str = data.decode('utf-8')
            else:
                data_str = str(data)
            
            encrypted_data = fernet.encrypt(data_str.encode())
            
            return {
                "encrypted_data": base64.urlsafe_b64encode(encrypted_data).decode(),
                "key_id": hashlib.sha256(self.encryption_key).hexdigest()[:16]
            }
            
        except Exception as e:
            logger.error(f"Error cifrando datos: {e}")
            return {"error": str(e)}
    
    def decrypt_data(self, encrypted_data: str, key_id: str) -> Union[str, Dict, None]:
        """Descifra datos previamente cifrados."""
        try:
            if not self.encryption_key:
                return None
            
            # Verificar que la clave coincida
            current_key_id = hashlib.sha256(self.encryption_key).hexdigest()[:16]
            if key_id != current_key_id:
                return None
            
            fernet = Fernet(self.encryption_key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
            decrypted_data = fernet.decrypt(encrypted_bytes)
            
            # Intentar parsear como JSON, si falla retornar como string
            try:
                return json.loads(decrypted_data.decode())
            except:
                return decrypted_data.decode()
                
        except Exception as e:
            logger.error(f"Error descifrando datos: {e}")
            return None
    
    def create_user(self, username: str, email: str, role: str, password: str,
                    admin_username: str = None) -> Dict[str, Any]:
        """Crea un nuevo usuario (solo admin)."""
        try:
            # Verificar permisos de admin
            if admin_username:
                admin_user = self.users.get(admin_username)
                if not admin_user or admin_user.role != "admin":
                    return {
                        "success": False,
                        "error": "Permisos insuficientes"
                    }
            
            # Verificar si el usuario ya existe
            if username in self.users:
                return {
                    "success": False,
                    "error": "El usuario ya existe"
                }
            
            # Verificar si el rol existe
            if role not in self.roles:
                return {
                    "success": False,
                    "error": "Rol inválido"
                }
            
            # Crear usuario
            salt = self._generate_salt()
            password_hash = self._hash_password(password, salt)
            
            new_user = User(
                username=username,
                email=email,
                role=role,
                password_hash=password_hash,
                salt=salt,
                created_at=datetime.now()
            )
            
            self.users[username] = new_user
            
            self._log_security_event(
                "user_created", "medium", admin_username or "system",
                f"Usuario {username} creado con rol {role}"
            )
            
            return {
                "success": True,
                "message": f"Usuario {username} creado exitosamente"
            }
            
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            return {
                "success": False,
                "error": "Error interno del sistema"
            }
    
    def get_security_report(self, admin_username: str) -> Dict[str, Any]:
        """Genera reporte de seguridad (solo admin)."""
        try:
            admin_user = self.users.get(admin_username)
            if not admin_user or admin_user.role != "admin":
                return {
                    "success": False,
                    "error": "Permisos insuficientes"
                }
            
            # Estadísticas de usuarios
            total_users = len(self.users)
            active_users = len([u for u in self.users.values() if u.is_active])
            locked_users = len([u for u in self.users.values() if u.locked_until and datetime.now() < u.locked_until])
            
            # Estadísticas de acceso
            total_logins = len([log for log in self.access_logs if log.action == "login"])
            successful_logins = len([log for log in self.access_logs if log.action == "login" and log.success])
            failed_logins = total_logins - successful_logins
            
            # Eventos de seguridad recientes
            recent_events = [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "severity": event.severity,
                    "username": event.username,
                    "description": event.description
                }
                for event in self.security_events[-20:]  # Últimos 20 eventos
            ]
            
            # Intentos de acceso sospechosos
            suspicious_ips = {}
            for log in self.access_logs[-100:]:  # Últimos 100 logs
                if not log.success:
                    if log.ip_address not in suspicious_ips:
                        suspicious_ips[log.ip_address] = 0
                    suspicious_ips[log.ip_address] += 1
            
            suspicious_ips = {ip: count for ip, count in suspicious_ips.items() if count > 5}
            
            return {
                "success": True,
                "report": {
                    "timestamp": datetime.now().isoformat(),
                    "user_statistics": {
                        "total_users": total_users,
                        "active_users": active_users,
                        "locked_users": locked_users
                    },
                    "access_statistics": {
                        "total_logins": total_logins,
                        "successful_logins": successful_logins,
                        "failed_logins": failed_logins,
                        "success_rate": (successful_logins / total_logins * 100) if total_logins > 0 else 0
                    },
                    "recent_security_events": recent_events,
                    "suspicious_ips": suspicious_ips
                }
            }
            
        except Exception as e:
            logger.error(f"Error generando reporte de seguridad: {e}")
            return {
                "success": False,
                "error": "Error interno del sistema"
            }
    
    def render_security_ui(self):
        """Renderiza la interfaz de seguridad en Streamlit."""
        st.subheader("🔐 **PANEL DE SEGURIDAD Y GESTIÓN DE ACCESOS**")
        
        # Tabs para diferentes funcionalidades
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔑 Autenticación", 
            "👥 Gestión de Usuarios", 
            "📊 Reportes de Seguridad",
            "🔍 Auditoría"
        ])
        
        with tab1:
            self._render_authentication_tab()
        
        with tab2:
            self._render_user_management_tab()
        
        with tab3:
            self._render_security_reports_tab()
        
        with tab4:
            self._render_audit_tab()
    
    def _render_authentication_tab(self):
        """Renderiza la pestaña de autenticación."""
        st.subheader("🔑 **Autenticación de Usuario**")
        
        # Formulario de login
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_button = st.form_submit_button("🔐 Iniciar Sesión", use_container_width=True)
            
            with col2:
                if st.form_submit_button("🆕 Crear Cuenta", use_container_width=True):
                    st.session_state["show_create_account"] = True
            
            if login_button and username and password:
                result = self.authenticate_user(username, password)
                if result["success"]:
                    st.session_state["session_token"] = result["session_token"]
                    st.session_state["current_user"] = result["user"]
                    st.success("✅ Login exitoso!")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
        
        # Mostrar usuario actual si está autenticado
        if "current_user" in st.session_state:
            st.success(f"✅ Autenticado como: **{st.session_state['current_user']['username']}** ({st.session_state['current_user']['role']})")
            
            if st.button("🚪 Cerrar Sesión"):
                del st.session_state["session_token"]
                del st.session_state["current_user"]
                st.rerun()
    
    def _render_user_management_tab(self):
        """Renderiza la pestaña de gestión de usuarios."""
        st.subheader("👥 **Gestión de Usuarios**")
        
        # Verificar permisos de admin
        if "current_user" not in st.session_state:
            st.warning("🔒 Debes iniciar sesión para acceder a esta función")
            return
        
        current_user = st.session_state["current_user"]
        if current_user["role"] != "admin":
            st.error("❌ Solo los administradores pueden gestionar usuarios")
            return
        
        # Crear nuevo usuario
        with st.expander("➕ Crear Nuevo Usuario", expanded=False):
            with st.form("create_user_form"):
                new_username = st.text_input("Nombre de usuario")
                new_email = st.text_input("Email")
                new_role = st.selectbox("Rol", list(self.roles.keys()))
                new_password = st.text_input("Contraseña", type="password")
                
                if st.form_submit_button("👤 Crear Usuario"):
                    if new_username and new_email and new_password:
                        result = self.create_user(
                            new_username, new_email, new_role, new_password,
                            current_user["username"]
                        )
                        if result["success"]:
                            st.success(result["message"])
                        else:
                            st.error(result["error"])
                    else:
                        st.warning("Por favor, completa todos los campos")
        
        # Lista de usuarios
        st.subheader("📋 **Usuarios del Sistema**")
        if self.users:
            user_data = []
            for username, user in self.users.items():
                user_data.append({
                    "Usuario": username,
                    "Email": user.email,
                    "Rol": user.role,
                    "Estado": "🟢 Activo" if user.is_active else "🔴 Inactivo",
                    "Bloqueado": "🔒 Sí" if user.locked_until and datetime.now() < user.locked_until else "✅ No",
                    "Último Login": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Nunca",
                    "Intentos Fallidos": user.failed_attempts
                })
            
            import pandas as pd
            user_df = pd.DataFrame(user_data)
            st.dataframe(user_df, use_container_width=True, hide_index=True)
    
    def _render_security_reports_tab(self):
        """Renderiza la pestaña de reportes de seguridad."""
        st.subheader("📊 **Reportes de Seguridad**")
        
        # Verificar permisos de admin
        if "current_user" not in st.session_state:
            st.warning("🔒 Debes iniciar sesión para acceder a esta función")
            return
        
        current_user = st.session_state["current_user"]
        if current_user["role"] != "admin":
            st.error("❌ Solo los administradores pueden ver reportes de seguridad")
            return
        
        if st.button("📊 Generar Reporte de Seguridad"):
            result = self.get_security_report(current_user["username"])
            if result["success"]:
                report = result["report"]
                
                # Métricas principales
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Usuarios", report["user_statistics"]["total_users"])
                with col2:
                    st.metric("Usuarios Activos", report["user_statistics"]["active_users"])
                with col3:
                    st.metric("Tasa de Éxito Login", f"{report['access_statistics']['success_rate']:.1f}%")
                with col4:
                    st.metric("Eventos Recientes", len(report["recent_security_events"]))
                
                # Eventos de seguridad recientes
                st.subheader("🚨 **Eventos de Seguridad Recientes**")
                if report["recent_security_events"]:
                    events_df = pd.DataFrame(report["recent_security_events"])
                    st.dataframe(events_df, use_container_width=True, hide_index=True)
                
                # IPs sospechosas
                if report["suspicious_ips"]:
                    st.subheader("⚠️ **IPs Sospechosas**")
                    for ip, count in report["suspicious_ips"].items():
                        st.warning(f"IP {ip}: {count} intentos fallidos")
    
    def _render_audit_tab(self):
        """Renderiza la pestaña de auditoría."""
        st.subheader("🔍 **Auditoría del Sistema**")
        
        # Verificar permisos
        if "current_user" not in st.session_state:
            st.warning("🔒 Debes iniciar sesión para acceder a esta función")
            return
        
        current_user = st.session_state["current_user"]
        if current_user["role"] not in ["admin", "analyst"]:
            st.error("❌ Permisos insuficientes para ver auditoría")
            return
        
        # Logs de acceso
        st.subheader("📝 **Logs de Acceso**")
        if self.access_logs:
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                action_filter = st.selectbox(
                    "Filtrar por Acción",
                    ["Todas"] + list(set(log.action for log in self.access_logs))
                )
            
            with col2:
                success_filter = st.selectbox(
                    "Filtrar por Resultado",
                    ["Todos", "Exitosos", "Fallidos"]
                )
            
            # Aplicar filtros
            filtered_logs = self.access_logs
            if action_filter != "Todas":
                filtered_logs = [log for log in filtered_logs if log.action == action_filter]
            if success_filter == "Exitosos":
                filtered_logs = [log for log in filtered_logs if log.success]
            elif success_filter == "Fallidos":
                filtered_logs = [log for log in filtered_logs if not log.success]
            
            # Mostrar logs filtrados
            if filtered_logs:
                log_data = []
                for log in filtered_logs[-50:]:  # Últimos 50 logs
                    log_data.append({
                        "Usuario": log.username,
                        "Acción": log.action,
                        "Recurso": log.resource,
                        "Timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "IP": log.ip_address,
                        "Resultado": "✅ Exitoso" if log.success else "❌ Fallido"
                    })
                
                log_df = pd.DataFrame(log_data)
                st.dataframe(log_df, use_container_width=True, hide_index=True)
            else:
                st.info("No hay logs que coincidan con los filtros")
        else:
            st.info("No hay logs de acceso disponibles")

# Instancia global
security_module = SecurityModule()








