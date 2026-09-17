# API de Gestão de Identidades no Active Directory


## Operações internas da aplicação:


- Criar OU
- Alterar/Mover OU
- Criar Pessoa
- Alterar Pessoa
- Remover Pessoa
- Mover Pessoa para outra OU
- Bloquear/Inativar Pessoa


## Operações da API (expostas por REST):


### Unidades

- Criar órgão de Administração Direta (POST /estrutura/unidades/direta)

	- Cria uma OU dentro do nó correto da administração direta, preenche os atributos padronizados para OU deste tipo
	- Sugestão de atributo padronizado: pmlNomeOrgao (nome real do órgão na estrutura da Prefeitura)
	- Inserir OUs no AD: 
		- PML -> Operativos -> Direta -> <novo nó>
		- PML -> Inoperantes -> Direta -> <novo nó>
	- Regras:
		- Nome da OU totalmente em uppercase
		- Nome da OU mínimo 2 caracteres

---


- Alterar Órgão de Administração Direta (PATCH /estrutura/unidades/direta)

	- Altera somente o que puder ser alterado em um nó de OU da administração direta
	- Sugestão inicial: poder alterar o valor de pmlNomeOrgao
	- Alterar no AD:
		- PML -> Operativos -> Direta -> <nó alterado>
		- PML -> Inoperantes -> Direta -> <nó alterado>
	- Regras:
		- Não é possível alterar desincorporadas (aceita somente OUs que estão em Operativos -> Direta)


---


- Criar Órgão de Administração Indireta (POST /estrutura/unidades/indireta)

	- Cria uma OU dentro do nó correto da administração indireta, preenche os atributos padronizados para OU deste tipo
	- Sugestão de atributo padronizado: pmlNomeOrgao (nome real do órgão na estrutura da Prefeitura)
	- Inserir do AD: 
		- PML -> Operativos -> Indireta -> <novo nó>
		- PML -> Inoperantes -> Indireta -> <novo nó>
	- Regras:
		- Nome da OU totalmente em uppercase
		- Nome da OU mínimo 2 caracteres


---


- Alterar Órgão de Administração Indireta (PATCH /estrutura/unidades/indireta)

	- Altera somente o que puder ser alterado em um nó de OU da administração indireta
	- Sugestão inicial: poder alterar o valor de pmlNomeOrgao
	- Alterar no AD:
		- PML -> Operativos -> Indireta -> <nó alterado>
		- PML -> Inoperantes -> Indireta -> <nó alterado>
	- Regras:
		- Não é possível alterar desincorporadas (aceita somente OUs que estão em Operativos -> Indireta)


---


- Criar Terceirizada (POST /estrutura/unidades/terceirizada)

	- Cria uma OU dentro do nó correto das Terceirizadas, preenche os atributos padronizados para OU deste tipo
	- Sugestão de atributo padronizado: pmlNomeOrgao (nome real do órgão na estrutura da Prefeitura)
	- Inserir do AD: 
		- PML -> Operativos -> Terceirizadas -> <novo nó>
		- PML -> Inoperantes -> Terceirizadas -> <novo nó>
	- Regras:
		- Nome da OU totalmente em uppercase
		- Nome da OU mínimo 2 caracteres


---


- Alterar Terceirizada (PATCH /estrutura/unidades/terceirizada)

	- Altera somente o que puder ser alterado em um nó de OU da administração indireta
	- Sugestão inicial: poder alterar o valor de pmlNomeOrgao
	- Alterar no AD:
		- PML -> Operativos -> Terceirizadas -> <nó alterado>
		- PML -> Inoperantes -> Terceirizadas -> <nó alterado>
	- Regras:
		- Não é possível alterar desincorporadas (aceita somente OUs que estão em Operativos -> Terceirizadas)


---


- Criar Preposto (POST /estrutura/unidades/preposto)

	- Cria uma OU dentro do nó correto das Terceirizadas, preenche os atributos padronizados para OU deste tipo
	- Sugestão de atributo padronizado: pmlNomeOrgao (nome real do órgão na estrutura da Prefeitura)
	- Inserir do AD: 
		- PML -> Operativos -> Prepostos -> <novo nó>
		- PML -> Inoperantes -> Prepostos -> <novo nó>
	- Regras:
		- Nome da OU totalmente em uppercase
		- Nome da OU mínimo 2 caracteres


---


- Alterar Preposto (PATCH /estrutura/unidades/preposto)

	- Altera somente o que puder ser alterado em um nó de OU da administração indireta
	- Sugestão inicial: poder alterar o valor de pmlNomeOrgao
	- Alterar no AD:
		- PML -> Operativos -> Prepostos -> <nó alterado>
		- PML -> Inoperantes -> Prepostos -> <nó alterado>
	- Regras:
		- Não é possível alterar desincorporadas (aceita somente OUs que estão em Operativos -> Prepostos)


---


- Desincorporar Órgão da Administração Direta (DELETE /estrutura/unidades/direta)

	- Move a OU de um órgão da Administração Direta do Ramo "Operativos" para o ramo "Desincorporados"
	- Registra atributo documentando a fato: pmlDesincorporadoInstrumento, pmlDesincorporadoData
	- Mover no AD:
		De: PML -> Operativos -> Direta -> <nó destituído>  / Para: PML -> Desincorporados -> Direta -> <nó destituído>


---


- Desincorporar Órgão da Administração Indireta (DELETE /estrutura/unidades/indireta)

	- Move a OU de um órgão da Administração Direta do Ramo "Operativos" para o ramo "Desincorporados"
	- Registra atributo documentando a fato: pmlDesincorporadoInstrumento, pmlDesincorporadoData
	- Mover no AD:
		De: PML -> Operativos -> Indireta -> <nó destituído>  / Para: PML -> Desincorporados -> Indireta -> <nó destituído>


