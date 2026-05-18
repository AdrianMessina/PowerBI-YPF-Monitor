"""
Security Verification Script - Pre-commit Check
Verifica que no haya información sensible antes de hacer commit a GitHub

Usage:
    python scripts/verify_security.py [--fix]

Options:
    --fix    Intentar corregir problemas automáticamente

Exit codes:
    0 = Todo OK, seguro para commit
    1 = Se encontraron problemas de seguridad, NO hacer commit
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import argparse


class SecurityIssue:
    """Representa un problema de seguridad encontrado"""

    def __init__(self, file_path: str, line_number: int, issue_type: str,
                 content: str, severity: str = "high"):
        self.file_path = file_path
        self.line_number = line_number
        self.issue_type = issue_type
        self.content = content
        self.severity = severity  # low, medium, high, critical

    def __str__(self):
        severity_prefix = {
            'critical': '[CRIT]',
            'high': '[HIGH]',
            'medium': '[MED ]',
            'low': '[LOW ]'
        }
        prefix = severity_prefix.get(self.severity, '[WARN]')
        return (f"{prefix} [{self.severity.upper()}] {self.file_path}:{self.line_number}\n"
                f"   Tipo: {self.issue_type}\n"
                f"   Contenido: {self.content[:80]}...")


class SecurityScanner:
    """Scanner de seguridad para detectar información sensible"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[SecurityIssue] = []

        # Patrones sensibles a buscar
        self.patterns = {
            'usuarios_ypf': {
                'regex': r'(se\d{5}|ry\d{5})',
                'severity': 'high',
                'description': 'Código de usuario YPF'
            },
            'emails_personales': {
                'regex': r'[a-zA-Z0-9._%+-]+@(?:grupo\.)?ypf\.com',
                'severity': 'medium',
                'description': 'Email corporativo YPF'
            },
            'passwords': {
                'regex': r'(?:password|passwd|pwd|clave)\s*=\s*["\'](?!your_|example|changeme|<)[^"\']{3,}["\']',
                'severity': 'critical',
                'description': 'Contraseña hardcodeada'
            },
            'api_keys': {
                'regex': r'(?:api[_-]?key|apikey|access[_-]?token)\s*=\s*["\'][^"\']{10,}["\']',
                'severity': 'critical',
                'description': 'API Key o Token'
            },
            'db_credentials': {
                'regex': r'(?:database|db)[_-]?(?:password|user|host)\s*=\s*["\'](?!your_|example|localhost|<)[^"\']{3,}["\']',
                'severity': 'high',
                'description': 'Credenciales de base de datos'
            },
            'private_keys': {
                'regex': r'BEGIN (?:RSA |EC |DSA )?PRIVATE KEY',
                'severity': 'critical',
                'description': 'Clave privada SSH/SSL'
            }
        }

        # Archivos que SIEMPRE deben estar en .gitignore
        self.required_gitignore_entries = [
            '.env',
            '.env.local',
            '.env.ypf.example',
            '.streamlit/secrets.toml',
            'logs/',
            '*.log'
        ]

        # Extensiones de archivos a escanear
        self.scan_extensions = {'.py', '.md', '.txt', '.yaml', '.yml', '.json', '.toml', '.env'}

        # Archivos/carpetas a excluir del escaneo
        self.exclude_paths = {'venv', 'env', '.venv', '__pycache__', '.git', 'node_modules',
                             'dist', 'build', '.idea', '.vscode', 'backups'}

    def scan_all(self) -> List[SecurityIssue]:
        """Escanear todos los archivos del proyecto"""
        print("[SCAN] Escaneando archivos en busca de informacion sensible...\n")

        # 1. Verificar .gitignore
        self._check_gitignore()

        # 2. Verificar .env.example no tiene valores reales
        self._check_env_example()

        # 3. Escanear todos los archivos
        self._scan_files()

        return self.issues

    def _check_gitignore(self):
        """Verificar que .gitignore tiene las entradas necesarias"""
        gitignore_path = self.project_root / '.gitignore'

        if not gitignore_path.exists():
            self.issues.append(SecurityIssue(
                str(gitignore_path), 0, 'missing_gitignore',
                'Archivo .gitignore no existe', 'critical'
            ))
            return

        with open(gitignore_path, 'r', encoding='utf-8') as f:
            gitignore_content = f.read()

        for entry in self.required_gitignore_entries:
            if entry not in gitignore_content:
                self.issues.append(SecurityIssue(
                    str(gitignore_path), 0, 'missing_gitignore_entry',
                    f'Falta entrada en .gitignore: {entry}', 'high'
                ))

    def _check_env_example(self):
        """Verificar que .env.example no tiene valores sensibles"""
        env_example_path = self.project_root / '.env.example'

        if not env_example_path.exists():
            return  # No es crítico si no existe

        with open(env_example_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            # Buscar usuarios YPF reales
            if re.search(r'(se\d{5}|ry\d{5})', line, re.IGNORECASE):
                self.issues.append(SecurityIssue(
                    str(env_example_path), i, 'usuario_ypf_en_example',
                    line.strip(), 'critical'
                ))

            # Buscar contraseñas no vacías
            if re.search(r'PASSWORD\s*=\s*[^#\n]', line, re.IGNORECASE):
                if not re.search(r'(your_|example|changeme|<|=\s*$)', line):
                    self.issues.append(SecurityIssue(
                        str(env_example_path), i, 'password_en_example',
                        line.strip(), 'high'
                    ))

    def _scan_files(self):
        """Escanear archivos del proyecto"""
        for file_path in self.project_root.rglob('*'):
            # Skip directorios
            if file_path.is_dir():
                continue

            # Skip archivos excluidos
            if any(excl in file_path.parts for excl in self.exclude_paths):
                continue

            # Solo escanear extensiones permitidas
            if file_path.suffix not in self.scan_extensions:
                continue

            # Skip .gitignore y archivos de seguridad
            if file_path.name in ['.gitignore', 'verify_security.py', '.env']:
                continue

            # Escanear archivo
            self._scan_file(file_path)

    def _scan_file(self, file_path: Path):
        """Escanear un archivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                for pattern_name, pattern_info in self.patterns.items():
                    matches = re.finditer(pattern_info['regex'], line, re.IGNORECASE)
                    for match in matches:
                        # Verificar si es un comentario o documentación
                        if self._is_documentation(line, file_path.suffix):
                            continue

                        self.issues.append(SecurityIssue(
                            str(file_path.relative_to(self.project_root)),
                            i,
                            pattern_name,
                            line.strip(),
                            pattern_info['severity']
                        ))

        except Exception as e:
            print(f"⚠️  Error leyendo {file_path}: {str(e)}")

    def _is_documentation(self, line: str, extension: str) -> bool:
        """Verificar si una línea es documentación/comentario"""
        line_stripped = line.strip()

        # Python comments
        if extension == '.py' and line_stripped.startswith('#'):
            # Permitir ejemplos en comentarios
            if 'ejemplo' in line_stripped.lower() or 'example' in line_stripped.lower():
                return True

        # Markdown
        if extension == '.md':
            # En markdown, casi todo es documentación
            # Solo alertar si parece código real (indentado o en bloques de código)
            if not line_stripped.startswith(('    ', '\t', '```')):
                return True

        return False

    def generate_report(self) -> Dict[str, any]:
        """Generar reporte de issues encontrados"""
        report = {
            'total': len(self.issues),
            'critical': sum(1 for i in self.issues if i.severity == 'critical'),
            'high': sum(1 for i in self.issues if i.severity == 'high'),
            'medium': sum(1 for i in self.issues if i.severity == 'medium'),
            'low': sum(1 for i in self.issues if i.severity == 'low'),
            'issues': self.issues
        }
        return report


def print_report(report: Dict):
    """Imprimir reporte de seguridad"""
    print("\n" + "="*70)
    print("REPORTE DE SEGURIDAD")
    print("="*70 + "\n")

    print(f"Total de issues encontrados: {report['total']}")
    print(f"  [CRIT] Criticos: {report['critical']}")
    print(f"  [HIGH] Altos:    {report['high']}")
    print(f"  [MED]  Medios:   {report['medium']}")
    print(f"  [LOW]  Bajos:    {report['low']}")
    print()

    if report['issues']:
        print("Detalles de los issues:\n")
        for issue in sorted(report['issues'], key=lambda x: x.severity, reverse=True):
            print(issue)
            print()

        print("="*70)
        print("[ERROR] SE ENCONTRARON PROBLEMAS DE SEGURIDAD")
        print("="*70)
        print("\n[WARN] NO HACER COMMIT HASTA RESOLVER LOS ISSUES CRITICOS Y ALTOS\n")
        print("Acciones recomendadas:")
        print("1. Revisar cada issue listado arriba")
        print("2. Remover información sensible de los archivos")
        print("3. Mover valores reales a .env (que está en .gitignore)")
        print("4. Usar valores de ejemplo en archivos que se suben a GitHub")
        print("5. Volver a ejecutar este script: python scripts/verify_security.py")
        print()

        return False
    else:
        print("="*70)
        print("[OK] TODO OK - SEGURO PARA COMMIT A GITHUB")
        print("="*70)
        print("\nNo se encontraron problemas de seguridad.")
        print("Puedes hacer commit y push con confianza.\n")
        return True


def main():
    parser = argparse.ArgumentParser(description='Verificar seguridad antes de commit')
    parser.add_argument('--fix', action='store_true', help='Intentar corregir automáticamente')

    args = parser.parse_args()

    # Get project root (assuming script is in scripts/ folder)
    project_root = Path(__file__).parent.parent

    print("[SECURITY] YPF BI Monitor - Security Verification Tool")
    print(f"Project root: {project_root}\n")

    # Scan
    scanner = SecurityScanner(project_root)
    issues = scanner.scan_all()
    report = scanner.generate_report()

    # Print report
    success = print_report(report)

    # Exit code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
