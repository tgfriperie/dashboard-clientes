import pandas as pd

arquivo_entrada = r"C:\Users\Windows\Desktop\Apoio dental\base nova\CLIENTES_COM_UMA_COMPRA.xlsx"
df = pd.read_excel(arquivo_entrada)

print("Colunas encontradas:")
for col in df.columns:
    print(f"'{col}'")
