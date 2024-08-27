from alibabacloud_dingtalk.im_1_0.models import (InteractiveCardCreateInstanceRequestCardData,
                                                 SendInteractiveCardRequestCardData)
from typing import Dict


class CardData(SendInteractiveCardRequestCardData):
    """
    docs: https://open.dingtalk.com/document/orgapp/send-interactive-dynamic-cards-1#h2-vnz-jdj-vrc
    """

    def __init__(self, sys_full_json_obj: Dict[str: str]):
        super().__init__(card_param_map={},
                         card_media_id_param_map={})
        self.sys_full_json_obj = sys_full_json_obj
        self.card_param_map["sys_full_json_obj"] = sys_full_json_obj.__str__()

    def get_card_content(self):
        return self.sys_full_json_obj