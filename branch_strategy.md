# Estratégia de Branches para o Projeto

## Estrutura de Branches

Implementaremos a seguinte estrutura de branches para o projeto:

### Branches Principais
- **main**: Branch de produção. Apenas código estável e testado deve ser mesclado aqui. Esta branch é a que será usada para deploys em produção.
- **develop**: Branch principal de desenvolvimento onde as features são integradas antes de irem para produção.

### Branches Temporárias
- **feature/nome-da-feature**: Para desenvolvimento de novas funcionalidades.
- **bugfix/nome-do-bug**: Para correção de bugs.
- **hotfix/nome-do-hotfix**: Para correções urgentes diretamente aplicadas à branch principal.
- **release/versão**: Para preparar uma nova versão para lançamento.

## Fluxo de Trabalho

1. **Desenvolvimento de Novas Funcionalidades**:
   - Criar uma branch `feature/nome-da-feature` a partir de `develop`
   - Desenvolver a funcionalidade
   - Fazer merge para `develop` quando pronta

2. **Correção de Bugs**:
   - Criar uma branch `bugfix/nome-do-bug` a partir de `develop`
   - Corrigir o bug
   - Fazer merge para `develop`

3. **Preparação para Release**:
   - Criar uma branch `release/X.Y.Z` a partir de `develop`
   - Fazer ajustes finais, testes e correções
   - Fazer merge para `main` e `develop`
   - Criar tag com a versão

4. **Correções Urgentes em Produção**:
   - Criar uma branch `hotfix/nome-do-hotfix` a partir de `main`
   - Corrigir o problema
   - Fazer merge para `main` e `develop`
   - Atualizar a tag de versão

## Convenções de Versionamento

Usaremos o padrão Semantic Versioning (SemVer) para as versões:

- **X.Y.Z** onde:
  - **X**: Versão principal (major) - Mudanças incompatíveis com versões anteriores
  - **Y**: Versão secundária (minor) - Adições de funcionalidades compatíveis
  - **Z**: Versão de patch - Correções de bugs compatíveis

## Implementação

Para implementar esta estratégia nos repositórios existentes:

1. **Frontend (ap-frontend)**:
   - Criar branch `develop` a partir da `main` atual
   - Configurar proteções para a branch `main`
   - Criar milestone v1.0.0 para a versão atual estável
   - Criar milestone v1.1.0 para as próximas funcionalidades

2. **Backend (ap-backend)**:
   - Mesmo procedimento do frontend
   - Garantir que as versões sejam coerentes entre os dois repositórios

## Comandos para Implementação

```bash
# Frontend
cd ap-frontend
git checkout -b develop
git push -u origin develop

# Backend
cd ../ap-backend
git checkout -b develop
git push -u origin develop
```

## Benefícios

- **Estabilidade**: A branch `main` sempre contém código pronto para produção.
- **Isolamento**: Desenvolvimento ocorre separadamente da produção.
- **Controle de versão**: Cada versão é claramente definida e rastreável.
- **Colaboração**: Múltiplos desenvolvedores podem trabalhar em diferentes funcionalidades sem conflitos. 