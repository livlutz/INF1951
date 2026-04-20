# Generated migration for loading ISO 27001 default controls

from django.db import migrations


def load_iso27001_controls(apps, schema_editor):
    """Load all ISO 27001 standard controls into the database."""
    Controle = apps.get_model('ismsapp', 'Controle')
    CategoriaControle = apps.get_model('ismsapp', 'CategoriaControle')

    # ISO 27001 Controls grouped by section and categorization
    CONTROLES_ISO27001 = [
        # Controles Organizacionais (Seção 5)
        {
            'nome': '5.1 - Políticas de segurança da informação',
            'descricao': 'Defenir e comunicar as políticas de segurança da informação que refletem os objetivos da organizaçao e proporcionam a direção geral para a segurança da informação.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.2 - Papéis e responsabilidades pela segurança da informação',
            'descricao': 'Atribuir papéis e responsabilidades relativos à segurança da informação a todos os funcionários e prestadores de serviços.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.3 - Segregação de funções',
            'descricao': 'Segregar tarefas e áreas de responsabilidade para reduzir oportunidades de modificação ou uso inadequado de ativos da organização.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.4 - Responsabilidades da direção',
            'descricao': 'A direção deve demonstrar competência e reforçar a importância da gestão de segurança da informação e conformidade com a política de segurança.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.5 - Contato com autoridades',
            'descricao': 'Manter contato e colaboração com autoridades relevantes e órgãos reguladores. Estabelecer relacionamentos para reportar incidentes de segurança.',
            'categorias': ['preventivo', 'corretivo']
        },
        {
            'nome': '5.6 - Contato com grupos de interesse especial',
            'descricao': 'Manter contato e colaboração com grupos especiais relacionados à segurança da informação, incluindo associações e comunidades de segurança.',
            'categorias': ['preventivo', 'corretivo']
        },
        {
            'nome': '5.7 - Inteligência de ameaças',
            'descricao': 'Obter informações sobre ameaças e vulnerabilidades de segurança da informação e torná-las disponíveis para suportar decisões sobre ações de tratamento de risco.',
            'categorias': ['preventivo', 'detectivo', 'corretivo']
        },
        {
            'nome': '5.8 - Segurança da informação no gerenciamento de projetos',
            'descricao': 'Definir e aplicar controles de segurança da informação no gerenciamento de projetos, independentemente do tipo de projeto.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.9 - Inventário de informações e outros ativos associados',
            'descricao': 'Identificar, documentar e manter o registro de informações e ativos associados, bem como os proprietários correspondentes.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.10 - Uso aceitável de informações e outros ativos associados',
            'descricao': 'Definir e implementar regras sobre o uso aceitável de informações e ativos associados para todos os funcionários e prestadores de serviços.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.11 - Devolução de ativos',
            'descricao': 'Exigir que todos os funcionários e prestadores de serviços devolvam todos os ativos da organização no término de seu contrato de trabalho/serviço.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.12 - Classificação das informações',
            'descricao': 'Classificar as informações e ativos associados de acordo com as necessidades de segurança da informação estabelecidas pela organização.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.13 - Rotulagem de informações',
            'descricao': 'Rotular informações e ativos associados em alinhamento com o esquema de classificação de informações da organização.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.14 - Transferência de informações',
            'descricao': 'Controlar a transferência de informações em alinhamento com a classificação e os relativos requisitos de segurança da informação.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.15 - Controle de acesso',
            'descricao': 'Limitar o acesso a informações e ativos de processos de negócios, bem como aos controles e funções de sistema associados.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.16 - Gestão de identidade',
            'descricao': 'Gerenciar identificadores de usuários e associar cada usuario a um único identificador, bem como documentar papéis e responsabilidades.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.17 - Informações de autenticação',
            'descricao': 'Proteger informações de autenticação de usuários através de seu ciclo de vida, incluindo geração, distribuição, armazenamento, uso e redefinição.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.18 - Direitos de acesso',
            'descricao': 'Conceder e revogar o acesso a informações e outros ativos associados para usuários autorizados de forma oportuna e apropriada.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.19 - Segurança da informação nas relações com fornecedores',
            'descricao': 'Incorporar requisitos de segurança da informação e avaliar conformidade em acordos com fornecedores.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.20 - Abordagem da segurança da informação nos contratos de fornecedores',
            'descricao': 'Incluir nas cláusulas de contrato com fornecedores requisitos de segurança da informação relevantes para seus serviços.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.21 - Gestão da segurança da informação na cadeia de fornecimento de TIC',
            'descricao': 'Manter um processo para gerenciar a segurança da informação associada ao uso de produtos e serviços de TIC de fornecedores.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.22 - Monitoramento, análise crítica e gestão de mudanças dos serviços de fornecedores',
            'descricao': 'Monitorar, revisar periodicamente e gerenciar mudanças na prestação de serviços de segurança da informação de fornecedores.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.23 - Segurança da informação para uso de serviços em nuvem',
            'descricao': 'Estabelecer política, salvaguardas e procedimentos para gerenciar o uso seguro de serviços em nuvem.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.24 - Planejamento e preparação da gestão de incidentes de segurança da informação',
            'descricao': 'Preparar a organização para responder a incidentes de segurança da informação planejando uma equipe de resposta e recursos.',
            'categorias': ['corretivo']
        },
        {
            'nome': '5.25 - Avaliação e decisão sobre eventos de segurança da informação',
            'descricao': 'Avaliar eventos de segurança da informação e decidir se eles são classificados como incidentes de segurança da informação.',
            'categorias': ['detectivo']
        },
        {
            'nome': '5.26 - Resposta a incidentes de segurança da informação',
            'descricao': 'Responder a incidentes de segurança da informação aplicando planos e procedimentos de resposta pré-estabelecidos.',
            'categorias': ['corretivo']
        },
        {
            'nome': '5.27 - Aprendizado com incidentes de segurança da informação',
            'descricao': 'Usar informações de incidentes para reforçar as medidas preventivas e melhorar a resposta a incidentes.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.28 - Coleta de evidências',
            'descricao': 'Definir e aplicar procedimentos para identificar, coletar, acessar e preservar informações relacionadas a eventos de segurança da informação, conforme aplicável.',
            'categorias': ['corretivo']
        },
        {
            'nome': '5.29 - Segurança da informação durante a disrupção',
            'descricao': 'Manter a disponibilidade e a segurança de ativos de informação durante interrupções, incluindo durante situações de crise.',
            'categorias': ['preventivo', 'corretivo']
        },
        {
            'nome': '5.30 - Prontidão de TIC para continuidade de negócios',
            'descricao': 'Desenvolver, implantar e testar a prontidão de infraestrutura de TIC para suportar a continuidade de negócios em situações de operação degradada.',
            'categorias': ['corretivo']
        },
        {
            'nome': '5.31 - Requisitos legais, estatutários, regulamentares e contratuais',
            'descricao': 'Identificar e cumprir requisitos legais aplicáveis, estatutários, regulamentares e contratuais relacionados à segurança da informação.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.32 - Direitos de propriedade intelectual',
            'descricao': 'Manter, proteger e fazer cumprir requisitos relativos aos direitos de propriedade intelectual.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.33 - Proteção de registros',
            'descricao': 'Proteger registros contra destruição, falsificação, acesso não autorizado e lançamento não autorizado, incluindo informações armazenadas em nuvem.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.34 - Privacidade e proteção de dados pessoais',
            'descricao': 'Respeitar o direito à privacidade e proteger dados pessoais em alinhamento com os requisitos identificados no princípio de conformidade.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.35 - Análise crítica independente da segurança da informação',
            'descricao': 'Realizar análises críticas independentes periódicas da segurança da informação, incluindo avaliações da política e conformidade.',
            'categorias': ['preventivo', 'corretivo']
        },
        {
            'nome': '5.36 - Conformidade com políticas, regras e normas para segurança da informação',
            'descricao': 'Avaliar a conformidade com política, regras e normas de segurança da informação e tomar medidas corretivas conforme necessário.',
            'categorias': ['preventivo']
        },
        {
            'nome': '5.37 - Documentação dos procedimentos de operação',
            'descricao': 'Documentar, manter e comunicar procedimentos de operação utilizados para controlar sistemas de processamento de informações.',
            'categorias': ['preventivo', 'corretivo']
        },
        # Controles de Pessoas (Seção 6)
        {
            'nome': '6.1 - Seleção',
            'descricao': 'Realizar verificações de antecedentes sobre candidatos para funções que acessarão informações e ativos críticos, consistente com as conclusões da análise de risco.',
            'categorias': ['preventivo']
        },
        {
            'nome': '6.2 - Termos e condições de contratação',
            'descricao': 'Negociar e manter acordos de negociação que incluam obrigações de segurança da informação relevantes com funcionários e prestadores de serviços.',
            'categorias': ['preventivo']
        },
        {
            'nome': '6.3 - Conscientização, educação e treinamento em segurança da informação',
            'descricao': 'Fornecer educação, treinamento e conscientização em segurança da informação apropriados para funcionários e prestadores de serviços.',
            'categorias': ['preventivo']
        },
        {
            'nome': '6.4 - Processo disciplinar',
            'descricao': 'Implementar um processo disciplinar comunicado para funcionários e prestadores de serviços que violem política, regras e normas de segurança da informação.',
            'categorias': ['preventivo']
        },
        {
            'nome': '6.5 - Responsabilidades após encerramento ou mudança da contratação',
            'descricao': 'Manter responsabilidades de segurança da informação, como remoção de direitos de acesso, devolução de ativos e devolução de informações confidenciais.',
            'categorias': ['preventivo']
        },
        {
            'nome': '6.6 - Acordos de confidencialidade ou não divulgação',
            'descricao': 'Implementar e reforçar obrigações de confidencialidade ou não divulgação em alinhamento com as necessidades de segurança da informação da organização.',
            'categorias': ['preventivo']
        },
        {
            'nome': '6.7 - Trabalho remoto',
            'descricao': 'Implementar políticas, procedimentos e controles técnicos para permitir trabalho remoto seguro sobre informações e TIC.',
            'categorias': ['preventivo', 'corretivo']
        },
        {
            'nome': '6.8 - Relato de eventos de segurança da informação',
            'descricao': 'Facilitar o relato de eventos de segurança da informação para que funcionários e prestadores de serviços relatem suspeitas ou confirmar incidentes de segurança.',
            'categorias': ['detectivo']
        },
        # Controles Físicos (Seção 7)
        {
            'nome': '7.1 - Perímetros de segurança física',
            'descricao': 'Estabelecer barreiras e entradas determinadas para criar perímetros de segurança física em torno de áreas que contêm informações e outros ativos associados.',
            'categorias': ['preventivo']
        },
        {
            'nome': '7.2 - Entrada física',
            'descricao': 'Controlar o acesso físico aos edifícios, áreas, salas e outras facilidades de forma apropriada e baseados nos requisitos de segurança.',
            'categorias': ['preventivo']
        },
        {
            'nome': '7.3 - Segurança de escritórios, salas e instalações',
            'descricao': 'Proteger escritórios, salas, dependências e outras facilidades contra acesso, dano e interferência não autorizados.',
            'categorias': ['preventivo']
        },
        {
            'nome': '7.4 - Monitoramento de segurança física',
            'descricao': 'Monitorar atividades não autorizadas em áreas onde informações e ativos estão armazenados e processados.',
            'categorias': ['preventivo', 'detectivo']
        },
        {
            'nome': '7.5 - Proteção contra ameaças físicas e ambientais',
            'descricao': 'Projetar e realizar controles para proteger contra ameaças físicas e ambientais, como desastres naturais.',
            'categorias': ['preventivo']
        },
        {
            'nome': '7.6 - Trabalho em áreas seguras',
            'descricao': 'Estabelecer procedimentos para o uso seguro, alocação de espaço e proteção de suportes de informação em áreas seguras.',
            'categorias': ['preventivo']
        },
        {
            'nome': '7.7 - Mesa limpa e tela limpa',
            'descricao': 'Implementar uma política de mesa limpa para documentos impressos e mídias removíveis e uma política de tela limpa para recursos de processamento de informações.',
            'categorias': ['preventivo']
        },
        {
            'nome': '7.8 - Localização e proteção de equipamentos',
            'descricao': 'Localizar e proteger equipamentos de processamento de informações para reduzir o risco de dano, roubo ou comprometimento não autorizado.',
            'categorias': ['preventivo']
        },
        {
            'nome': '7.9 - Segurança de ativos fora das instalações da organização',
            'descricao': 'Proteger os ativos da organização fora (incluindo informações) localizados fora de suas áreas controladas e manter a proteção apropriada durante o transporte.',
            'categorias': ['preventivo']
        },
        {
            'nome': '7.10 - Mídia de armazenamento',
            'descricao': 'Reusar, remanufaturar, reciclar ou destruir de forma segura a mídia de armazenamento que contém informações de modo a reduzir risco de exposição de informações.',
            'categorias': ['preventivo']
        },
        {
            'nome': '7.11 - Serviços de infraestrutura',
            'descricao': 'Manter a disponibilidade e a proteção dos serviços de utilidade pública que supports sistemas de processamento de informações.',
            'categorias': ['preventivo', 'detectivo']
        },
        {
            'nome': '7.12 - Segurança do cabeamento',
            'descricao': 'Proteger a infraestrutura de cabeamento de telecomunicações, tanto dentro quanto fora dos edifícios, contra intercepção, interferência e dano.',
            'categorias': ['preventivo']
        },
        {
            'nome': '7.13 - Manutenção de equipamentos',
            'descricao': 'Manter equipamentos de forma apropriada para garantir sua disponibilidade contínua e integridade durante sua vida útil.',
            'categorias': ['preventivo']
        },
        {
            'nome': '7.14 - Descarte seguro ou reutilização de equipamentos',
            'descricao': 'Descartar ou preparar para reutilização os equipamentos com segurança quando não forem mais necessários, de modo a reduzir o risco de exposição de informações.',
            'categorias': ['preventivo']
        },
        # Controles Tecnológicos (Seção 8)
        {
            'nome': '8.1 - Dispositivos endpoint do usuário',
            'descricao': 'Implementar técnicas de gerenciamento e segurança em dispositivos do usuário endpoint para reduzir riscos de acesso não autorizado a informações.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.2 - Direitos de acessos privilegiados',
            'descricao': 'Restringir e controlar a alocação e uso de direitos de acesso privilegiados para computadores e sistemas de informação.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.3 - Restrição de acesso à informação',
            'descricao': 'Restringir o acesso a informações e funções de sistemas de informação de acordo com os requisitos de segurança da informação.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.4 - Acesso ao código-fonte',
            'descricao': 'Controlar o acesso ao código-fonte de programas de computador e restringe a modificação de códigos-fonte para reduzir risco de inserção de código malicioso.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.5 - Autenticação segura',
            'descricao': 'Usar mecanismos de autenticação strong para controlar o acesso a sistemas e aplicativos de informação.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.6 - Gestão de capacidade',
            'descricao': 'Monitorar, avaliar, planejar e implementar recursos de computação, de modo a prover a processamento suficiente para atender as demandas.',
            'categorias': ['preventivo', 'detectivo']
        },
        {
            'nome': '8.7 - Proteção contra malware',
            'descricao': 'Detectar e eliminar software malicioso usando ferramentas de proteção e procedimentos apropriados mantidas atualizadas.',
            'categorias': ['preventivo', 'detectivo', 'corretivo']
        },
        {
            'nome': '8.8 - Gestão de vulnerabilidades técnicas',
            'descricao': 'Identificar, avaliar e tomar medidas contra vulnerabilidades técnicas, incluindo aplicação de patches de segurança.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.9 - Gestão de configuração',
            'descricao': 'Estabelecer e manter linhas de base de configuração para sistemas de informação incluindo documentação, avaliação de mudanças e aprovação.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.10 - Exclusão de informações',
            'descricao': 'Remover ou redefinir as informações de forma segura em equipamentos, suportes de informação ou outros ativos para reduzir risco de exposição.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.11 - Mascaramento de dados',
            'descricao': 'Usar técnicas de mascaramento de dados para reduzir a exposição de informações pessoais em ambiente de teste e desenvolvimento.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.12 - Prevenção de vazamento de dados',
            'descricao': 'Detectar e prevenir a transferência, transmissão ou cópia não autorizada de informações através de dispositivos e redes.',
            'categorias': ['preventivo', 'detectivo']
        },
        {
            'nome': '8.13 - Backup das informações',
            'descricao': 'Fazer cópia de backup de informações, software de sistema e software aplicativo e testar regularmente a restauração desses backups.',
            'categorias': ['corretivo']
        },
        {
            'nome': '8.14 - Redundância dos recursos de tratamento de informações',
            'descricao': 'Implementar redundância de recursos de processamento de informações para suportar disponibilidade e operação resiliente.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.15 - Log',
            'descricao': 'Registrar atividades de usuário, exceções, eventos de segurança de informação relevante e gerar evidência de violações com segurança.',
            'categorias': ['detectivo']
        },
        {
            'nome': '8.16 - Atividades de monitoramento',
            'descricao': 'Detectar e relatar anomalias em atividades nas redes que poderão indicar tentativas de hack ou compromiso com segurança.',
            'categorias': ['detectivo', 'corretivo']
        },
        {
            'nome': '8.17 - Sincronização do relógio',
            'descricao': 'Sincronizar os relógios de todos os sistemas de processamento de informação ou redes dentro da organização ou área de segurança relevante.',
            'categorias': ['detectivo']
        },
        {
            'nome': '8.18 - Uso de programas utilitários privilegiados',
            'descricao': 'Prever uso de programas utilitários especializados que são poderosos na sua capacidade para contornar controles de sistema.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.19 - Instalação de software em sistemas operacionais',
            'descricao': 'Controlar a instalação de software em sistemas operacionais de forma apropriada ao modelo de execução permitido do ambiente de TIC.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.20 - Segurança de redes',
            'descricao': 'Segmentar a rede da organização em grupos de informação, usuários e sistemas de informação separados e implementar salvaguardas entre segmentos.',
            'categorias': ['preventivo', 'detectivo']
        },
        {
            'nome': '8.21 - Segurança dos serviços de rede',
            'descricao': 'Identificar, implementar e manter mecanismos de segurança para serviços de rede para garantir disponibilidade segura e apropriada de serviços.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.22 - Segregação de redes',
            'descricao': 'Agrupar e controlar a transmissão de dados eletrônicos entre grupos de máquinas informáticas contendo informações de diferentes categorias.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.23 - Filtragem da web',
            'descricao': 'Implementar filtragem de conteúdo baseado em web através de sistemas de informação para evitar acesso a sites considerados prejudiciais à segurança.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.24 - Uso de criptografia',
            'descricao': 'Classificar informações e definir requisitos de criptografia para proteção em repouso e em transito com base na classificação e risco descoberto.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.25 - Ciclo de vida de desenvolvimento seguro',
            'descricao': 'Estabelecer e implementar regras de desenvolvimento seguro de software incluindo requisitos de privacidade, projeto, construção, teste e release.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.26 - Requisitos de segurança da aplicação',
            'descricao': 'Definir, documentar, revisar e aprovar requisitos de segurança da informação para novas aplicações ou enhancements aos sistemas de informação.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.27 - Princípios de arquitetura e engenharia de sistemas seguros',
            'descricao': 'Estabelecer, documentar, manter e comunicar princípios de arquitetura segura e engenharia de sistemas para design e desenvolvimento de sistemas.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.28 - Codificação segura',
            'descricao': 'Implementar práticas de programação segura e standards de codificação para reduzir vulnerabilidades potenciais de segurança nos programas.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.29 - Testes de segurança em desenvolvimento e aceitação',
            'descricao': 'Implementar testes de segurança em durante fases de desenvolvimento e aceitação de novas aplicações ou systems.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.30 - Desenvolvimento terceirizado',
            'descricao': 'Estabelecer e manter processos de negociação e contratos que abordem segurança da informação no desenvolvimento de software de terceiros.',
            'categorias': ['preventivo', 'detectivo']
        },
        {
            'nome': '8.31 - Separação dos ambientes de desenvolvimento, teste e produção',
            'descricao': 'Manter ambientes de desenvolvimento, teste e produção separados para reduzir risco de acesso não autorizado ou alteração em ambiente de produção.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.32 - Gestão de mudanças',
            'descricao': 'Controlar modificações aos sistemas de informação incluindo procedimentos, aprovação, documentação e testes de mudanças de segurança.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.33 - Informações de testes',
            'descricao': 'Proteger, segregar e controlar informações usadas para teste de forma apropriada ao seu nível de classificação.',
            'categorias': ['preventivo']
        },
        {
            'nome': '8.34 - Proteção de sistemas de informação durante os testes de auditoria',
            'descricao': 'Implementar salvaguardas durante testes de sistema e auditoria de segurança para proteger contra acesso ou modificação não autorizada.',
            'categorias': ['preventivo']
        },
    ]

    for controle_data in CONTROLES_ISO27001:
        nome = controle_data['nome']
        descricao = controle_data['descricao']
        categorias_tipos = controle_data['categorias']

        # Create or get the control
        controle, created = Controle.objects.get_or_create(
            nome=nome,
            defaults={'descricao': descricao}
        )

        # Add categories to the control
        for categoria_tipo in categorias_tipos:
            try:
                categoria = CategoriaControle.objects.get(tipo=categoria_tipo)
                controle.categorias.add(categoria)
            except CategoriaControle.DoesNotExist:
                pass


def reverse_iso27001_controls(apps, schema_editor):
    """Remove ISO 27001 controls (reverse operation)."""
    Controle = apps.get_model('ismsapp', 'Controle')
    # Delete all controls that start with section numbers (5., 6., 7., 8.)
    Controle.objects.filter(nome__regex=r'^[5678]\.\d+').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ismsapp', '0034_inicializar_categoria_controle'),
    ]

    operations = [
        migrations.RunPython(load_iso27001_controls, reverse_iso27001_controls),
    ]
