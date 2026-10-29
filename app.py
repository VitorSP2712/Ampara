"""Application factory do Ampara (Req. 1).

`create_app(config)` carrega `config.py`, integra o gerenciamento de conexão
SQLite por requisição (`g.db` + teardown) e expõe `init_db` como comando CLI
(`flask init-db`). Os blueprints serão registrados nas próximas tasks; o ponto
de registro já fica preparado para manter a factory extensível.
"""

import click
from flask import Flask

from config import Config
from data import db as db_module


def create_app(config=None):
    """Cria e configura a aplicação Flask.

    `config` pode ser uma classe/objeto de configuração (padrão: `Config`),
    permitindo injetar um banco temporário ou `:memory:` nos testes.
    """
    app = Flask(__name__)
    app.config.from_object(config or Config)

    # Conexão SQLite por requisição: fecha no teardown do contexto (Req. 1.4).
    db_module.init_app(app)

    # Comando CLI `flask init-db` para aplicar o schema (Req. 1.1/1.2/1.3/1.5).
    @app.cli.command("init-db")
    def init_db_command():
        """Inicializa o banco de dados aplicando o schema."""
        db_module.init_db(app)
        print(f"Banco inicializado em {app.config['DATABASE']}.")

    # Comando CLI `flask create-admin` para criar a conta de admin (Req. 12).
    @app.cli.command("create-admin")
    @click.option("--email", default=None, help="E-mail (padrão: ADMIN_EMAIL).")
    @click.option("--password", default=None, help="Senha (padrão: ADMIN_PASSWORD).")
    @click.option("--name", default=None, help="Nome (padrão: parte local do e-mail).")
    def create_admin_command(email, password, name):
        """Cria uma conta com papel admin."""
        from data.db import get_db
        from services import admin_service
        from services.errors import DomainError

        data = {
            "email": email or app.config.get("ADMIN_EMAIL"),
            "password": password or app.config.get("ADMIN_PASSWORD"),
            "name": name,
        }
        try:
            admin = admin_service.create_admin(get_db(), data)
        except DomainError as error:
            raise click.ClickException(error.message) from error
        print(f"Admin criado: {admin['email']}.")

    # Disponibiliza init_db no objeto app para uso programático/testes.
    app.init_db = lambda: db_module.init_db(app)

    _register_blueprints(app)

    return app


def _register_blueprints(app):
    """Ponto de registro de blueprints.

    Mantido extensível de propósito: novas rotas (`routes/`) são adicionadas nas
    tasks seguintes, cada uma com seu blueprint registrado aqui.
    """
    # Registro de ocorrência: POST /api/reports e GET /reportar (Req. 2).
    from routes.report_routes import bp as report_bp

    app.register_blueprint(report_bp)

    # Agregados públicos por célula: GET /api/grid (Req. 3.4, 4).
    from routes.grid_routes import bp as grid_bp

    app.register_blueprint(grid_bp)

    # Indicadores públicos por SQL: GET /api/indicators/* (Req. 5).
    from routes.indicator_routes import bp as indicator_bp

    app.register_blueprint(indicator_bp)

    # Páginas públicas: GET / (mapa) e GET /indicadores (indicadores).
    from routes.main_routes import bp as main_bp

    app.register_blueprint(main_bp)

    # Cadastro, login e logout: /auth/register|login|logout (Req. 8).
    from routes.auth_routes import bp as auth_bp

    app.register_blueprint(auth_bp)

    # Auto-cadastro de ONG: /ong/register (Req. 10.1/10.2).
    from routes.ong_routes import bp as ong_bp

    app.register_blueprint(ong_bp)

    # Administração de ONGs: /admin/ongs/pending|<id>/approve|reject (Req. 12).
    from routes.admin_routes import bp as admin_bp

    app.register_blueprint(admin_bp)


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
