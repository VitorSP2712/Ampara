# Ampara

Plataforma web de proteção e bem-estar animal. Cidadãos registram ocorrências georreferenciadas de animais em situação de risco (rua, abandono, suspeita de maus-tratos), o sistema mostra um mapa público agregado por células de grade (sem expor coordenadas exatas) e indicadores, e encaminha cada caso à ONG aprovada que cobre a região.

## Stack

- Python 3 + Flask (`Flask>=3.0,<4.0`, única dependência de runtime)
- SQLite (módulo `sqlite3` da biblioteca padrão)
- Leaflet (mapa) e Chart.js (gráficos), carregados no front-end
- Testes: pytest + Hypothesis (somente desenvolvimento)

Estrutura em camadas: `routes/` (HTTP) → `services/` (regras) → `data/` (repositórios SQLite), com `utils/` para grade geográfica, validação e segurança.

## Instalação

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux/macOS
# source .venv/bin/activate

# Runtime
pip install -r requirements.txt

# Runtime + testes (pytest e hypothesis)
pip install -r requirements-dev.txt
```

## Configuração

Copie `.env.example` para `.env` e ajuste os valores. A aplicação lê as variáveis do **ambiente do processo** (`os.environ`); ela não carrega o arquivo `.env` sozinha. Exporte as variáveis no shell ou use a ferramenta de sua preferência para carregá-las.

| Variável | Descrição | Padrão |
| --- | --- | --- |
| `SECRET_KEY` | Chave de sessão Flask. Use um valor aleatório em produção. | `dev-secret-change-me` |
| `DATABASE` | Caminho do arquivo SQLite. | `ampara.db` |
| `GRID_PRECISION` | Casas decimais da grade geográfica. | `2` |
| `UPLOAD_FOLDER` | Diretório de imagens das ocorrências. | `uploads` |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Credenciais padrão de `flask create-admin` (opcionais). Senha de 8 a 128 caracteres. | vazio |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Credenciais SMTP (opcionais). `SMTP_PORT` padrão: `587`. | vazio |

**Modo simulado:** sem credenciais SMTP, as notificações às ONGs são apenas registradas no banco com estado `simulada`. Ocorrências sem ONG aprovada cobrindo a célula ficam como `pendente_atribuicao`. A aplicação funciona normalmente sem SMTP.

Exemplo (PowerShell):

```powershell
$env:SECRET_KEY = "uma-chave-aleatoria"
$env:DATABASE = "ampara.db"
```

## Inicialização do banco

Aplica `database/schema.sql` em uma única transação (rollback em caso de falha). É idempotente e preserva dados existentes.

```bash
flask --app app init-db
```

Também é possível chamar `create_app().init_db()` em código.

Para criar uma conta de administrador (necessária para aprovar ONGs), depois do `init-db`:

```bash
flask --app app create-admin --email admin@exemplo.com --password "senha-forte-123"
# ou defina ADMIN_EMAIL e ADMIN_PASSWORD no ambiente e rode sem opções
```

## Executando a aplicação

```bash
flask --app app run --debug
# ou
python app.py
```

Acesse `http://127.0.0.1:5000/`.

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

Os testes usam bancos SQLite temporários e não alteram o `ampara.db` local.

## Endpoints principais

Páginas:

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/` | Mapa interativo agregado por célula |
| GET | `/indicadores` | Página de indicadores |
| GET | `/reportar` | Formulário de registro de ocorrência |
| GET | `/me/reports` | Relatos do usuário logado (requer login) |
| GET | `/auth/login`, `/auth/register` | Telas de login e cadastro |
| GET | `/ong/register` | Auto-cadastro de ONG |
| GET | `/ong/painel` | Painel da ONG (papel `ong`) |
| GET | `/admin/ongs/pending` | ONGs pendentes (papel `admin`) |

API:

| Método | Rota | Descrição |
| --- | --- | --- |
| POST | `/api/reports` | Cria ocorrência (anônima ou autenticada) |
| GET | `/api/grid` | Agregados por célula; filtros opcionais de categoria, status e período |
| GET | `/api/indicators/category` | Contagem por categoria |
| GET | `/api/indicators/status` | Contagem por status |
| GET | `/api/indicators/monthly` | Contagem por mês (`AAAA-MM`) |
| GET | `/api/indicators/ranking` | Top 10 células com mais ocorrências |
| POST | `/auth/register`, `/auth/login`, `/auth/logout` | Cadastro, login e logout |
| POST | `/ong/register` | Auto-cadastro de ONG (status `pendente`) |
| POST | `/ong/reports/<id>/status` | ONG atualiza o status de uma ocorrência da sua área |
| POST | `/admin/ongs/<id>/approve` | Admin aprova ONG |
| POST | `/admin/ongs/<id>/reject` | Admin rejeita ONG |

Os endpoints públicos (`/api/grid`, `/api/indicators/*`) nunca retornam latitude/longitude exatas, descrição ou dados do usuário.
