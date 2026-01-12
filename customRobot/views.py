import datetime
import json
import logging
import os
import re
import time

import dingtalk_stream
from alibabacloud_dingtalk.card_1_0 import models as dingtalkcard__1__0_models
from alibabacloud_dingtalk.card_1_0.client import Client as dingtalkcard_1_0Client
from alibabacloud_dingtalk.im_1_0 import models as dingtalkim__1__0_models
from alibabacloud_dingtalk.im_1_0.client import Client as dingtalkim_1_0Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from dingtalk.Card import Card, CardData
from dingtalk.DingtalkBase import DingtalkBase
from dingtalk.Models.dingtalk_card_struct import SpaceTypeEnum
from dingtalk.services.argo_workflows import ArgoWorkflowsService

from dingtalk.services.dingtalk_client import DingTalkClient
from . import EchoMarkdownHandler
from dingtalk.WatchJobStatus import gen_chart_data, get_task_job_from_workflows_api, settings
# from django_q.tasks import schedule
# from django_q.models import Schedule, Task
from dingtalk.tasks.TaskStatusOfWorkflowsJob import test

from dingtalk.CardDataStore import CardDataStore

logger = logging.getLogger("dingtalk_bot")

def index(request):
    return JsonResponse({"foo": "bar"})


def setup_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s %(name)-8s %(levelname)-8s %(message)s [%(filename)s:%(lineno)d]'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


## 示例：https://github.com/open-dingtalk/dingtalk-tutorial-python
def dingtalk_stream1(request):
    logger = setup_logger()

    credential = dingtalk_stream.Credential("dino0gpks7ih", "utI4JqkOzvuj")
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC,
                                     EchoMarkdownHandler.EchoMarkdownHandler(logger))
    client.start_forever()


def create_imclient() -> dingtalkim_1_0Client:
    """
    使用 Token 初始化账号Client
    @return: Client
    @throws Exception
    """
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    return dingtalkim_1_0Client(config)


def create_card_client() -> dingtalkcard_1_0Client:
    """
    使用 Token 初始化账号Client
    @return: Client
    @throws Exception
    """
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    return dingtalkcard_1_0Client(config)


