"""
PBIP Loader - Cloud-Ready File Loading
Handles PBIP file loading for both local and cloud environments (Cloudera AI Workbench)
"""

import streamlit as st
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple, List
import shutil
import os


class PBIPLoader:
    """
    Unified PBIP loader that works in both local and cloud environments
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize PBIP loader

        Args:
            storage_path: Path to persistent storage for PBIP projects
                         If None, uses temporary storage (files deleted on restart)
        """
        self.storage_path = Path(storage_path) if storage_path else None

        # Create storage directory if specified and doesn't exist
        if self.storage_path and not self.storage_path.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)

    def render_uploader(self, key: str = "pbip_uploader") -> Optional[str]:
        """
        Render file uploader UI and return path to extracted PBIP file

        Args:
            key: Unique key for the uploader widget

        Returns:
            Path to .pbip file if successful, None otherwise
        """
        st.markdown("### 📂 Cargar Proyecto PBIP")

        # Show two tabs: Upload or Select Existing (if persistent storage)
        if self.storage_path:
            tab1, tab2 = st.tabs(["📤 Subir Nuevo Proyecto", "📁 Proyectos Guardados"])

            with tab1:
                upload_path = self._render_upload_tab(key)

            with tab2:
                existing_path = self._render_existing_projects_tab()

            # Priorizar upload (recien subido) sobre existing
            return upload_path or existing_path
        else:
            # Only upload available (no persistent storage)
            return self._render_upload_tab(key)

    def _render_upload_tab(self, key: str) -> Optional[str]:
        """Render upload interface"""

        st.markdown("""
        <div style="background: rgba(4, 81, 228, 0.05); padding: 1rem; border-radius: 8px;
                    border-left: 3px solid #0451E4; margin-bottom: 1rem;">
            <p style="margin: 0; font-size: 0.9rem; color: #1E293B;">
                <strong>💡 Cómo preparar tu proyecto:</strong>
            </p>
            <ol style="margin: 0.5rem 0 0 1.5rem; font-size: 0.85rem; color: #475569;">
                <li>Abre tu reporte en Power BI Desktop</li>
                <li>Guarda como <strong>.pbip</strong> (Archivo → Guardar como → Power BI Project)</li>
                <li>Comprime la carpeta completa en un archivo <strong>.zip</strong></li>
                <li>Sube el archivo aquí 👇</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Sube tu proyecto PBIP comprimido",
            type=['zip'],
            help="Archivo ZIP que contiene tu proyecto .pbip completo",
            key=key
        )

        if not uploaded_file:
            st.info("👆 Sube un archivo ZIP con tu proyecto PBIP para comenzar")
            return None

        try:
            # Determine extraction path
            if self.storage_path:
                # Persistent storage
                extract_path = self._extract_to_persistent(uploaded_file)
            else:
                # Temporary storage
                extract_path = self._extract_to_temp(uploaded_file)

            # Find .pbip file
            pbip_files = list(Path(extract_path).rglob("*.pbip"))

            if not pbip_files:
                st.error("❌ No se encontró archivo .pbip en el ZIP subido")
                st.info("Verifica que hayas comprimido la carpeta completa del proyecto PBIP")
                return None

            if len(pbip_files) > 1:
                st.warning(f"⚠️ Se encontraron {len(pbip_files)} archivos .pbip. Usando: {pbip_files[0].name}")

            pbip_path = str(pbip_files[0])

            # Show success message (unified)
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.10);
                        border: 1px solid rgba(16, 185, 129, 0.25);
                        border-left: 4px solid #10B981;
                        border-radius: 8px;
                        padding: 0.85rem 1.1rem;
                        margin: 0.5rem 0;">
                <p style="margin: 0; font-weight: 600; color: #10B981; font-size: 0.95rem;">
                    ✅ Proyecto cargado exitosamente
                </p>
                <p style="margin: 0.3rem 0 0 0; font-size: 0.85rem; color: #64748B;">
                    📊 {pbip_files[0].name}
                </p>
            </div>
            """, unsafe_allow_html=True)

            return pbip_path

        except zipfile.BadZipFile:
            st.error("❌ El archivo no es un ZIP válido")
            return None
        except Exception as e:
            st.error(f"❌ Error al procesar el proyecto: {str(e)}")
            with st.expander("🔍 Ver detalles del error"):
                import traceback
                st.code(traceback.format_exc())
            return None

    def _render_existing_projects_tab(self) -> Optional[str]:
        """Render interface to select from existing projects"""

        if not self.storage_path:
            st.warning("⚠️ Almacenamiento persistente no configurado")
            return None

        # Find all PBIP projects in storage
        pbip_files = list(self.storage_path.rglob("*.pbip"))

        if not pbip_files:
            st.info("""
            📭 No hay proyectos guardados todavía

            Sube tu primer proyecto en la pestaña **"Subir Nuevo Proyecto"**
            """)
            return None

        # Create project list with metadata
        projects = []
        for pbip_file in pbip_files:
            stat = pbip_file.stat()
            projects.append({
                'name': pbip_file.stem,
                'path': str(pbip_file),
                'size_mb': stat.st_size / (1024 * 1024),
                'modified': stat.st_mtime,
                'display': f"{pbip_file.stem} ({stat.st_size / (1024 * 1024):.1f} MB)"
            })

        # Sort by most recently modified
        projects.sort(key=lambda x: x['modified'], reverse=True)

        st.markdown(f"""
        <div style="background: #F8FAFC; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem;">
            <p style="margin: 0; font-size: 0.9rem; color: #475569;">
                📁 <strong>{len(projects)}</strong> proyecto(s) disponible(s)
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Project selector
        selected_display = st.selectbox(
            "Selecciona un proyecto",
            [p['display'] for p in projects],
            key="existing_project_selector"
        )

        if selected_display:
            # Find selected project
            selected = next(p for p in projects if p['display'] == selected_display)

            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""
                <div style="padding: 0.5rem; background: white; border-radius: 6px; border: 1px solid #E2E8F0;">
                    <p style="margin: 0; font-weight: 600; color: #0451E4;">📊 {selected['name']}</p>
                    <p style="margin: 0.25rem 0 0 0; font-size: 0.8rem; color: #64748B;">
                        {selected['size_mb']:.1f} MB
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button("🗑️ Eliminar", key="delete_project"):
                    if self._delete_project(Path(selected['path'])):
                        st.success("✅ Proyecto eliminado")
                        st.rerun()
                    else:
                        st.error("❌ Error al eliminar")

            with col3:
                if st.button("✅ Usar", key="use_project", type="primary"):
                    st.session_state.selected_pbip_path = selected['path']

            # Return path if selected
            if 'selected_pbip_path' in st.session_state:
                path = st.session_state.selected_pbip_path
                del st.session_state.selected_pbip_path
                return path

        return None

    def _extract_to_temp(self, uploaded_file) -> str:
        """Extract ZIP to temporary directory"""
        tmpdir = tempfile.mkdtemp(prefix="pbip_")

        zip_path = Path(tmpdir) / uploaded_file.name
        zip_path.write_bytes(uploaded_file.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        return tmpdir

    def _extract_to_persistent(self, uploaded_file) -> str:
        """Extract ZIP to persistent storage"""
        # Create project folder based on uploaded file name
        project_name = Path(uploaded_file.name).stem
        project_path = self.storage_path / project_name

        # Remove existing if present
        if project_path.exists():
            shutil.rmtree(project_path)

        project_path.mkdir(parents=True, exist_ok=True)

        # Save and extract ZIP
        zip_path = project_path / uploaded_file.name
        zip_path.write_bytes(uploaded_file.read())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(project_path)

        # Remove the ZIP after extraction
        zip_path.unlink()

        return str(project_path)

    def _delete_project(self, pbip_path: Path) -> bool:
        """Delete a project from persistent storage"""
        try:
            # Delete the parent directory of the .pbip file
            project_dir = pbip_path.parent
            if project_dir.exists() and project_dir != self.storage_path:
                shutil.rmtree(project_dir)
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def get_storage_path_from_env() -> Optional[str]:
        """
        Get storage path from environment variables

        Checks:
        1. PBIP_STORAGE_PATH env var
        2. Default Cloudera path: /home/cdsw/pbip_projects
        3. None (temp storage only)
        """
        # Check env var
        env_path = os.getenv('PBIP_STORAGE_PATH')
        if env_path:
            return env_path

        # Check if running in Cloudera (common path)
        cloudera_path = Path('/home/cdsw/pbip_projects')
        if cloudera_path.parent.exists():
            return str(cloudera_path)

        # Fall back to temp storage
        return None


# Convenience functions for quick integration

def load_pbip_cloud_ready(key: str = "pbip_upload",
                          persistent_storage: bool = True) -> Optional[str]:
    """
    Quick function to load PBIP with cloud-ready defaults

    Args:
        key: Unique key for the uploader widget
        persistent_storage: Whether to use persistent storage (if available)

    Returns:
        Path to .pbip file if successful, None otherwise

    Example:
        ```python
        pbip_path = load_pbip_cloud_ready(key="analyzer_upload")
        if pbip_path:
            results = analyze_powerbi_file(pbip_path)
        ```
    """
    storage_path = None
    if persistent_storage:
        storage_path = PBIPLoader.get_storage_path_from_env()

    loader = PBIPLoader(storage_path=storage_path)
    return loader.render_uploader(key=key)


def is_cloudera_environment() -> bool:
    """
    Detect if running in Cloudera AI Workbench

    Returns:
        True if in Cloudera environment
    """
    # Common Cloudera paths
    return (
        Path('/home/cdsw').exists() or
        os.getenv('CDSW_PROJECT_URL') is not None or
        os.getenv('CDSW_ENGINE_ID') is not None
    )
