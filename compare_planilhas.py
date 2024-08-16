class Compare:
  def __init__(self):
    self.list_dominios_planilha1 = []
    self.list_contratos_planilha2 = []

    self.list_contratos_planilha1 = []
    self.list_dominios_planilha2 = []

  def verify_dominios(self):
    for dominio in self.list_dominios_planilha1:
      if dominio not in self.list_dominios_planilha2:
        print(f"Dominio {dominio} não encontrado na planilha 2")

  def verify_contratos(self):
    for contrato in self.list_contratos_planilha1:
      if contrato not in self.list_contratos_planilha2:
        print(f"Contrato {contrato} não encontrado na planilha 2")

  def compare_dominio_index_igual_contrato(self):
    for dominio, contrato in zip(self.list_dominios_planilha1, self.list_contratos_planilha1):
      if dominio not in self.list_dominios_planilha2:
        print(f"Dominio {dominio} não encontrado na planilha 2")
      if contrato not in self.list_contratos_planilha2:
        print(f"Contrato {contrato} não encontrado na planilha 2")
      
      index_domain_1 = self.list_dominios_planilha1.index(dominio)
      index_domain_2 = self.list_dominios_planilha2.index(dominio)
      index_contract_1 = self.list_contratos_planilha1.index(contrato)
      index_contract_2 = self.list_contratos_planilha2.index(contrato)

      if contrato != self.list_contratos_planilha2[index_domain_2]:
        print(f"Contrato {contrato} não está no mesmo index do dominio {dominio} na planilha 2")
      
      