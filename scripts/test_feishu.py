import argparse
from trendradar.core.loader import load_config
from trendradar.context import AppContext
from trendradar.notification.senders import send_to_feishu


def main():
    parser = argparse.ArgumentParser(prog="test_feishu", description="TrendRadar 飞书发送测试")
    parser.add_argument("--type", choices=["text", "interactive"], default="interactive")
    parser.add_argument("--webhook", default="")
    parser.add_argument("--batch-size", type=int, default=0)
    parser.add_argument("--interval", type=float, default=0.0)
    parser.add_argument("--report-type", default="当日汇总")
    parser.add_argument("--mode", default="daily")
    args = parser.parse_args()

    cfg = load_config()
    if args.webhook:
        cfg["FEISHU_WEBHOOK_URL"] = args.webhook
    if not cfg.get("FEISHU_WEBHOOK_URL"):
        print("缺少 FEISHU_WEBHOOK_URL")
        return

    cfg["FEISHU_MESSAGE_TYPE"] = args.type
    if args.batch_size > 0:
        cfg["FEISHU_INTERACTIVE_BATCH_SIZE"] = args.batch_size
    if args.interval > 0.0:
        cfg["BATCH_SEND_INTERVAL"] = args.interval

    ctx = AppContext(cfg)

    report_data = {
        "stats": [
            {
                "word": "测试关键词",
                "count": 2,
                "titles": [
                    {
                        "title": "**粗体示例** 与 [链接](https://example.com)",
                        "url": "https://example.com",
                        "rank": 3,
                        "time": "10:05",
                    },
                    {
                        "title": "次条目 --- 分割线后",
                        "url": "https://example.com/2",
                        "rank": 5,
                        "time": "10:15",
                    },
                ],
            }
        ],
        "failed_ids": [],
        "new_titles": [],
        "id_to_name": {},
    }

    batch_size = (
        cfg.get("FEISHU_INTERACTIVE_BATCH_SIZE", cfg.get("FEISHU_BATCH_SIZE", 29000))
        if args.type == "interactive"
        else cfg.get("FEISHU_BATCH_SIZE", 29000)
    )

    ok = send_to_feishu(
        webhook_url=cfg["FEISHU_WEBHOOK_URL"],
        report_data=report_data,
        report_type=args.report_type,
        update_info={"version": "test"},
        proxy_url=None,
        mode=args.mode,
        account_label="",
        batch_size=batch_size,
        batch_interval=cfg.get("BATCH_SEND_INTERVAL", 1.0),
        message_type=cfg.get("FEISHU_MESSAGE_TYPE", "text"),
        split_content_func=ctx.split_content,
        get_time_func=ctx.get_time,
        rss_items=None,
        rss_new_items=None,
        ai_analysis=None,
        display_regions=cfg.get("DISPLAY", {}).get("REGIONS", {}),
        standalone_data=None,
    )
    print("发送结果:", ok)


if __name__ == "__main__":
    main()
