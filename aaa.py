import pandas as pd

# Replace 'your_file.xlsx' with the actual path to your Excel file
file_path = 'C:\Users\Korisnik\Desktop\privatni_projekti\\football-app\\football_app\England\LIGA\England-Premier Leauge.xlsx'

# Read the Excel file and select the "Fix" sheet
df = pd.read_excel(file_path, sheet_name='Fix')

# Print the values in the "Fix" sheet
print(df)