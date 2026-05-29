"""Enterprise App Builder - Full-stack SaaS generation using REAL AI"""
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from neuro.router.smart_router import SmartRouter

class AppType(Enum):
    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    DASHBOARD = "dashboard"
    CRM = "crm"
    CMS = "cms"
    API = "api"

@dataclass
class AppSpec:
    name: str
    app_type: AppType
    features: List[str] = field(default_factory=list)
    tech_stack: Dict[str, str] = field(default_factory=dict)

class EnterpriseAppBuilder:
    """Builds enterprise-level applications using REAL AI."""
    
    def __init__(self):
        self.router = SmartRouter()
    
    def build_app(self, goal: str, app_type: AppType = AppType.SAAS, output_dir: str = "./output") -> Dict[str, Any]:
        """Build COMPLETE enterprise application using REAL AI."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate specification
        spec_prompt = f"""Create a detailed specification for: {goal}
App type: {app_type.value}

Include:
- Application name and description
- User roles and permissions
- Feature list (10+ features)
- Data models
- API endpoints
- Tech stack recommendations
- UI/UX requirements

Output as structured text.
"""
        spec = self.router.chat(spec_prompt, task_type="architecture_design")
        
        # Generate frontend
        frontend_prompt = f"""Generate complete React frontend for: {goal}
App type: {app_type.value}

Include:
- App.jsx with React Router
- Auth pages (login, register)
- Dashboard with charts
- CRUD pages for main entities
- Settings page
- API integration
- Tailwind styling

Output ONLY React code, no markdown.
"""
        frontend = self.router.chat(frontend_prompt, task_type="frontend_react")
        
        # Generate backend
        backend_prompt = f"""Generate complete Node.js/Express backend for: {goal}
App type: {app_type.value}

Include:
- Express server with CORS, helmet, rate limiting
- JWT authentication middleware
- RESTful routes for CRUD
- Database models (SQLAlchemy or Mongoose)
- Validation with express-validator
- Error handling
- Unit tests

Output ONLY Node.js code, no markdown.
"""
        backend = self.router.chat(backend_prompt, task_type="backend_api")
        
        # Generate database schema
        db_prompt = f"""Generate PostgreSQL database schema for: {goal}
App type: {app_type.value}

Include:
- All tables with columns and types
- Primary keys and foreign keys
- Indexes for performance
- Triggers for timestamps
- Seed data for testing

Output ONLY SQL code, no markdown.
"""
        database = self.router.chat(db_prompt, task_type="database_sql")
        
        # Generate deployment configs
        deploy_prompt = f"""Generate Docker deployment files for: {goal}
Tech stack: React + Node.js + PostgreSQL

Include:
- Dockerfile for app
- docker-compose.yml with all services
- nginx.conf for reverse proxy
- GitHub Actions CI/CD

Output ONLY code, no markdown.
"""
        deploy = self.router.chat(deploy_prompt, task_type="devops_deployment")
        
        # Write files to disk
        files_written = []
        
        # Write index.html
        index_html_path = output_path / "index.html"
        index_html_path.write_text(frontend)
        files_written.append(str(index_html_path))
        print(f"📄 Written: {index_html_path}")
        
        # Write App.jsx
        app_jsx_path = output_path / "App.jsx"
        app_jsx_path.write_text(frontend)
        files_written.append(str(app_jsx_path))
        print(f"📄 Written: {app_jsx_path}")
        
        # Write style.css
        style_css_path = output_path / "style.css"
        style_css_path.write_text("// Styles for " + goal)
        files_written.append(str(style_css_path))
        print(f"📄 Written: {style_css_path}")
        
        # Write backend
        backend_path = output_path / "server.js"
        backend_path.write_text(backend)
        files_written.append(str(backend_path))
        print(f"📄 Written: {backend_path}")
        
        # Write database schema
        db_path = output_path / "schema.sql"
        db_path.write_text(database)
        files_written.append(str(db_path))
        print(f"📄 Written: {db_path}")
        
        # Write deployment files
        deploy_path = output_path / "docker-compose.yml"
        deploy_path.write_text(deploy)
        files_written.append(str(deploy_path))
        print(f"📄 Written: {deploy_path}")
        
        print(f"\n✅ Enterprise app built in: {output_path}")
        print(f"   Output files: {files_written}")
        
        return {
            "spec": spec,
            "frontend": frontend,
            "backend": backend,
            "database": database,
            "deploy": deploy,
            "app_type": app_type.value,
            "output_dir": str(output_path),
            "files_written": files_written,
        }


def build_enterprise_app(goal: str, app_type: str = "saas", output_dir: str = "./output") -> Dict[str, Any]:
    """Quick enterprise app builder using real AI."""
    builder = EnterpriseAppBuilder()
    app_types = {
        "saas": AppType.SAAS,
        "ecommerce": AppType.ECOMMERCE,
        "dashboard": AppType.DASHBOARD,
        "crm": AppType.CRM,
        "cms": AppType.CMS,
        "api": AppType.API,
    }
    return builder.build_app(goal, app_types.get(app_type, AppType.SAAS), output_dir)
