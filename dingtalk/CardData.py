from alibabacloud_dingtalk.im_1_0.models import InteractiveCardCreateInstanceRequestCardData, SendInteractiveCardRequestCardData


class CardData(SendInteractiveCardRequestCardData):
    """
    docs: https://open.dingtalk.com/document/orgapp/send-interactive-dynamic-cards-1#h2-vnz-jdj-vrc
    """
    def __init__(self, sys_full_json_obj: dict):
        self.sys_full_json_obj = sys_full_json_obj
        pass