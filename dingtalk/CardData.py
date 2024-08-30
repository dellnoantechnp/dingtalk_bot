from alibabacloud_dingtalk.im_1_0.models import (InteractiveCardCreateInstanceRequestCardData,
                                                 SendInteractiveCardRequestCardData)
from typing import Dict
import json


class CardData(SendInteractiveCardRequestCardData):
    """
    docs: https://open.dingtalk.com/document/orgapp/send-interactive-dynamic-cards-1#h2-vnz-jdj-vrc
    """

    def __init__(self, sys_full_json_obj: Dict[str, str]):
        """初始化 CardData 类相关的数据

        :param sys_full_json_obj: 自定义卡片模板变量结构
        """
        super().__init__(card_param_map={},
                         card_media_id_param_map={})

        #self.sys_full_json_obj = sys_full_json_obj
        self.card_param_map["sys_full_json_obj"] = sys_full_json_obj.__str__()

    def get_card_content(self):
        return json.dumps(self.card_param_map, indent=4, ensure_ascii=True)


if __name__ == "__main__":
    a = CardData(sys_full_json_obj=dict(abc=4, bcd="中文🧡"))
    print(a.get_card_content())
