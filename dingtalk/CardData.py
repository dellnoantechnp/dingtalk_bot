from alibabacloud_dingtalk.im_1_0.models import (InteractiveCardCreateInstanceRequestCardData,
                                                 SendInteractiveCardRequestCardData,
                                                 PrivateDataValue, UpdateInteractiveCardRequestCardData)
from typing import Dict
import json


class CardData(SendInteractiveCardRequestCardData, PrivateDataValue, UpdateInteractiveCardRequestCardData):
    """
    docs: https://open.dingtalk.com/document/orgapp/send-interactive-dynamic-cards-1#h2-vnz-jdj-vrc
    """

    def __init__(self, sys_full_json_obj: Dict[str, str | bool]):
        """初始化 CardData 类相关的数据

        :param sys_full_json_obj: 自定义卡片模板变量结构
        """
        self.card_media_id_param_map = dict()
        self.card_param_map = dict()
        super().__init__(card_param_map=self.card_param_map,
                         card_media_id_param_map=self.card_media_id_param_map)

        self.card_param_map["sys_full_json_obj"] = json.dumps(sys_full_json_obj)

    def get_card_content(self):
        return json.dumps(self.card_param_map, ensure_ascii=True)

    def __str__(self):
        return self.card_param_map["sys_full_json_obj"]


if __name__ == "__main__":
    a = CardData(sys_full_json_obj=dict(abc=4, bcd="中文🧡"))
    print(a.get_card_content())
