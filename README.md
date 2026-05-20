# SmartRisk: Um Sistema Automatizado para Gestão de Riscos em Segurança da Informação

![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=plastic&logo=django&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=plastic&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/css-%231572B6.svg?style=plastic&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/-JavaScript-black?style=flat-square&logo=javascript)
![Shell Script](https://img.shields.io/badge/shell_script-%23121011.svg?style=plastic&logo=gnu-bash&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05033?style=flat-square&logo=git&logoColor=white)
![SQLite](https://img.shields.io/badge/Sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![VSCode](https://img.shields.io/badge/VSCode-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)

![Open Issues](https://img.shields.io/github/issues/livlutz/INF1951)
![Open PRs](https://img.shields.io/github/issues-pr/livlutz/INF1951)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-darkmagenta.svg)
![GitHub Created At](https://img.shields.io/github/created-at/livlutz/INF1951)


![Languages Count](https://img.shields.io/github/languages/count/livlutz/INF1951)
![Last Commit](https://img.shields.io/github/last-commit/livlutz/INF1951)
![Repo Size](https://img.shields.io/github/repo-size/livlutz/INF1951)
![Code Size](https://img.shields.io/github/languages/code-size/livlutz/INF1951)


![GitHub stars](https://img.shields.io/github/stars/livlutz/INF1951?style=social)
![GitHub forks](https://img.shields.io/github/forks/livlutz/INF1951?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/livlutz/INF1951)


Projeto Final II 2026.1 - Lívia Lutz dos Santos - 2211055

## Escopo do Projeto

Este trabalho propõe o desenvolvimento de um sistema automatizado e integrado de apoio à gestão de riscos em um Sistema de Gestão de Segurança da Informação (SGSI/ ISMS). A solução visa modelar o ciclo de vida completo do risco, permitindo o alinhamento contínuo entre ativos e suas vulnerabilidades, bem como a reavaliação do risco residual. A proposta segue o padrão ISO/IEC 27001 e aplica o ciclo PDCA (Plan, Do, Check, Act), buscando reduzir erros manuais, aumentar a precisão das análises e fortalecer a resiliência organizacional frente às ameaças digitais. Espera-se, com isso, promover uma gestão de segurança da informação mais eficiente, automatizada e em conformidade com as melhores práticas internacionais.

Este repositório contém um sistema web completo para apoio à gestão de segurança da informação, desenvolvido com Django.

O sistema cobre o ciclo principal de gestão de risco, incluindo:

- Cadastro e valoração de ativos
- Identificação, análise, avaliação e tratamento de riscos
- Detecção de ameaças e gestão de vulnerabilidades
- Gestão de incidentes e emissão de relatório
- Registro de auditorias e gestão de controles
- Gestão de usuários e perfis

### Sistema de Usuários

✅ Cadastro de usuários

✅ Login e logout

✅ Perfil do usuário

✅ Edição de perfil

✅ Alteração de senha

✅ Exclusão de conta

### Gestão de Ativos

✅ Cadastro de categoria de ativo

✅ Cadastro de ativo

✅ Listagem de ativos

✅ Edição e exclusão de ativos

✅ Criação e análise de critérios de valoração de ativos (CIDP)

### Gestão de Riscos

✅ Criação de critérios de avaliação de riscos

✅ Identificação de riscos

✅ Listagem, edição e exclusão de
riscos

✅ Análise e avaliação de riscos

✅ Tratamento de riscos com controles e redução esperada

### Ameaças e Vulnerabilidades

✅ Detecção de ameaças

✅ Listagem, edição e exclusão de ameaças

✅ Gestão de vulnerabilidades

✅ Listagem, edição e exclusão de vulnerabilidades

### Incidentes

✅ Gestão de incidentes

✅ Cadastro de incidente

✅ Visualização e exclusão de incidente

✅ Geração de relatório de incidente

✅ Visualização de relatório de incidente

### Auditoria e Controles

✅ Registro de auditoria

✅ Listagem, edição e exclusão de auditorias

✅ Cadastro de controles

✅ Listagem, edição e exclusão de controles

### Interface e Experiência

✅ Navegação por módulos

✅ Formulários com validação

✅ Feedback visual de ações

## 🚀 Instalação e Configuração Local

### Instalação Automática

No diretório raiz do repositório:

```bash
./run.sh
```

Esse script:

1. Entra na pasta `isms/`
2. Cria e ativa ambiente virtual (se necessário)
3. Instala dependências
4. Executa migrações
5. Inicia o servidor Django

### Instalação Manual

Se preferir, uma alternativa mais rápida também é executar diretamente o script:

```bash
./run.sh
```

Ou siga o passo a passo manual abaixo:

1. Entre na pasta principal do projeto Django:

```bash
cd isms
```

1. Crie o ambiente virtual:

```bash
python -m venv venv
```

1. Ative o ambiente virtual:

```bash
source venv/bin/activate
```

1. Instale dependências:

```bash
pip install -r requirements.txt
```

1. Entre na pasta onde está o `manage.py`:

```bash
cd isms
```

1. Execute migrações:

```bash
python manage.py makemigrations
python manage.py migrate
```

1. Inicie o servidor:

```bash
python manage.py runserver
```

Após isso, acesse:

<http://127.0.0.1:8000/>

## 📚 Manual do Usuário

### 🏠 Página Inicial

A página inicial permite acesso aos principais módulos do sistema e às ações de autenticação.

### 👤 Usuários e Perfil

- Cadastro: criar uma nova conta
- Login: autenticar com credenciais
- Perfil: visualizar e editar dados pessoais
- Trocar senha: alterar credenciais
- Excluir conta: remover conta com confirmação

### 🧱 Módulo de Ativos

- Cadastrar categoria de ativo
- Cadastrar ativo
- Listar, editar e excluir ativos
- Avaliar valoração CIDP

### ⚠️ Módulo de Riscos

- Definir critérios de avaliação
- Identificar riscos
- Analisar e avaliar riscos
- Tratar riscos com controles

### 🛡️ Módulo de Ameaças e Vulnerabilidades

- Registrar ameaças e vinculá-las a ativos
- Registrar vulnerabilidades e vinculá-las a ameaças/ativos
- Editar e excluir registros

### 🚨 Módulo de Incidentes

- Registrar incidente
- Acompanhar incidentes
- Gerar relatório de incidente

### 📋 Módulo de Auditoria e Controles

- Registrar auditorias
- Consultar histórico de auditorias
- Cadastrar e manter controles

## 🔧 Testes Realizados

### Testes de Funcionalidade

✅ Autenticação de usuários

✅ Fluxo CRUD de ativos

✅ Fluxo CRUD de riscos

✅ Fluxo CRUD de ameaças

✅ Fluxo CRUD de vulnerabilidades

✅ Fluxo de tratamento de riscos

✅ Fluxo de incidentes e relatório

✅ Fluxo de auditorias

✅ Fluxo de controles

### Testes de Interface

✅ Validação de formulários

✅ Navegação entre módulos

✅ Consistência visual de componentes

### Testes de Segurança

✅ Restrição de acesso por autenticação

✅ Validação de permissões por perfil em fluxos críticos

## 🔄 Instruções para Manutenção

Sempre que houver alterações em modelos:

```bash
python manage.py makemigrations
python manage.py migrate
```

Para atualizar dependências:

```bash
pip install -r requirements.txt
```