@csrf_exempt
def dingtalk_test(request):
    logger = logging.getLogger("dingtalk_bot")
    logger.debug("appKey:" + settings.DINGTALK_CLIENT_ID + " appSecret:" + settings.DINGTALK_CLIENT_SECRET)
    dd = DingtalkBase(settings.DINGTALK_CLIENT_ID, settings.DINGTALK_CLIENT_SECRET)
    token = dd.access_token
    logger.info("token: " + token)
    time_tag = int(time.time() * 1000)
    # card_template_id = "bd57beb1-d127-45e5-92d4-81277c59c87b.schema"
    card_template_id = "98a61096-31e1-4611-be4e-b1d2f6897225.schema"
    out_track_id = f"{card_template_id}.{time_tag}"

    send_interactive_card_headers = dingtalkim__1__0_models.SendInteractiveCardHeaders()
    send_interactive_card_headers.x_acs_dingtalk_access_token = token

    send_interactive_card_request = dingtalkim__1__0_models.SendInteractiveCardRequest()
    send_interactive_card_request.card_template_id = card_template_id
    # send_interactive_card_request.card_template_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema"
    # send_interactive_card_request.out_track_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema.1715069378009"
    send_interactive_card_request.out_track_id = out_track_id
    send_interactive_card_request.robot_code = "dingqkoo0gpksjflc7ih"
    send_interactive_card_request.open_conversation_id = "cidUQXUpOwFEbiRNp87JyFE3w=="
    send_interactive_card_request.conversation_type = 1

    card_data = dingtalkim__1__0_models.SendInteractiveCardRequestCardData()
    object_string = {
        "markdown_content": "#### Tiltle\n* 123\n* 456",
        "approve_count": 10,
        "reject_count": 3,
        "card_title": "本次发布更新",
        "markdown_title": "本周发布commit汇总",
        "markdown": "4567"
    }.__str__()
    card_data.card_param_map = {"title": "朱小志提交的财务报销", "detailUrl": "https://dingtalk.com",
                                "status": "pending", "sys_full_json_obj": object_string}
    card_data.card_media_id_param_map = {}
    # send_interactive_card_request.card_data = dingtalkim__1__0_models.InteractiveCardCreateInstanceRequestCardData({"title": "123", "detailUrl": "https://dingtalk.com", "status": "pending", "sys_ful_json_obj": "{}"})
    # send_interactive_card_request.card_data = {"cardParamMap": {"title": "朱小志提交的财务报销", "detailUrl": "https://dingtalk.com", "status": "pending", "sys_full_json_obj": "{}"}}
    send_interactive_card_request.card_data = card_data

    ## Card
    create_and_deliver_headers = dingtalkcard__1__0_models.CreateAndDeliverHeaders()
    create_and_deliver_headers.x_acs_dingtalk_access_token = dd.access_token
    create_and_deliver_request = dingtalkcard__1__0_models.CreateAndDeliverRequest()
    create_and_deliver_request.card_template_id = card_template_id
    # send_interactive_card_request.card_template_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema"
    # send_interactive_card_request.out_track_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema.1715069378009"
    create_and_deliver_request.out_track_id = out_track_id
    create_and_deliver_request.robot_code = "dingqkoo0gpksjflc7ih"
    create_and_deliver_request.open_conversation_id = "cidUQXUpOwFEbiRNp87JyFE3w=="
    create_and_deliver_request.conversation_type = 1
    create_and_deliver_request.open_space_id = "dtv1.card//IM_SINGLE.cidUQXUpOwFEbiRNp87JyFE3w=="
    create_and_deliver_request.callback_type = "STREAM"
    # create_and_deliver_request.callback_type = "HTTP"

    im_group_deliver_model = dingtalkcard__1__0_models.CreateAndDeliverRequestImGroupOpenDeliverModel()
    im_group_deliver_model.robot_code = "dingqkoo0gpksjflc7ih"
    im_group_open_space_model = dingtalkcard__1__0_models.CreateCardRequestImGroupOpenSpaceModel()
    im_group_open_space_model.support_forward = True

    create_and_deliver_request.im_group_open_deliver_model = im_group_deliver_model
    create_and_deliver_request.im_group_open_space_model = im_group_open_space_model
    create_and_deliver_request.card_data = card_data

    logger.warning(send_interactive_card_request.from_map())

    im_client = create_imclient()
    card_client = create_card_client()
    try:
        logger.info("卡片创建和投递")
        # resp: dingtalkcard__1__0_models.CreateAndDeliverResponse = card_client.create_and_deliver_with_options(
        #     create_and_deliver_request,
        #     create_and_deliver_headers,
        #     util_models.RuntimeOptions()
        # )

        logger.info("卡片消息投递到聊天")
        resp: dingtalkim__1__0_models.SendInteractiveCardResponse = im_client.send_interactive_card_with_options(
            send_interactive_card_request,
            send_interactive_card_headers,
            util_models.RuntimeOptions()
        )
    except Exception as err:
        logger.error(err)

    # 更新卡片内容
    try:
        time.sleep(5)
        update_card_data = dingtalkim__1__0_models.SendInteractiveCardRequestCardData()
        object_string = {
            "markdown_content": "#### Tiltle\n* 123\n* 456",
            "approve": 0,
            "reject": 0,
            "card_title": "本次发布更新",
            "markdown_title": "本周发布commit汇总",
            "markdown": "4567121231231",
            "approve_max": 10,
            "reject_max": 2,
            "card_ref_link": "https://workflows.poc.jagat.io/workflows/workflows?&limit=50",
            "repository": "utown-biz",
            "project_id": "2165698",
            "author": "任贵生",
            "branch": "master",
            "commit_sha": "e8c15b9aa5debe96dd9f6441ba682f4edd064b30",
            "environment": "poc",
            "chart_data": {
                "type": "pieChart",
                "config": {
                    "pieChartStyle": "percentage",
                    "xAxisConfig": {},
                    "padding": [
                        0,
                        5,
                        0,
                        0
                    ],
                    "yAxisConfig": {},
                    "color": [
                        "#329FFE",
                        "#1AC681",
                        "#FD9E5E",
                        "#C766EC",
                        "#98D333",
                        "#5A88FE",
                        "#FE7A66",
                        "#ED63AD",
                        "#A564ED",
                        "#F7BE4D"
                    ]
                },
                "data": [
                    {
                        "x": "江西省",
                        "y": 1
                    },
                    {
                        "x": "西藏自治区",
                        "y": 1
                    },
                    {
                        "x": "北京",
                        "y": 1
                    },
                    {
                        "x": "山西省",
                        "y": 1
                    }
                ]
            },
            "approve_action": False,
            "reject_action": False
        }.__str__()
        update_card_data.card_param_map = {"title": "朱小志提交的财务报销", "detailUrl": "https://dingtalk.com",
                                           "status": "pending", "sys_full_json_obj": object_string}
        update_card_data.card_media_id_param_map = {}

        # -------------------------------------------------------------------------------------------------------------
        logger.info("卡片更新")
        # update_card_request = dingtalkcard__1__0_models.UpdateCardRequest()
        # update_card_request.out_track_id = out_track_id
        # update_card_request.card_data = update_card_data
        #
        # ## Private data
        # ccc = dingtalkim__1__0_models.PrivateDataValue()
        #
        # update_card_request.private_data = {'052605600220581061': ccc}
        #
        # update_card_header = dingtalkcard__1__0_models.UpdateCardHeaders()
        # update_card_header.x_acs_dingtalk_access_token = token
        # resp: dingtalkcard__1__0_models.UpdateCardResponse = card_client.update_card_with_options(
        #     update_card_request,
        #     update_card_header,
        #     util_models.RuntimeOptions()
        # )

        # card_data = dingtalkim__1__0_models.UpdateInteractiveCardRequestCardData(
        #     card_param_map={"title": "朱小志提交的财务报销", "detailUrl": "https://dingtalk.com",
        #                                    "status": "pending", "sys_full_json_obj": object_string},
        #     card_media_id_param_map={}
        # )
        card_data = dingtalkim__1__0_models.UpdateInteractiveCardRequestCardData(
            card_param_map={"key": "测试"},
            card_media_id_param_map={"key": "测试"}
        )

        update_interactive_card_request = dingtalkim__1__0_models.UpdateInteractiveCardRequest()
        #update_interactive_card_request.card_template_id = card_template_id
        # send_interactive_card_request.card_template_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema"
        # send_interactive_card_request.out_track_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema.1715069378009"
        # update_interactive_card_request.out_track_id = out_track_id + ".update"
        #update_interactive_card_request.robot_code = "dingqkoo0gpksjflc7ih"
        #update_interactive_card_request.open_conversation_id = "cidUQXUpOwFEbiRNp87JyFE3w=="
        #update_interactive_card_request.conversation_type = 1
        update_interactive_card_request.card_data = card_data
        update_interactive_card_request.out_track_id = out_track_id
        print(update_interactive_card_request.out_track_id)
        # card_options = dingtalkim__1__0_models.UpdateInteractiveCardRequestCardOptions(
        #     update_card_data_by_key=False,
        #     update_private_data_by_key=False
        # )
        # update_interactive_card_request.card_options = card_options
        # update_interactive_card_request.user_id_type = 1
        update_interactive_card_request.private_data = {"privateDataValueKey": card_data}

        update_interactive_card_headers = dingtalkim__1__0_models.UpdateInteractiveCardHeaders()
        update_interactive_card_headers.x_acs_dingtalk_access_token = token

        logger.info("卡片更新投递到聊天")
        update_resp: dingtalkim__1__0_models.UpdateInteractiveCardResponse = im_client.update_interactive_card_with_options(
            update_interactive_card_request,
            update_interactive_card_headers,
            util_models.RuntimeOptions()
        )
    except Exception as err:
        print(f"ERROR: ... {err.args}")
        pass

    # return HttpResponse(dd.getAccessToken())

    return HttpResponse(update_resp.body)


