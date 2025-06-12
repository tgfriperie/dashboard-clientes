import pandas as pd

# === CONFIGURAÇÕES ===
arquivo_entrada = r"C:\Users\Windows\Desktop\Apoio dental\base nova\CLIENTES_COM_VARIAS_COMPRAS.xlsx"
arquivo_saida = r"C:\Users\Windows\Desktop\Apoio dental\base nova\relatorio_clientes_2_compra.xlsx"

# === 1. Leitura do Excel ===
df = pd.read_excel(arquivo_entrada)

# === 2. Normalização das colunas ===
df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('  ', ' ', regex=False)

# === 3. Identificação única do cliente ===
df['Cliente_ID'] = df['Nome Completo / Razão Social'].fillna(df['e-mail 1'])

# === 4. Agrupamento por mês/cliente para contar compras ===
compras_por_cliente = (
    df.groupby(['Ano da Última Compra', 'Mês da Última Compra', 'Física / Jurídica', 'Atacado / Varejo', 'Cliente_ID'])
    .size()
    .reset_index(name='Qtd_Compras')
)

# === 5. Filtrar quem comprou exatamente 1 vez no mês ===
clientes_1_compra = compras_por_cliente[compras_por_cliente['Qtd_Compras'] == 1]

# === 6. Merge com dados originais para recuperar valor da compra ===
df_merge = pd.merge(
    clientes_1_compra,
    df,
    on=['Ano da Última Compra', 'Mês da Última Compra', 'Física / Jurídica', 'Atacado / Varejo', 'Cliente_ID'],
    how='left'
)

# === 7. Agrupamento final com contagem e ticket médio ===
relatorio = (
    df_merge.groupby(['Ano da Última Compra', 'Mês da Última Compra', 'Física / Jurídica', 'Atacado / Varejo'])
    .agg(
        Qtd_Clientes=('Cliente_ID', 'nunique'),
        Ticket_Medio=('Valor Compra', 'mean')
    )
    .reset_index()
    .sort_values(['Ano da Última Compra', 'Mês da Última Compra'])
)

# === 8. Exporta para Excel ===
relatorio.to_excel(arquivo_saida, index=False)

print("✅ Relatório gerado com sucesso em:")
print(arquivo_saida)
