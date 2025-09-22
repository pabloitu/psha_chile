import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

sns.set_style("darkgrid", {"axes.facecolor": ".9", 'font.family': 'Ubuntu'})

data = pd.read_csv('../data/hazard_condom.csv')


data['Hazard1'].hist(bins=50)
plt.xlabel('PGA (10% - 50 yr.)')
plt.ylabel('Condominium count')
plt.title('Renta Condominium Portfolio - PGA Histogram')
plt.savefig('histogram_pga.png', dpi=300)
plt.show()

plt.plot(data['Hazard1'], data['POL_MONTO_']*40/1000, 'o', markersize=4, alpha=0.7,
                            markeredgecolor='white', label='Analyzed Asset')
plt.title('Renta Condominium Portfolio')
plt.legend()
plt.ylabel('TIV (1000 USD)')
plt.xlabel('PGA (10% - 50 yr.)')
plt.savefig('PGA_vs_USD.png', dpi=300)

plt.show()