@csrf_exempt
def interactive_card_test(request):
    logger = logging.getLogger("dingtalk_bot")
    logger.debug("appKey:" + settings.DINGTALK_CLIENT_ID + " appSecret:" + settings.DINGTALK_CLIENT_SECRET)
    dd = DingtalkBase(settings.DINGTALK_CLIENT_ID, settings.DINGTALK_CLIENT_SECRET)
    token = dd.access_token

    task_name = request.POST.get("task_name", "undefined")

    a = Card(access_token=token,
             card_template_id=request.POST.get("card_template_id", "d42325af-b4e9-4857-b4be-3b917e0a9388.schema"),
             robot_code=settings.DINGTALK_ROBOT_CODE,
             #open_conversation_id="cidUQXUpOwFEbiRNp87JyFE3w==",
             open_conversation_id=request.POST.get("open_conversation_id", "cidXyTRHG7fjdQSMOK7O5RE0w=="),
             task_name=task_name,
             )

    if "markdown_content" in request.POST.keys():
        markdown_content = request.POST.get("markdown_content")
        ## 格式化 markdown 消息格式
        logger.debug(f"origin markdown_content: {markdown_content.encode('unicode_escape')}")
        regex = re.compile('\\n')
        markdown_content = regex.sub("<br>\\n", markdown_content)
        regex = re.compile('\\n\\s{6}')
        markdown_content = regex.sub("\\n> ", markdown_content)
    else:
        markdown_content = "#### Test tiltle\n* 123\n* 456"

    default_chart_data = {
        "type": "pieChart",
        "config": {
            "pieChartStyle": "percentage",
            "xAxisConfig": {},
            "padding": [
                0,
                5,
                0,
                0
            ],
            "yAxisConfig": {},
            "color": [
                "#329FFE",
                "#1AC681",
                "#FD9E5E",
                "#C766EC",
                "#98D333",
                "#5A88FE",
                "#FE7A66",
                "#ED63AD",
                "#A564ED",
                "#F7BE4D"
            ]
        },
        "data": [
            {
                "x": "江西省",
                "y": 1
            },
            {
                "x": "西藏自治区",
                "y": 1
            },
            {
                "x": "北京",
                "y": 1
            },
            {
                "x": "山西省",
                "y": 1
            }
        ]
    }

    # 获取 workflows task 任务状态
    task_info = get_task_job_from_workflows_api(token=settings.ARGO_WORKFLOWS_TOKEN,
                                                api_domain=settings.ARGO_WORKFLOWS_DOMAIN,
                                                namespace=settings.ARGO_WORKFLOWS_WORKER_NAMESPACE,
                                                task_name=request.POST.get("task_name", "Unknown_task_name")
                                                )
    # 根据 task_info 来更新 card chart data 数据字段
    default_chart_data["data"] = gen_chart_data(task_info)

    # 增加定时调度任务
    # add_schedule_job(request.POST.get("task_name", "none"))

    card_vars = {
        "markdown_content": markdown_content,
        "approve": 0,
        "reject": 0,
        "card_title": request.POST.get("card_title", "本次发布更新"),
        "markdown_title": "<font sizeToken=common_footnote_text_style__font_size "
                          "colorTokenV2=common_level3_base_color>*" + request.POST.get("markdown_title",
                                                                                       "本次发布 CHANGELOG 汇总") +
                          "*</font>",
        "approve_max": 10,
        "reject_max": 2,
        "card_ref_link": request.POST.get("card_ref_link",
                                          "https://workflows.poc.jagat.io/workflows/workflows?&limit=50"),
        "repository": request.POST.get("repository", "undefined"),
        "project_id": request.POST.get("project_id", "100000"),
        "author": request.POST.get("author", "Unknown"),
        "branch": request.POST.get("branch", "Unknown"),
        "commit_sha": request.POST.get("commit_sha", "e8c15b9aa5debe96dd9f6441ba682f4edd064b30"),
        "environment": request.POST.get("environment", "undefined"),
        "chart_data": json.loads(request.POST.get("chart_data", json.dumps(default_chart_data))),
        "approve_action": False,
        "reject_action": False,
        "cicd_status": request.POST.get("cicd_status", "正在更新中..."),  # 三个值，failure / success / 更新中...
        "config": {"autoLayout": "True" == request.POST.get("config.autoLayout")},  # 是否宽屏显示
        "cicd_elapse": request.POST.get("cicd_elapse", "_")  # 最新的耗时时长
    }
    b = CardData(card_vars)
    a.create_and_update_card_data(b)
    a.send_interactive_card()

    time.sleep(5)
    a2 = Card(access_token=token, task_name=task_name)
    card_vars["markdown_content"] = card_vars["markdown_content"] + "."
    b2 = CardData(card_vars)
    # b2 = dingtalkim__1__0_models.UpdateInteractiveCardRequestCardData(
    #     card_param_map=card_vars,
    #     card_media_id_param_map=card_vars
    # )
    # logger.info(f"Card param map: {b.get_card_content()}")
    a2.create_and_update_card_data(b2)
    # a.__persistent_card()
    a2.private_data = {"privateDataValueKey": b2}
    # a2.open_conversation_id = None
    # a2.card_template_id = None
    # a2.open_space_id = None
    # a2.robot_code = None
    a2.user_id_type = None

    logger.info(f"开始更新卡片")
    a2.out_track_id = a.out_track_id
    a2.update_interactive_card()
    return HttpResponse("OK")


