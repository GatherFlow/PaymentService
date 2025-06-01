
from aiomonobnk import MonoPay

from config import get_settings


mono_client = MonoPay(token=get_settings().monopay.token)
