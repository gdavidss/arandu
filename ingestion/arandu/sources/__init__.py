from arandu.sources.bcb import fetch_bcb_sgs
from arandu.sources.bcb_mpv import fetch_bcb_mpv_cartoes, fetch_bcb_mpv_monthly
from arandu.sources.bcb_olinda import fetch_bcb_olinda_expectativas
from arandu.sources.bcb_spi import fetch_bcb_spi_pix
from arandu.sources.comexstat import fetch_comexstat
from arandu.sources.ecb_fx import fetch_ecb_fx
from arandu.sources.ibge import fetch_ibge_sidra
from arandu.sources.pix_dict import fetch_pix_dict_usuarios
from arandu.sources.rfb_cnae import fetch_rfb_cnae
from arandu.sources.static_table import fetch_static_table
from arandu.sources.tesouro import fetch_tesouro_series

CONNECTORS = {
    "bcb_sgs": fetch_bcb_sgs,
    "bcb_olinda_expectativas": fetch_bcb_olinda_expectativas,
    "bcb_spi_pix": fetch_bcb_spi_pix,
    "bcb_mpv_monthly": fetch_bcb_mpv_monthly,
    "bcb_mpv_cartoes": fetch_bcb_mpv_cartoes,
    "pix_dict_usuarios": fetch_pix_dict_usuarios,
    "tesouro_series": fetch_tesouro_series,
    "ibge_sidra": fetch_ibge_sidra,
    "comexstat": fetch_comexstat,
    "ecb_fx": fetch_ecb_fx,
    "rfb_cnae": fetch_rfb_cnae,
    "static_table": fetch_static_table,
}