@csrf_exempt
def update_card(request):
    logger = logging.getLogger("dingtalk_bot")
    logger.debug("appKey:" + settings.DINGTALK_CLIENT_ID + " appSecret:" + settings.DINGTALK_CLIENT_SECRET)
    base = DingtalkBase(settings.DINGTALK_CLIENT_ID, settings.DINGTALK_CLIENT_SECRET)
    token = base.get_access_token()
    logger.info("token: " + token)
    abc = CardDataStore()
    abc.set_access_token(request.GET.get("task_name"), token)
    return HttpResponse("Done")


@csrf_exempt
def interactive_card_test2(request):
    logger = logging.getLogger("dingtalk_bot")
    logger.debug(
        f"appKey: {os.environ.get('DINGTALK_CLIENT_ID')} appSecret: {os.environ.get('DINGTALK_CLIENT_SECRET')}")
    dd = DingtalkBase(os.environ.get("DINGTALK_CLIENT_ID"), os.environ.get("DINGTALK_CLIENT_SECRET"), "dingtalk_bot")
    token = dd.get_access_token()
    logger.info("token: " + token)

    updateCard = Card(access_token=token,
                      card_template_id="98a61096-31e1-4611-be4e-b1d2f6897225.schema",
                      robot_code="dingqkoo0gpksjflc7ih",
                      open_conversation_id="cidUQXUpOwFEbiRNp87JyFE3w==",
                      )

    card_vars = {
        "markdown_content": "#### Tiltle\n* 123\n* 456",
        "approve": 7,
        "reject": 3,
        "card_title": "本次发布更新",
        "markdown_title": "本周发布commit汇总",
        "markdown": "4567121231231",
        "approve_max": 10,
        "reject_max": 5,
    }
    b = CardData(card_vars)
    updateCard.create_and_update_card_data(b)
    updateCard.send_interactive_card()

    time.sleep(3)
    card_vars["markdown_content"] = card_vars["markdown_content"] + "7890"
    b = CardData(card_vars)
    # logger.info(f"Card param map: {b.get_card_content()}")
    updateCard.create_and_update_card_data(b)
    # a.__persistent_card()

    logger.info(f"开始更新卡片")
    updateCard.update_interactive_card()
    return HttpResponse("OK")