---


- Desincorporar Terceirizada (DELETE /estrutura/unidades/terceirizada)

	- Move a OU Terceirizada do Ramo "Operativos" para o ramo "Desincorporados"
	- Registra atributo documentando a fato: pmlDesincorporadoInstrumento, pmlDesincorporadoData
	- Mover no AD:
		De: PML -> Operativos -> Terceirizadas -> <nó destituído>  / Para: PML -> Desincorporados -> Terceirizadas -> <nó destituído>


---


- Desincorporar Preposto (DELETE /estrutura/unidades/preposto)

	- Move a OU Preposto do Ramo "Operativos" para o ramo "Desincorporados"
	- Registra atributo documentando a fato: pmlDesincorporadoInstrumento, pmlDesincorporadoData
	- Mover no AD:
		De: PML -> Operativos -> Prepostos -> <nó destituído>  / Para: PML -> Desincorporados -> Prepostos -> <nó destituído>


### Identidades


- Criar Estagiário (POST /identidade/humanos/estagio)

	- Cria humano estagiário na unidade indicada, dentro da nó "Inoperantes"
	- Bloqueia o humano criado
	- Regras:
		- samAccountName = mínimo 5 caracteres. (a-zA-Z){2,10}'\.'(a-z-A-Z){2,10}
		- name = mínimo 5 caracteres. ^[A-Z][a-z]+\s[A-Z][a-z]+$


---


- Alterar Estagiário (PATCH /identidade/humanos/estagio/{id})

	- Altera somente os atributos mutáveis da identidade do estagiário
	- Regras:
		- Não é possível alterar fora da árvore Operativos

---


- Destituir Estagiário (DELETE /identidade/humanos/estagio/{id})

	- Move a pessoa para a mesma OU da árvore "Inoperantes"
	- Bloqueia a pessoa
	- Registra atributo documentando a fato: pmlDestituidoInstrumento, pmlDestituidoData
	- Regras:
		- Somente é possível destituir da árvore "Operativos"


---


- Criar Servidor de Carreira (POST /identidade/humanos/carreira)

	- Cria humano de carreira na unidade indicada, dentro da árvore "Inoperantes"
	- Bloqueia o humano criado
	- Regras:
		- samAccountName = mínimo 5 caracteres. (a-zA-Z){2,10}'\.'(a-z-A-Z){2,10}
		- name = mínimo 5 caracteres. ^[A-Z][a-z]+\s[A-Z][a-z]+$


--


- Alterar Servidor de Carreira (PATCH /identidade/humanos/carreira/{id})

	- Altera somente os atributos mutáveis da identidade do servidor de carreira
	- Regras:
		- Não é possível alterar fora da árvore Operativos


--


- Destituir Servidor de Carreira (DELETE /identidade/humanos/carreira/{id})

	- Move a pessoa para a mesma OU da árvore "Inoperantes"
	- Bloqueia a pessoa
	- Registra atributo documentando a fato: pmlDestituidoInstrumento, pmlDestituidoData
	- Regras:
		- Somente é possível destituir da árvore "Operativos"


--


- Criar Comissionado (POST /identidade/humanos/comissionado)

	- Cria humano comissionado na unidade indicada, dentro da árvore "Inoperantes"
	- Bloqueia o humano criado
	- Regras:
		- samAccountName = mínimo 5 caracteres. (a-zA-Z){2,10}'\.'(a-z-A-Z){2,10}
		- name = mínimo 5 caracteres. ^[A-Z][a-z]+\s[A-Z][a-z]+$


--


- Alterar Comissionado (PATCH /identidade/humanos/comissionado/{id})

	- Altera somente os atributos mutáveis da identidade do servidor comissionado
	- Regras:
		- Não é possível alterar fora da árvore Operativos


--


- Destituir Comissionado (DELETE /identidade/humanos/comissionado/{id})

	- Move a pessoa para a mesma OU da árvore "Inoperantes"
	- Bloqueia a pessoa
	- Registra atributo documentando a fato: pmlDestituidoInstrumento, pmlDestituidoData
	- Regras:
		- Somente é possível destituir da árvore "Operativos"


--


- Criar Não Humano (POST /identidade/naohumanos)

	- Cria não-humano na unidade indicada, dentro da árvore "Inoperantes"
	- Bloqueia o humano criado
	- Registra atributo documentando a fato: pmlNaoHumanoTipo
	- Regras:
		- samAccountName = mínimo 5 caracteres. 'nhu\.'(a-zA-Z){2,10}'\.'(a-z-A-Z){2,10}
		- name = mínimo 5 caracteres. ^[a-z]{5,}


--


- Alterar Não Humano (PATCH /identidade/naohumanos/{id})

	- Altera somente os atributos mutáveis da identidade do não humano
	- Regras:
		- Não é possível alterar fora da árvore "Desincorporados"


--


- Bloquear Não Humano (PATCH /identidade/naohumanos/{id})

	- Bloqueia a autenticação do não humano
	- Regras:
		- Não é possível alterar fora da árvore "Desincorporados"


--


- Remover Não Humano (DELETE /identidade/naohumanos/{id})

	- Remove fisicamente o não humano da base do Active Directory


--


- Bloquear Humano (PATCH /identidade/humanos/{id})

	- Bloqueia a autenticação do humano
	- Regras:
		- Não é possível alterar fora da árvore "Desincorporados"


--



- Remover Humano (DELETE /identidade/humanos/{id})

	- Remove fisicamente o humano da base do Active Directory