@csrf_exempt
def task_test(request):
    logger = logging.getLogger("dingtalk_bot")
    logger.info("add schedule job")
    # schedule("my_task", schedule_type=Schedule.ONCE, next_run=timezone.now() + timedelta(minutes=1))
    # task_test_job(repeat=10)
    #task_id = async_task("customRobot.views.my_task", hook="customRobot.views.print_result")
    # task_id = schedule("customRobot.views.my_task", args=("abcd",), schedule_type=Schedule.MINUTES, minutes=0.5,
    #                    repeats=-1)
    #task_result = result(task_id)
    #return HttpResponse(f"OK111 {task_id} result: {task_result}")
    return HttpResponse(f"OK111")


def stop_task(request):
    logger = logging.getLogger("dingtalk_bot")
    logger.info("stop schedule job")
    # recent_tasks = Task.objects.all()
    # filter_schedule = Schedule.objects.filter(args="('abc1',)")
    # print(filter_schedule)
    #
    # scheduled_tasks = Schedule.objects.all()
    # for task in scheduled_tasks:
    #     print(f"Task Name: {task.name}, Func: {task.func}, Cron: {task.task}, IsSuccess: {task.success()} was deleted.")
    #     # task.delete()
    return HttpResponse("OK")


def my_task(args):
    # 任务逻辑
    logger = logging.getLogger("dingtalk_bot")
    logger.info(f"task {args} running ...")
    print(f"定时任务执行了！！ {args} {datetime.datetime.now()}")
    logger.info("task completed.")
    return 2


# @background(schedule=10, remove_existing_tasks=True)
# def task_test_job():
#     logger = logging.getLogger("dingtalk_bot")
#     logger.info("task running ...")
#     print(datetime.datetime.now())
#     logger.info("task completed.")


def print_result(task):
    print(task.result)


def workflow_test(request):
    workflow_instance = ArgoWorkflowsService()
    b = workflow_instance.get_result(
        namespace=request.GET.get("namespace", "workflows"),
        name=request.GET.get("name")
    )

    # TODO: 测试异步任务执行
    test.delay()  # 测试触发异步任务
    return JsonResponse(b)

@csrf_exempt
def new_notification(request):
    notice = DingTalkClient(
        task_name=request.POST.get("task_name"),
        space_type=SpaceTypeEnum.IM_GROUP
    )
    notice.parse_api_data(request=request)
    # ret = notice.build_card_data(schema)
    # notice.card_param_map = ret
    # print(ret)
    notice.send()
    return HttpResponse("OK")